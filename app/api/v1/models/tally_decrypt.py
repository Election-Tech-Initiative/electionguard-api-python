from typing import Any, Dict, List

from electionguard.types import BALLOT_ID

from .base import BaseResponse, BaseRequest, Base
from .election import CiphertextElectionContextDto
from .tally import CiphertextTally

__all__ = [
    "CiphertextTallyDecryptionShare",
    "DecryptTallyShareRequest",
    "DecryptionShareRequest",
    "DecryptionShareResponse",
]

DecryptionShare = Any
ElectionGuardCiphertextTally = Any


class CiphertextTallyDecryptionShare(Base):
    """
    A DecryptionShare provided by a guardian for a specific tally.

    Optionally can include ballot_shares for challenge ballots.
    """

    election_id: str  # TODO: not needed since we have the tally_name?
    tally_name: str
    guardian_id: str
    tally_share: DecryptionShare
    """The EG Decryptionshare that includes a share for each contest in the election."""
    ballot_shares: Dict[BALLOT_ID, DecryptionShare] = {}
    """A collection of shares for each challenge ballot."""


class DecryptTallyShareRequest(BaseRequest):
    """A request to partially decrypt a tally and generate a DecryptionShare."""

    guardian_id: str
    encrypted_tally: CiphertextTally
    context: CiphertextElectionContextDto


class DecryptionShareRequest(BaseRequest):
    """A request to submit a decryption share."""

    share: CiphertextTallyDecryptionShare


class DecryptionShareResponse(BaseResponse):
    """A response that includes a collection of decryption shares."""

    shares: List[CiphertextTallyDecryptionShare]
