import dataclasses
import json
import logging
import os
import typing
from argparse import ONE_OR_MORE, ArgumentParser
from argparse import _ActionsContainer as ActionsContainer
from typing import Any, Dict, Generic, List, Mapping, Optional, Protocol, Sequence, Type, TypeVar, Union

import toml
import yaml

from scouttwang.dataclass_utils.ops import dataclass_from_flatdict, field_default
from scouttwang.dataclass_utils.typing import DataclassT
from scouttwang.flatdict import flatten_dict

log = logging.getLogger(__name__)


no_default = object()


def parser_add_argument(parser: ActionsContainer, dest: str, atype: Type, default: Any = no_default) -> None:
    origin_type = typing.get_origin(atype)
    type_args = typing.get_args(atype)

    if dataclasses.is_dataclass(atype):
        parser_add_dataclass_arguments(parser, atype, prefix=dest + ".")
        return
    if atype is bool:
        parser_add_bool_argument(parser, dest, default)
        return
    if origin_type is tuple and type_args[1] is Ellipsis:
        parser_add_tuple_argument(parser, dest, type_args[0], default)
        return

    kwargs = {"action": "store", "dest": dest, "type": atype}
    if default is not no_default:
        kwargs["default"] = default

    parser.add_argument(f"--{dest}", **kwargs)  # type: ignore
    return


def parser_add_dataclass_arguments(parser: ActionsContainer, dataclass: Type[DataclassT], prefix: str = ""):
    # parser.add_argument()
    for field in dataclasses.fields(dataclass):
        dest = prefix + field.name
        if dataclasses.is_dataclass(field.type):  # nested dataclass
            parser_add_dataclass_arguments(parser.add_argument_group(field.name), field.type, prefix=f"{dest}.")
            continue
        parser_add_argument(parser, dest, field.type, field_default(field, default=no_default))


def parser_add_tuple_argument(
    parser: ActionsContainer, dest: str, vtype: Type, default: Union[List, object] = no_default
) -> None:
    kwargs = {"action": "extend", "nargs": ONE_OR_MORE, "type": vtype, "dest": dest}
    if default is not no_default:
        kwargs["default"] = default
    parser.add_argument(f"--{dest}", **kwargs)  # type: ignore


def parser_add_bool_argument(parser: ActionsContainer, dest: str, default: Union[bool, object] = no_default) -> None:
    exclusive_group = parser.add_mutually_exclusive_group(required=default is no_default)
    exclusive_group.add_argument(f"--{dest}", action="store_true", dest=dest)
    reverse_argflag = "--not_" + dest
    exclusive_group.add_argument(reverse_argflag, action="store_false", dest=dest)


class SupportsRead(Protocol):
    def read(self, size: int = ...) -> str:
        pass


T = TypeVar("T")


class ConfigLoader:
    def load(self, path: str) -> Mapping[str, Any]:
        _, ext = os.path.splitext(path)
        with open(path, encoding="utf-8") as stream:
            if ext in (".json",):
                return self.load_json(stream)
            if ext in (".yaml", ".yml"):
                return self.load_yaml(stream)
            if ext in (".toml",):
                return self.load_toml(stream)
            raise ValueError("")

    def load_json(self, stream: SupportsRead):
        return json.load(stream)

    def load_yaml(self, stream: SupportsRead):
        return yaml.safe_load(stream)

    def load_toml(self, stream: SupportsRead):
        obj = toml.load(stream)
        log.info(obj)
        return obj


class DataclassParser(Generic[DataclassT]):
    def __init__(self, dataclass: Type[DataclassT]) -> None:
        self.dataclass = dataclass

    def parse_args(self, args: Optional[Sequence[str]] = None) -> DataclassT:
        confparser = ArgumentParser()
        confparser.add_argument("-c", "--conf", nargs=ONE_OR_MORE, required=False)
        ns, args = confparser.parse_known_args(args)

        loader = ConfigLoader()
        flat_conf_kwargs: Dict[str, Any] = {}
        for conf in ns.conf:
            kwargs = loader.load(conf)
            flat_conf_kwargs.update(flatten_dict(kwargs))

        parser = ArgumentParser()
        parser.set_defaults(**flat_conf_kwargs)
        parser_add_dataclass_arguments(parser, self.dataclass)
        ns = parser.parse_args(args)
        flat_conf_kwargs.update(vars(ns))
        log.debug("flat kwargs: %s", flat_conf_kwargs)
        return dataclass_from_flatdict(flat_conf_kwargs, self.dataclass)


def parse_dataclass(dataclass: Type[DataclassT]) -> DataclassT:
    return DataclassParser(dataclass).parse_args()
