from pydantic import BaseModel, Field

"""
Координаты географических точек.

Координаты географических точек задаются в виде широты (latitude) и долготы (longitude).
Единицы измерения географических координат - градусы с долями, с точностью до 1".
Тип данных – LONGREAL (число с плавающей запятой длиной 8 байт).
    Пример: 25° 10´ 11" = 25.16972°
Диапазон изменения географической широты:
    от минус 90° до плюс 90° (северная широта имеет знак «+», южная широта – знак «-»).
Диапазон изменения географической долготы:
    от минус 180° до плюс 180° (восточная долгота имеет знак «+», западная долгота – знак «-»).

Пример JSON- представления информации о географической точке:
    {"lat": 37.4224764, "lng": -122.0842499}
"""


class LocationPoint(BaseModel):
    x: float = Field(None, alias="lng")
    y: float = Field(None, alias="lat")

    # FIXME: Уточнить сравнение координат float (м.б. заменить на decimal)
    def __eq__(self, other):
        return other and self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    class Config:
        allow_population_by_field_name = True
