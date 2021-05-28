"""
Работа с сигналами и спектрограммами
"""
from datetime import datetime
from math import ceil
from typing import List, Optional, Tuple
from uuid import UUID
from uuid import uuid4 as gen_uuid4

from scipy import interpolate

from .gis import LocationPoint
from .pydantic_patch import PropertyBaseModel


class RfBandwidth(PropertyBaseModel):
    guid: str
    start_freq_hz: int
    stop_freq_hz: int

    @property
    def bandwidth_hz(self) -> int:
        return self.stop_freq_hz - self.start_freq_hz

    def shift_start_freq_to(self, new_start_freq_hz: int) -> None:
        bw = self.bandwidth_hz
        self.start_freq_hz = new_start_freq_hz
        self.stop_freq_hz = self.start_freq_hz + bw


class RfSpectrumSignal(RfBandwidth):
    trace_guid: str
    f0_freq_hz: int

    def shift_start_freq_to(self, new_start_freq_hz: int) -> None:
        delta = self.start_freq_hz - new_start_freq_hz
        super().shift_start_freq_to(new_start_freq_hz)
        self.f0_freq_hz -= delta


def dbm_array_encoder(dbm_array: bytes) -> list:
    if isinstance(dbm_array, bytes):
        return [
            int.from_bytes(y, "little", signed=True) / 100
            for y in [
                dbm_array[offset : offset + 2] for offset in range(0, len(dbm_array), 2)
            ]
        ]


def dbm_array_decoder(dbm_array: list) -> bytes:
    if isinstance(dbm_array, list):
        """
        особенности округления в python:

        int.from_bytes(b'\x9c\xe2', 'little', signed=True)
        -7524

        int.to_bytes(-7524, 2, 'little', signed=True)
        b'\x9c\xe2'

        int.to_bytes(int(-75.24 * 100), 2, 'little', signed=True)
        b'\x9d\xe2' <- НЕ СОВПАДАЕТ!!!  т.к. -75.24 * 100 = -7523.999999999999
        """
        return b"".join(
            [int.to_bytes(round(y * 100), 2, "little", signed=True) for y in dbm_array]
        )


class RfSpectrumTrace(RfBandwidth):
    step_freq_hz: int
    noise: float
    numpoints: int
    y_val_dbm: bytes

    class Config:
        json_encoders = {bytes: dbm_array_encoder}

    def apply_gain(self, gain_value: float) -> None:
        """
        Применить коэффициент усиления ко всем точкам спектрограммы
        :param gain_value: коэффициент усиления
        """
        y_val_dbm_arr = dbm_array_encoder(self.y_val_dbm)
        self.y_val_dbm = dbm_array_decoder(
            list(map(lambda y: y + gain_value, y_val_dbm_arr))
        )
        self.noise += gain_value

    def blank(self) -> None:
        """
        Применить к спектрограмме режим Blanked: сигнал выключен на всей полосе
        """
        self.numpoints = 0
        self.y_val_dbm = b""
        self.noise = 0


class RfSpectrumTraceForLocation(RfSpectrumTrace):
    timestamp: datetime
    location: LocationPoint


class RfTraceSignals:
    def __init__(self, trace: RfSpectrumTrace, signals: List[RfSpectrumSignal]):
        self.trace = trace
        self.signals = signals

    @property
    def trace_guid(self) -> str:
        return self.trace.guid

    @property
    def signals_guid(self) -> Tuple[str, ...]:
        return tuple(signal.guid for signal in self.signals)

    def signal_by_guid(self, signal_guid: UUID) -> Optional[RfSpectrumSignal]:
        return next(
            (signal for signal in self.signals if signal.guid == signal_guid.hex), None
        )

    def __getitem__(self, signal_guid: UUID) -> Optional[RfSpectrumSignal]:
        return self.signal_by_guid(signal_guid)

    def get_max_dbm(self, signal_guid: UUID) -> float:
        """
        Максимальное значение мощности отдельного сигнала на полосе спектрограммы
        :param signal_guid: идентификатор сигнала
        :return: значение мощности сигнала, дБм
        """
        signal = self.signal_by_guid(signal_guid)
        if signal is None:
            raise ValueError("Unknown signal GUID")

        y_val_dbm = dbm_array_encoder(self.trace.y_val_dbm)

        # дополнительный контроль за фактическим кол-вом точек в спектрограмме
        x_val_hz = range(
            self.trace.start_freq_hz,
            self.trace.stop_freq_hz + 1,
            self.trace.step_freq_hz,
        )[: self.trace.numpoints]
        last_point_n = min(
            (n for n in enumerate(x_val_hz) if n[1] >= signal.stop_freq_hz),
            key=lambda x: x[0],
            default=(0, 0),
        )[0]
        return max(y_val_dbm[:last_point_n])


def cut_signal_from_trace(
    src_trace: RfSpectrumTrace, signal: RfSpectrumSignal, min_fq_bandwidth_hz: int = 0
) -> Optional[RfSpectrumTrace]:
    """
    Выделяет из спектрограммы отдельный сигнал в виде новой спектрограммы
    :param src_trace: исходная спектрограмма
    :param signal: сигнал
    :param min_fq_bandwidth_hz: минимальная полоса сигнала (дискретность обработки), если = 0 - игнорировать дискретность
    :return: спектрограмма или None (невозможно вырезать сигнал по заданным условиям)
    """

    def _calc_cut_range():
        if (
            len(x_val_hz) > 0
            and cut_start_freq_hz >= x_val_hz[0]
            and cut_stop_freq_hz <= x_val_hz[-1]
        ):
            _first = max(
                (n for n in enumerate(x_val_hz) if n[1] <= cut_start_freq_hz),
                key=lambda x: x[0],
                default=None,
            )
            _last = min(
                (n for n in enumerate(x_val_hz) if n[1] >= cut_stop_freq_hz),
                key=lambda x: x[0],
                default=None,
            )
            return _first, _last
        else:
            return None, None

    # начинаем вырезать всегда с частоты, заданной в сигнале
    cut_start_freq_hz = signal.start_freq_hz
    if min_fq_bandwidth_hz > 0:
        # полоса сигнала должна быть кратной дискрету
        _bandwidth = (
            ceil(signal.bandwidth_hz / min_fq_bandwidth_hz) * min_fq_bandwidth_hz
        )
        cut_stop_freq_hz = signal.start_freq_hz + _bandwidth
    else:
        cut_stop_freq_hz = signal.stop_freq_hz

    # дополнительный контроль за фактическим кол-вом точек в спектрограмме
    x_val_hz = range(
        src_trace.start_freq_hz, src_trace.stop_freq_hz + 1, src_trace.step_freq_hz
    )[: src_trace.numpoints]

    first, last = _calc_cut_range()
    if first is None or last is None:
        # невозможно вырезать сигнал по заданным условиям
        return None
    src_y_val_dbm = dbm_array_encoder(src_trace.y_val_dbm)

    y_base = src_y_val_dbm[first[0] : (last[0] + 1)]
    x_base = [x for x in range(first[1], last[1] + 1, src_trace.step_freq_hz)]
    f = interpolate.interp1d(x_base, y_base)
    y_val_dbm = [
        round(f(x).item(0), 2)
        for x in range(cut_start_freq_hz, cut_stop_freq_hz + 1, src_trace.step_freq_hz)
    ]
    y_val_dbm_packed = dbm_array_decoder(y_val_dbm)
    trace = RfSpectrumTrace(
        guid=gen_uuid4().hex,
        start_freq_hz=cut_start_freq_hz,
        step_freq_hz=src_trace.step_freq_hz,
        stop_freq_hz=cut_stop_freq_hz,
        noise=src_trace.noise,
        numpoints=len(y_val_dbm),
        y_val_dbm=y_val_dbm_packed,
    )
    return trace
