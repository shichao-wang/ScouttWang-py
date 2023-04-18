from dataclasses import Field
from typing import ClassVar, Dict, Protocol, TypeVar


class Dataclass(Protocol):  # pylint: disable=too-few-public-methods
    __dataclass_fields__: ClassVar[Dict[str, Field]]


DataclassT = TypeVar("DataclassT", bound=Dataclass)
