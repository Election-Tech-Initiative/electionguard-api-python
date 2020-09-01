# FIXME Serialization should exist in electionguard-python repository

from electionguard.serializable import set_serializers, FROM_JSON_FILE
from typing import Any, cast
from jsons import (
    dump,
    dumps,
    suppress_warnings,
)


def write_json(object_to_write: Any) -> Any:
    set_serializers()
    suppress_warnings()
    return cast(
        str, dumps(object_to_write, strip_privates=True, strip_nulls=True)
    ).replace(FROM_JSON_FILE, "")


def write_json_object(object_to_write: Any) -> Any:
    json = dump(object_to_write, strip_privates=True, strip_nulls=True)
    scrub(json, "from_json_file")
    return json


def scrub(obj: object, key_to_remove: str) -> Any:
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            if key == key_to_remove:
                del obj[key]
            else:
                scrub(obj[key], key_to_remove)
    elif isinstance(obj, list):
        for i in reversed(range(len(obj))):
            if obj[i] == key_to_remove:
                del obj[i]
            else:
                scrub(obj[i], key_to_remove)
