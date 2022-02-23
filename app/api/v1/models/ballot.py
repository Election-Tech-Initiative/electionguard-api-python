from typing import Any, Dict, List, Optional
from enum import Enum
from electionguard.ballot import (
    SubmittedBallot,
    CiphertextBallot,
    CiphertextBallotContest,
    CiphertextBallotSelection,
)
from electionguard.chaum_pedersen import DisjunctiveChaumPedersenProof
from electionguard.elgamal import ElGamalCiphertext
from electionguard.chaum_pedersen import ConstantChaumPedersenProof
from electionguard.ballot_box import BallotBoxState
from electionguard.proof import ProofUsage


from app.api.v1.common.type_mapper import (
    string_to_element_mod_p,
    string_to_element_mod_q,
    string_to_nullable_element_mod_q,
)
from app.api.v1_1.models.election import CiphertextElectionContext

from .base import Base, BaseRequest, BaseResponse, BaseValidationRequest
from .manifest import ElectionManifest

__all__ = [
    "BallotQueryResponse",
    "BallotInventory",
    "BallotInventoryResponse",
    "BaseBallotRequest",
    "CastBallotsRequest",
    "SpoilBallotsRequest",
    "SubmitBallotsRequest",
    "ValidateBallotRequest",
]

DecryptionShare = Any
AnySubmittedBallot = Any
CiphertextBallot = Any
PlaintextBallot = Any

BALLOT_CODE = str
BALLOT_URL = str


class BallotInventory(Base):
    """
    The Ballot Inventory retains metadata about ballots in an election,
    including mappings of ballot tracking codes to ballot id's
    """

    election_id: str
    cast_ballot_count: int = 0
    spoiled_ballot_count: int = 0
    cast_ballots: Dict[BALLOT_CODE, BALLOT_URL] = {}
    """
    Collection of cast ballot codes mapped to a route that is accessible.

    Note: the BALLOT_URL is storage dependent and is not meant to be shared with the election record
    """
    spoiled_ballots: Dict[BALLOT_CODE, BALLOT_URL] = {}
    """
    Collection of spoiled ballot codes mapped to a route that is accessible.

    Note: the BALLOT_URL is storage dependent and is not meant to be shared with the election record
    """


class BallotInventoryResponse(BaseResponse):
    inventory: BallotInventory


class BallotQueryResponse(BaseResponse):
    election_id: str
    ballots: List[CiphertextBallot] = []


class BaseBallotRequest(BaseRequest):
    election_id: Optional[str] = None
    manifest: Optional[ElectionManifest] = None
    context: Optional[CiphertextElectionContext] = None


class CastBallotsRequest(BaseBallotRequest):
    """Cast the enclosed ballots."""

    ballots: List[CiphertextBallot]


class SpoilBallotsRequest(BaseBallotRequest):
    """Spoil the enclosed ballots."""

    ballots: List[CiphertextBallot]


class SubmitBallotsRequest(BaseBallotRequest):
    """Submit a ballot against a specific election."""

    ballots: List[AnySubmittedBallot]


class BallotBoxStateDto(Enum):
    CAST = "CAST"
    SPOILED = "SPOILED"
    UNKNOWN = "UNKNOWN"


def ballot_box_state_dto_to_sdk(
    ballot_box_state_dto: BallotBoxStateDto,
) -> BallotBoxState:
    if ballot_box_state_dto == BallotBoxStateDto.CAST:
        return BallotBoxState.CAST
    if ballot_box_state_dto == BallotBoxStateDto.SPOILED:
        return BallotBoxState.SPOILED
    return BallotBoxState.UNKNOWN


class ElGamalCiphertextDto(Base):
    pad: str
    data: str

    def to_sdk_format(self) -> ElGamalCiphertext:
        pad = string_to_element_mod_p(self.pad)
        data = string_to_element_mod_p(self.data)
        result = ElGamalCiphertext(pad, data)
        return result


class ConstantChaumPedersenProofDto(Base):
    proof_zero_pad: str
    proof_zero_data: str
    challenge: str
    proof_zero_response: str
    constant: int
    usage: str

    def to_sdk_format(self) -> ConstantChaumPedersenProof:
        pad = string_to_element_mod_p(self.proof_zero_pad)
        data = string_to_element_mod_p(self.proof_zero_data)
        challenge = string_to_element_mod_q(self.challenge)
        proof_response = string_to_element_mod_q(self.proof_zero_response)
        usage = ProofUsage(self.usage)
        result = ConstantChaumPedersenProof(
            pad, data, challenge, proof_response, self.constant, usage
        )
        return result


class DisjunctiveChaumPedersenProofDto(Base):
    proof_zero_pad: str
    proof_zero_data: str
    proof_one_pad: str
    proof_one_data: str
    proof_zero_challenge: str
    proof_one_challenge: str
    challenge: str
    proof_zero_response: str
    proof_one_response: str
    usage: str

    def to_sdk_format(self) -> DisjunctiveChaumPedersenProof:
        proof_zero_pad = string_to_element_mod_p(self.proof_zero_pad)
        proof_zero_data = string_to_element_mod_p(self.proof_zero_data)
        proof_one_pad = string_to_element_mod_p(self.proof_one_pad)
        proof_one_data = string_to_element_mod_p(self.proof_one_data)
        proof_zero_challenge = string_to_element_mod_q(self.proof_zero_challenge)
        proof_one_challenge = string_to_element_mod_q(self.proof_one_challenge)
        challenge = string_to_element_mod_q(self.challenge)
        proof_zero_response = string_to_element_mod_q(self.proof_zero_response)
        proof_one_response = string_to_element_mod_q(self.proof_one_response)
        usage = ProofUsage(self.usage)

        result = DisjunctiveChaumPedersenProof(
            proof_zero_pad,
            proof_zero_data,
            proof_one_pad,
            proof_one_data,
            proof_zero_challenge,
            proof_one_challenge,
            challenge,
            proof_zero_response,
            proof_one_response,
            usage,
        )
        return result


class BallotSelectionDto(Base):
    object_id: str
    sequence_order: int
    description_hash: str
    ciphertext: ElGamalCiphertextDto
    crypto_hash: str
    is_placeholder_selection: bool
    nonce: Optional[str] = None
    proof: DisjunctiveChaumPedersenProofDto
    extended_data: Optional[ElGamalCiphertextDto] = None

    def to_sdk_format(self) -> CiphertextBallotSelection:
        description_hash = string_to_element_mod_q(self.description_hash)
        ciphertext = self.ciphertext.to_sdk_format()
        crypto_hash = string_to_element_mod_q(self.crypto_hash)
        nonce = string_to_nullable_element_mod_q(self.nonce)
        proof = self.proof.to_sdk_format()
        extended_data = (
            None if self.extended_data is None else self.extended_data.to_sdk_format()
        )
        result = CiphertextBallotSelection(
            self.object_id,
            description_hash,
            ciphertext,
            crypto_hash,
            self.is_placeholder_selection,
            nonce,
            proof,
            extended_data,
        )
        return result


class ContestDto(Base):
    object_id: str
    description_hash: str
    ciphertext_accumulation: ElGamalCiphertextDto
    crypto_hash: str
    nonce: Optional[str] = None
    proof: ConstantChaumPedersenProofDto
    ballot_selections: List[BallotSelectionDto]

    def to_sdk_format(self) -> CiphertextBallotContest:
        description_hash = string_to_element_mod_q(self.description_hash)
        crypto_hash = string_to_element_mod_q(self.crypto_hash)
        ballot_selections = list(
            map(lambda s: s.to_sdk_format(), self.ballot_selections)
        )
        ciphertext_accumulation = self.ciphertext_accumulation.to_sdk_format()
        nonce = string_to_nullable_element_mod_q(self.nonce)
        proof = self.proof.to_sdk_format()
        result = CiphertextBallotContest(
            self.object_id,
            description_hash,
            ballot_selections,
            ciphertext_accumulation,
            crypto_hash,
            nonce,
            proof,
        )
        return result


class SubmittedBallotDto(Base):
    state: BallotBoxStateDto
    code: str
    object_id: str
    style_id: str
    manifest_hash: str
    code_seed: str
    crypto_hash: str
    nonce: Optional[str] = None
    timestamp: int
    contests: List[ContestDto]

    def to_sdk_format(self) -> SubmittedBallot:
        state = ballot_box_state_dto_to_sdk(self.state)
        code = string_to_element_mod_q(self.code)
        manifest_hash = string_to_element_mod_q(self.manifest_hash)
        code_seed = string_to_element_mod_q(self.code_seed)
        crypto_hash = string_to_element_mod_q(self.crypto_hash)
        contests = list(map(lambda c: c.to_sdk_format(), self.contests))
        nonce = string_to_nullable_element_mod_q(self.nonce)

        ballot = SubmittedBallot(
            self.object_id,
            self.style_id,
            manifest_hash,
            code_seed,
            contests,
            code,
            self.timestamp,
            crypto_hash,
            nonce,
            state,
        )
        return ballot


class SubmitBallotsRequestDto(BaseValidationRequest):
    """Submit a ballot against a specific election."""

    ballots: List[SubmittedBallotDto]


class ValidateBallotRequest(BaseValidationRequest):
    """Submit a ballot against a specific election description and contest to determine if it is accepted."""

    ballot: CiphertextBallot
    manifest: ElectionManifest
    context: CiphertextElectionContext
