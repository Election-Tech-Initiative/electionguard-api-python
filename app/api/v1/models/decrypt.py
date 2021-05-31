from typing import Any, Dict, List

from .base import BaseRequest
from .election import CiphertextElectionContext
from .guardian import Guardian, GuardianId

__all__ = [
    "DecryptBallotSharesRequest",
    "DecryptBallotSharesResponse",
    "DecryptBallotsWithSharesRequest",
]

DecryptionShare = Any
SubmittedBallot = Any


class DecryptBallotsWithSharesRequest(BaseRequest):
    """
    Decrypt the provided ballots with the provided shares
    """

    encrypted_ballots: List[SubmittedBallot]
    shares: Dict[GuardianId, List[DecryptionShare]]
    context: CiphertextElectionContext


class DecryptBallotSharesRequest(BaseRequest):
    encrypted_ballots: List[SubmittedBallot]
    guardian: Guardian
    context: CiphertextElectionContext


class DecryptBallotSharesResponse(BaseRequest):
    shares: List[DecryptionShare]
