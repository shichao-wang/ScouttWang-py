import dataclasses
from dataclasses import MISSING, Field
from typing import Any, Dict, Mapping, Type

from .typing import DataclassT


def dataclass_defaults(dataclass: Type[DataclassT]) -> Dict[str, Any]:
    defaults = {}
    for field in dataclasses.fields(dataclass):
        if dataclasses.is_dataclass(field.type):
            continue
        default = field_default(field)
        if default is None:
            continue
        defaults[field.name] = default
    return defaults


def field_default(field: Field, *, default: Any = None) -> Any:
    if field.default is not MISSING:
        return field.default
    if field.default_factory is not MISSING:
        return field.default_factory()
    return default


_marker = object()


def dataclass_from_flatdict(flatdict: Mapping[str, str], dataclass: Type[DataclassT]) -> DataclassT:
    kwargs = dataclass_defaults(dataclass)

    for field in dataclasses.fields(dataclass):
        if dataclasses.is_dataclass(field.type):
            prefix = f"{field.name}."
            plen = len(prefix)
            subdict = {k[plen:]: v for k, v in flatdict.items() if k.startswith(field.name)}
            kwargs[field.name] = dataclass_from_flatdict(subdict, field.type)
        else:
            value = flatdict.get(field.name, _marker)
            if value is not _marker:
                kwargs[field.name] = value

    return dataclass(**kwargs)


def dataclass_from_dict(kwargs: Mapping[str, Any], dataclass: Type[DataclassT]) -> DataclassT:
    init_kwargs = dataclass_defaults(dataclass)

    for field in dataclasses.fields(dataclass):
        if dataclasses.is_dataclass(field.type):
            init_kwargs[field.name] = dataclass_from_dict(kwargs[field.name], field.type)
        else:
            value = kwargs.get(field.name, _marker)
            if value is not _marker:
                init_kwargs[field.name] = value

    return dataclass(**init_kwargs)
