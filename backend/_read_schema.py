import json

keys: set[str] = set()


def attrgetter(container: list | dict, parent: str = '') -> None:
    """Get attributes recursively."""
    if isinstance(container, dict):
        for key, val in container.items():
            name = parent
            if name:
                name += "."
            name += key
            if isinstance(val, (dict, list)):
                attrgetter(val, name)
            else:
                keys.add(name)
    elif isinstance(container, list):
        for key, val in enumerate(container):
            name = parent
            if name:
                name += "."
            name += str(key)
            if isinstance(val, (dict, list)):
                attrgetter(val, name)
            else:
                keys.add(name)


with open("laptops_raw.json", 'r') as f:
    data = json.load(f)
    for laptop in data:
        attrgetter(laptop)
    with open("laptops_schema.json", "w+") as f:
        json.dump(sorted(list(keys)), f)
keys = set()
with open("phones_raw.json", 'r') as f:
    data = json.load(f)
    for phone in data:
        attrgetter(phone)
    with open("phones_schema.json", "w+") as f:
        json.dump(sorted(list(keys)), f)
