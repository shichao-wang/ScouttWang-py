from typing import Any, Dict, Mapping, Sequence


def flatdict_to_hierarchical(flatdict: Mapping[str, Any]) -> Dict[str, Any]:
    def _inner_setitem(keys: Sequence[str], value: Any) -> None:
        entry = kwargs
        for key in keys[:-1]:
            if key not in entry:
                entry[key] = {}
            entry = entry[key]
        entry[keys[-1]] = value

    kwargs: Dict[str, Any] = {}
    for key, value in flatdict.items():
        _inner_setitem(key.split("."), value)
    return kwargs


def flatten_dict(kwargs: Mapping[str, Any]) -> Dict[str, Any]:
    def _inner_flatten(_kwargs: Mapping[str, Any], prefix: str = ""):
        flatdict: Dict[str, Any] = {}
        for key, value in _kwargs.items():
            if isinstance(value, Mapping):
                flatdict.update(_inner_flatten(value, f"{prefix+key}."))
            else:
                flatdict[prefix + key] = value
        return flatdict

    return _inner_flatten(kwargs)


__all__ = ["flatdict_to_hierarchical", "flatten_dict"]
