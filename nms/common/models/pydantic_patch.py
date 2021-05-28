from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny

from pydantic import BaseModel

"""
Workaround for serializing properties with pydantic until
https://github.com/samuelcolvin/pydantic/issues/935
is solved
"""


class PropertyBaseModel(BaseModel):
    @classmethod
    def get_properties(cls):
        return [
            prop
            for prop in dir(cls)
            if isinstance(getattr(cls, prop), property)
            and prop not in ("__values__", "fields")
        ]

    def dict(self, *args, **kwargs) -> "DictStrAny":
        self.__dict__.update(
            {prop: getattr(self, prop) for prop in self.get_properties()}
        )

        return super().dict(*args, **kwargs)
