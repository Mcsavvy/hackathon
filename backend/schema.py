"""
Read Data Scheme.

This file reads the schema from the data itself it
a way that makes classification more target and the structure
of the data more transparent.
"""
import json
from typing import TypedDict as tdict, Union, Optional


NodeType = Union[int, str, float, list, dict, bool]

def walk_json_tree(
    value: NodeType,
    key: Optional[str] = None,
    parent: Optional[dict] = None,
    get_values: bool = False,
    get_types: bool = False,
    count: bool = False,
) -> dict:
    """
    Walk a tree of json objects.

    Returns:
        ...
    """
    _type = type(value).__name__
    is_root = parent is None
    if is_root:
        obj = dict()  # type: ignore
    else:
        obj = parent.setdefault(key, dict())  # type: ignore
        if count:
            obj["count"] = obj.get("count", 0) + 1

    if _type == 'list':
        for idx, item in enumerate(value):  # type: ignore
            walk_json_tree(item, "[]", obj, get_values=get_values,
                           get_types=get_types, count=count)
    elif _type == 'dict':
        for key, val in value.items():  # type: ignore
            walk_json_tree(val, key, obj, get_values=get_values,
                           get_types=get_types, count=count)
    else:
        if get_types:
            obj_types = obj.setdefault("types", [])
            if _type not in obj_types:
                obj_types.append(_type)
        if get_values:
            obj_values = obj.setdefault("values", list())
            if value not in obj_values:
                obj_values.append(value)
    return obj


with open("laptops_raw.json", 'r') as f:
    data = json.load(f)
    tree = walk_json_tree(data)
    with open("laptops_schema_real.json", "w+") as f:
        json.dump(tree, f, indent=2)

with open("phones_raw.json", 'r') as f:
    data = json.load(f)
    with open("phones_schema_real.json", "w+") as f:
        json.dump(walk_json_tree(data), f, indent=2)
