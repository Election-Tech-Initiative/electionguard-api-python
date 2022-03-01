from typing import Any, Dict, List, Optional
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
)
from app.api.v1_1.models.election import CiphertextElectionContext

from .base import Base, BaseRequest, BaseResponse, BaseValidationRequest
from .manifest import ElectionManifest, ElementModQ

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
AnyCiphertextBallot = Any
PlaintextBallot = Any

BALLOT_CODE = str
BALLOT_URL = str


class ElementModQDto(Base):
    data: str

    def to_sdk_format(self) -> ElementModQ:
        return string_to_element_mod_q(self.data)


class ElementModPDto(Base):
    data: str

    def to_sdk_format(self) -> ElementModQ:
        return string_to_element_mod_p(self.data)


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


class ElGamalCiphertextDto(Base):
    pad: ElementModPDto
    data: ElementModPDto

    def to_sdk_format(self) -> ElGamalCiphertext:
        pad = self.pad.to_sdk_format()
        data = self.data.to_sdk_format()
        result = ElGamalCiphertext(pad, data)
        return result


class ConstantChaumPedersenProofDto(Base):
    pad: ElementModPDto
    data: ElementModPDto
    challenge: ElementModQDto
    response: ElementModQDto
    constant: int
    usage: str

    def to_sdk_format(self) -> ConstantChaumPedersenProof:
        pad = self.pad.to_sdk_format()
        data = self.data.to_sdk_format()
        challenge = self.challenge.to_sdk_format()
        proof_response = self.response.to_sdk_format()
        usage = ProofUsage(self.usage)
        result = ConstantChaumPedersenProof(
            pad, data, challenge, proof_response, self.constant, usage
        )
        return result


class DisjunctiveChaumPedersenProofDto(Base):
    proof_zero_pad: ElementModPDto
    proof_zero_data: ElementModPDto
    proof_one_pad: ElementModPDto
    proof_one_data: ElementModPDto
    proof_zero_challenge: ElementModQDto
    proof_one_challenge: ElementModQDto
    challenge: ElementModQDto
    proof_zero_response: ElementModQDto
    proof_one_response: ElementModQDto
    usage: str

    def to_sdk_format(self) -> DisjunctiveChaumPedersenProof:
        proof_zero_pad = self.proof_zero_pad.to_sdk_format()
        proof_zero_data = self.proof_zero_data.to_sdk_format()
        proof_one_pad = self.proof_one_pad.to_sdk_format()
        proof_one_data = self.proof_one_data.to_sdk_format()
        proof_zero_challenge = self.proof_zero_challenge.to_sdk_format()
        proof_one_challenge = self.proof_one_challenge.to_sdk_format()
        challenge = self.challenge.to_sdk_format()
        proof_zero_response = self.proof_zero_response.to_sdk_format()
        proof_one_response = self.proof_one_response.to_sdk_format()
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
    description_hash: ElementModQDto
    ciphertext: ElGamalCiphertextDto
    crypto_hash: ElementModQDto
    is_placeholder_selection: bool
    nonce: Optional[ElementModQDto] = None
    proof: DisjunctiveChaumPedersenProofDto
    extended_data: Optional[ElGamalCiphertextDto] = None

    def to_sdk_format(self) -> CiphertextBallotSelection:
        description_hash = self.description_hash.to_sdk_format()
        ciphertext = self.ciphertext.to_sdk_format()
        crypto_hash = self.crypto_hash.to_sdk_format()
        nonce = None if self.nonce is None else self.nonce.to_sdk_format()
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
    description_hash: ElementModQDto
    ciphertext_accumulation: ElGamalCiphertextDto
    crypto_hash: ElementModQDto
    nonce: Optional[ElementModQDto] = None
    proof: ConstantChaumPedersenProofDto
    ballot_selections: List[BallotSelectionDto]

    def to_sdk_format(self) -> CiphertextBallotContest:
        description_hash = self.description_hash.to_sdk_format()
        crypto_hash = self.crypto_hash.to_sdk_format()
        ballot_selections = list(
            map(lambda s: s.to_sdk_format(), self.ballot_selections)
        )
        ciphertext_accumulation = self.ciphertext_accumulation.to_sdk_format()
        nonce = None if self.nonce is None else self.nonce.to_sdk_format()
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
    state: int
    code: ElementModQDto
    object_id: str
    style_id: str
    manifest_hash: ElementModQDto
    code_seed: ElementModQDto
    crypto_hash: ElementModQDto
    nonce: Optional[ElementModQDto] = None
    timestamp: int
    contests: List[ContestDto]

    def to_sdk_format(self) -> SubmittedBallot:
        state = BallotBoxState(self.state)
        code = self.code.to_sdk_format()
        manifest_hash = self.manifest_hash.to_sdk_format()
        code_seed = self.code_seed.to_sdk_format()
        crypto_hash = self.crypto_hash.to_sdk_format()
        contests = list(map(lambda c: c.to_sdk_format(), self.contests))
        nonce = None if self.nonce is None else self.nonce.to_sdk_format()

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
