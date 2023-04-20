import dataclasses
import json
import logging
import os
import typing
from argparse import ONE_OR_MORE, ArgumentParser
from typing import Any, Dict, Generic, Mapping, Optional, Protocol, Sequence, Type, TypeVar, Union

import toml
import yaml

from scouttwang.dataclass_utils.ops import dataclass_from_flatdict
from scouttwang.dataclass_utils.typing import DataclassT
from scouttwang.flatdict import flatten_dict

log = logging.getLogger(__name__)


def parser_add_dataclass_arguments(parser: ArgumentParser, dataclass: Type[DataclassT], prefix: str = ""):
    for field in dataclasses.fields(dataclass):
        dest = prefix + field.name
        argflag = "--" + dest
        required = parser.get_default(dest) is None

        if dataclasses.is_dataclass(field.type):
            parser_add_dataclass_arguments(parser, field.type, prefix=f"{dest}.")
        elif field.type is bool:
            exclusive_group = parser.add_mutually_exclusive_group(required=required)
            exclusive_group.add_argument(argflag, action="store_true", dest=dest)
            reverse_argflag = "--not_" + dest
            exclusive_group.add_argument(reverse_argflag, action="store_false", dest=dest)
        elif field.type in (int, float, str):
            parser.add_argument(argflag, type=field.type, required=required, dest=dest)
        elif typing.get_origin(field.type) is tuple and typing.get_args(field.type)[1] is Ellipsis:
            value_type = typing.get_args(field.type)[0]
            parser.add_argument(
                argflag, action="extend", nargs=ONE_OR_MORE, type=value_type, required=required, dest=dest
            )
        else:
            log.warning("Unsupported field: %s(%s)", dest, field.type)


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
        return dataclass_from_flatdict(flat_conf_kwargs, self.dataclass)


def parse_dataclass(dataclass: Type[DataclassT]) -> DataclassT:
    return DataclassParser(dataclass).parse_args()
