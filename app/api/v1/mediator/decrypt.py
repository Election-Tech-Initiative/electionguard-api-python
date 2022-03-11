from typing import Any, Dict, List

from electionguard.ballot import SubmittedBallot
from electionguard.ballot_box import BallotBoxState
from electionguard.decrypt_with_shares import decrypt_ballot
from electionguard.decryption_share import DecryptionShare
from electionguard.election import CiphertextElectionContext
from electionguard.serializable import read_json_object, write_json_object
from electionguard.type import BALLOT_ID, GUARDIAN_ID
from fastapi import APIRouter, Body, HTTPException

from ..models import DecryptBallotsWithSharesRequest
from ..tags import ENCRYPT

router = APIRouter()


@router.post("/decrypt", tags=[ENCRYPT])
def decrypt_ballots(request: DecryptBallotsWithSharesRequest = Body(...)) -> Any:
    """Decrypt ballots with the provided shares"""
    ballots = [
        SubmittedBallot.from_json_object(ballot) for ballot in request.encrypted_ballots
    ]
    context: CiphertextElectionContext = CiphertextElectionContext.from_json_object(
        request.context
    )

    # only decrypt spoiled ballots using this API
    for ballot in ballots:
        if ballot.state != BallotBoxState.SPOILED:
            raise HTTPException(
                status_code=400,
                detail=f"Ballot {ballot.object_id} must be spoiled",
            )

    all_shares: List[DecryptionShare] = [
        read_json_object(share, DecryptionShare)
        for shares in request.shares.values()
        for share in shares
    ]
    shares_by_ballot = index_shares_by_ballot(all_shares)

    extended_base_hash = context.crypto_extended_base_hash
    decrypted_ballots = {
        ballot.object_id: decrypt_ballot(
            ballot, shares_by_ballot[ballot.object_id], extended_base_hash
        )
        for ballot in ballots
    }

    return write_json_object(decrypted_ballots)


def index_shares_by_ballot(
    shares: List[DecryptionShare],
) -> Dict[BALLOT_ID, Dict[GUARDIAN_ID, DecryptionShare]]:
    """
    Construct a lookup by ballot ID containing the dictionary of shares needed
    to decrypt that ballot.
    """
    shares_by_ballot: Dict[str, Dict[str, DecryptionShare]] = {}
    for share in shares:
        ballot_shares = shares_by_ballot.setdefault(share.object_id, {})
        ballot_shares[share.guardian_id] = share

    return shares_by_ballot
