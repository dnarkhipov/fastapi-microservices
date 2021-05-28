from collections.abc import Sequence
from typing import Generic, TypeVar, Union

from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponsePage(GenericModel, Generic[T]):
    page: int = Field(description="номер страницы")
    limit: int = Field(description="максимальное количество записей на странице")
    total: int = Field(description="всего записей")
    params: dict[str, Union[int, str]] = Field(
        default=dict(),
        description="список параметров, принятых при формировании страницы",
    )
    content: Sequence[T]
