import electionguard.election
from electionguard.serializable import read_json_object
import electionguard.tally
from typing import Any, Dict, List


from .ballot import CiphertextAcceptedBallot
from .base import Base
from .election import ElectionDescription, CiphertextElectionContext
from .guardian import Guardian

__all__ = [
    "PublishedCiphertextTally",
    "TallyDecryptionShare",
    "StartTallyRequest",
    "AppendTallyRequest",
    "DecryptTallyRequest",
    "DecryptTallyShareRequest",
    "convert_tally",
]

PublishedCiphertextTally = Any
TallyDecryptionShare = Any


class StartTallyRequest(Base):
    ballots: List[CiphertextAcceptedBallot]
    description: ElectionDescription
    context: CiphertextElectionContext


class AppendTallyRequest(StartTallyRequest):
    encrypted_tally: PublishedCiphertextTally


class DecryptTallyRequest(Base):
    encrypted_tally: PublishedCiphertextTally
    shares: Dict[str, TallyDecryptionShare]
    description: ElectionDescription
    context: CiphertextElectionContext


class DecryptTallyShareRequest(Base):
    encrypted_tally: PublishedCiphertextTally
    guardian: Guardian
    description: ElectionDescription
    context: CiphertextElectionContext


def convert_tally(
    encrypted_tally: PublishedCiphertextTally,
    description: electionguard.election.InternalElectionDescription,
    context: electionguard.election.CiphertextElectionContext,
) -> electionguard.tally.CiphertextTally:
    """
    Convert to an SDK CiphertextTally model
    """

    published_tally = read_json_object(
        encrypted_tally, electionguard.tally.PublishedCiphertextTally
    )
    tally = electionguard.tally.CiphertextTally(
        published_tally.object_id, description, context
    )
    tally.cast = published_tally.cast

    return tally
