import dataclasses
import json
from typing import Protocol, Type

from typing_extensions import Self

from scouttwang.dataclass_utils import dataclass_from_dict


class SerdeJson(Protocol):
    def to_json(self) -> str:
        if dataclasses.is_dataclass(self):
            return json.dumps(dataclasses.asdict(self))
        raise NotImplementedError()

    @classmethod
    def from_json(cls: Type[Self], s: str) -> Self:  # type: ignore
        kwargs = json.loads(s)
        if dataclasses.is_dataclass(cls):
            return dataclass_from_dict(kwargs, cls)
        raise NotImplementedError()
