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
    def string_to_element_mod_p(value: str) -> ElementModP:
        elementmodp = hex_to_p(value)
        if elementmodp is None:
            raise ValueError("invalid key: " + value)
        return elementmodp

    @staticmethod
    def string_to_element_mod_q(value: str) -> ElementModQ:
        elementmodq = hex_to_q(value)
        if elementmodq is None:
            raise ValueError("invalid key: " + value)
        return elementmodq

    @staticmethod
    def int_to_element_mod_p(value: int) -> ElementModP:
        elementmodp = int_to_p(value)
        if elementmodp is None:
            raise ValueError("invalid key: " + value)
        return elementmodp

    @staticmethod
    def int_to_element_mod_q(value: int) -> ElementModQ:
        elementmodq = int_to_q(value)
        if elementmodq is None:
            raise ValueError("invalid key: " + value)
        return elementmodq
