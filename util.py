import json
from dataclasses import asdict, astuple, dataclass, fields
from typing import Any, List


# Dump list of dataclasses to full version and minimized version of JSON files
def dataclassToJson(objectClass: dataclass, objects: List[dataclass], filePrefix: str, sort = True) -> None:
    try:
        sort and objects.sort()
    except TypeError:  # '<' not supported between instances of 'objectClass' and 'objectClass'
        print(f'Warning: {objectClass.__name__} is not sorted.')

    json.dump(
        [asdict(o) for o in objects],
        open(f'{filePrefix}.json', 'w'),
        indent=4
    )

    json.dump(
        {
            'keys': [f.name for f in fields(objectClass)],
            'values': [astuple(o) for o in objects]
        },
        open(f'{filePrefix}.min.json', 'w'),
        separators=(',', ':')
    )


# Dump list of objects to full version and minimized version of JSON files
# Usually it's a list of strings
def listToJson(objects: List[Any], filePrefix: str) -> None:
    objects.sort()

    json.dump(
        objects,
        open(f'{filePrefix}.json', 'w'),
        indent=4
    )

    json.dump(
        objects,
        open(f'{filePrefix}.min.json', 'w'),
        separators=(',', ':')
    )
