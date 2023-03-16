"""
Read Data Scheme.

This file reads the schema from the data itself it
a way that makes classification more target and the structure
of the data more transparent.
"""
import json
from typing import TypedDict as tdict, Union, Optional
from .config import (
    LAPTOP_SCHEMA, LAPTOP_DB,
    PHONE_SCHEMA, PHONE_DB
)


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
    _type = {
        int: "integer", float: "decimal",
        dict: "object", list: "array",
        str: "string", bool: "boolean",
        type(None): "null"
    }[type(value)]
    is_root = parent is None
    if is_root:
        obj = dict()  # type: ignore
    else:
        obj = parent.setdefault(key, dict())  # type: ignore
        if count:
            obj["count"] = obj.get("count", 0) + 1

    if _type == 'array':
        for idx, item in enumerate(value):  # type: ignore
            walk_json_tree(
                item, "[]", obj,
                get_values=get_values,
                count=count)
    elif _type == 'object':
        for key, val in value.items():  # type: ignore
            walk_json_tree(
                val, key, obj,
                get_values=get_values,
                count=count)
    else:
        obj_types = obj.setdefault("type", "")
        if _type not in obj_types:
            if obj_types:
                obj_types += ", " + _type
            else:
                obj_types += _type
        obj["type"] = obj_types
        if get_values:
            if key not in ('url', 'price'):
                obj_values = obj.setdefault("values", list())
                if value not in obj_values:
                    obj_values.append(value)
    return obj


def create_scheme():
    """Create database schema."""
    import rich

    laptop_data = json.loads(LAPTOP_DB.read_text())
    phone_data = json.loads(PHONE_DB.read_text())
    laptop_schema = walk_json_tree(laptop_data, count=True)
    phone_schema = walk_json_tree(phone_data, count=True)
    LAPTOP_SCHEMA.write_text(json.dumps(laptop_schema, indent=1))
    PHONE_SCHEMA.write_text(json.dumps(phone_schema, indent=1))

if __name__ == "__main__":
    import rich

    data = json.loads(LAPTOP_DB.read_text())
    prices = [laptop["prices"] for laptop in data]
    schema = walk_json_tree(prices, count=True, get_values=True)
    rich.print(schema)

    create_scheme()
