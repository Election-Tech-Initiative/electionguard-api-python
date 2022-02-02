from typing import Any, List, Optional
from enum import Enum
from electionguard.election import CiphertextElectionContext
from electionguard.group import ElementModP, ElementModQ, hex_to_p, hex_to_q
from fastapi import (
    HTTPException,
    status,
)
from .base import Base, BaseRequest, BaseResponse
from .manifest import ElectionManifest


__all__ = [
    "Election",
    "ElectionState",
    "ElectionQueryRequest",
    "ElectionQueryResponse",
    "MakeElectionContextRequest",
    "MakeElectionContextResponse",
    "SubmitElectionRequest",
]


class CiphertextElectionContextDto(Base):
    """The meta-data required for an election including keys, manifest, number of guardians, and quorum"""

    number_of_guardians: int
    """
    The number of guardians necessary to generate the public key
    """
    quorum: int
    """
    The quorum of guardians necessary to decrypt an election.  Must be less than `number_of_guardians`
    """

    elgamal_public_key: str
    """the `joint public key (K)` in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    commitment_hash: str
    """
    the `commitment hash H(K 1,0 , K 2,0 ... , K n,0 )` of the public commitments
    guardians make to each other in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)
    """

    manifest_hash: str
    """The hash of the election metadata"""

    crypto_base_hash: str
    """The `base hash code (𝑄)` in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    crypto_extended_base_hash: str
    """The `extended base hash code (𝑄')` in [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    @staticmethod
    def string_to_elementModP(value: str) -> ElementModP:
        elementModP = hex_to_p(value)
        if elementModP is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid key: " + value
            )
        return elementModP

    @staticmethod
    def string_to_elementModQ(value: str) -> ElementModQ:
        elementModQ = hex_to_q(value)
        if elementModQ is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid key: " + value
            )
        return elementModQ

    def to_sdk_format(self) -> CiphertextElectionContext:
        sdkContext = CiphertextElectionContext(
            self.number_of_guardians,
            self.quorum,
            CiphertextElectionContextDto.string_to_elementModP(self.elgamal_public_key),
            CiphertextElectionContextDto.string_to_elementModQ(self.commitment_hash),
            CiphertextElectionContextDto.string_to_elementModQ(self.manifest_hash),
            CiphertextElectionContextDto.string_to_elementModQ(self.crypto_base_hash),
            CiphertextElectionContextDto.string_to_elementModQ(
                self.crypto_extended_base_hash
            ),
        )
        return sdkContext


class ElectionState(str, Enum):
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"


class Election(Base):
    """An election object."""

    election_id: str
    key_name: str
    state: ElectionState
    context: CiphertextElectionContextDto
    manifest: ElectionManifest


class ElectionQueryRequest(BaseRequest):
    """A request for elections using the specified filter."""

    filter: Optional[Any] = None
    """
    a json object filter that will be applied to the search.
    """

    class Config:
        schema_extra = {"example": {"filter": {"election_id": "some-election-id-123"}}}


class ElectionQueryResponse(BaseResponse):
    """A collection of elections."""

    elections: List[Election] = []


class SubmitElectionRequest(BaseRequest):
    """Submit an election."""

    election_id: str
    key_name: str
    context: CiphertextElectionContextDto
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextRequest(BaseRequest):
    """
    A request to build an Election Context for a given election.
    """

    elgamal_public_key: str
    commitment_hash: str
    number_of_guardians: int
    quorum: int
    manifest_hash: Optional[str] = None
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextResponse(BaseResponse):
    """A Ciphertext Election Context."""

    context: CiphertextElectionContextDto
