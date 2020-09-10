# FIXME Build a generic function in electionguard-python
from electionguard.serializable import set_deserializers, load
from typing import cast, Any, Type, TypeVar

T = TypeVar("T")


def read_json_object(data: Any, class_out: Type[T]) -> T:
    set_deserializers()
    return cast(T, load(data, class_out))
