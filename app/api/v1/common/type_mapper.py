from typing import Union
from electionguard.group import (
    ElementModP,
    ElementModQ,
    hex_to_p,
    hex_to_q,
    int_to_p,
    int_to_q,
)


class TypeMapper:
    @staticmethod
    def string_to_elementModP(value: Union[int, str]) -> ElementModP:
        if isinstance(value, str):
            elementmodp = hex_to_p(value)
        else:
            elementmodp = int_to_p(value)
        if elementmodp is None:
            raise ValueError("invalid key: " + value)
        return elementmodp

    @staticmethod
    def string_to_elementModQ(value: Union[int, str]) -> ElementModQ:
        if isinstance(value, str):
            elementmodq = hex_to_q(value)
        else:
            elementmodq = int_to_q(value)
        if elementmodq is None:
            raise ValueError("invalid key: " + value)
        return elementmodq
