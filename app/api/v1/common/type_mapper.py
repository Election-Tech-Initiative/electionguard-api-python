from typing import Optional, Union
from electionguard.group import (
    ElementModP,
    ElementModQ,
    hex_to_p,
    hex_to_q,
    int_to_p,
    int_to_q,
)


def string_to_element_mod_p(value: Union[int, str]) -> ElementModP:
    element = int_to_p(value) if isinstance(value, int) else hex_to_p(value)
    if element is None:
        raise ValueError(type_error_message(str(value), "element_mod_p"))
    return element


def string_to_element_mod_q(value: Union[int, str]) -> ElementModQ:
    element = int_to_q(value) if isinstance(value, int) else hex_to_q(value)
    if element is None:
        raise ValueError(type_error_message(str(value), "element_mod_q"))
    return element


def string_to_nullable_element_mod_q(value: Union[int, Optional[str]]) -> ElementModQ:
    if value is None:
        return None
    return string_to_element_mod_q(value)


def type_error_message(value: str, type: str) -> str:
    return f"{value} cannot be converted to {type}."
