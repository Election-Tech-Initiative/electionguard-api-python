# FIXME Build a generic function in electionguard-python
from electionguard.serializable import set_deserializers, load, cast, T
from typing import Any

def read_json_object(data: Any, generic_type: T) -> T:
    set_deserializers()
    return cast(T, load(data, generic_type))