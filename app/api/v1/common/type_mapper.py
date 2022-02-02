from electionguard.group import ElementModP, ElementModQ, hex_to_p, hex_to_q


class TypeMapper:
    @staticmethod
    def string_to_elementModP(value: str) -> ElementModP:
        elementModP = hex_to_p(value)
        if elementModP is None:
            raise ValueError("invalid key: " + value)
        return elementModP

    @staticmethod
    def string_to_elementModQ(value: str) -> ElementModQ:
        elementModQ = hex_to_q(value)
        if elementModQ is None:
            raise ValueError("invalid key: " + value)
        return elementModQ
