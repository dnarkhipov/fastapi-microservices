from datetime import datetime
from typing import List

from pydantic import BaseModel

from nms.common.models.gis import LocationPoint
from nms.common.models.rfspectrumtrace import (RfSpectrumTraceForLocation,
                                               dbm_array_decoder)


class RfSpectrumTraceInRequest(BaseModel):
    guid: str
    start_freq_hz: int
    stop_freq_hz: int
    step_freq_hz: int
    noise: float
    numpoints: int
    y_val_dbm: List[float]
    timestamp: datetime
    location: LocationPoint

    def as_packed_trace(self) -> RfSpectrumTraceForLocation:
        result = self.dict(exclude={'y_val_dbm'})
        result['y_val_dbm'] = dbm_array_decoder(self.y_val_dbm)
        return RfSpectrumTraceForLocation(**result)
