from typing import Any, Dict, List, Optional

import electionguard.auxiliary
import electionguard.election_polynomial
import electionguard.elgamal
import electionguard.group
import electionguard.guardian
import electionguard.key_ceremony
import electionguard.schnorr
from electionguard.serializable import read_json_object
from electionguard.types import GUARDIAN_ID

from .base import Base, BaseRequest, BaseResponse

__all__ = [
    "ElectionPolynomial",
    "ElectionPartialKeyBackup",
    "ElectionPartialKeyChallenge",
    "Guardian",
    "CreateGuardianRequest",
    "GuardianPublicKeysResponse",
    "GuardianBackupRequest",
    "GuardianBackupResponse",
    "BackupVerificationRequest",
    "BackupVerificationResponse",
    "BackupChallengeRequest",
    "BackupChallengeResponse",
    "ChallengeVerificationRequest",
    "to_sdk_guardian",
]

ElectionPolynomial = Any
ElectionPartialKeyBackup = Any
ElectionPartialKeyChallenge = Any
ElectionPartialKeyVerification = Any
GuardianId = Any

ElectionKeyPair = Any
AuxiliaryKeyPair = Any

AuxiliaryPublicKey = Any
ElectionPublicKey = Any

PublicKeySet = Any


class Guardian(Base):
    """The API guardian tracks the state of a guardain's interactions with other guardians."""

    guardian_id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_keys: ElectionKeyPair
    auxiliary_keys: AuxiliaryKeyPair
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_public_keys: Dict[GUARDIAN_ID, PublicKeySet] = {}
    cohort_backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_verifications: Dict[GUARDIAN_ID, ElectionPartialKeyVerification] = {}
    cohort_challenges: Dict[GUARDIAN_ID, ElectionPartialKeyChallenge] = {}


class CreateGuardianRequest(BaseRequest):
    """Request to create a Guardain."""

    guardian_id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
    auxiliary_key_pair: Optional[AuxiliaryKeyPair] = None


class CreateElectionKeyPairRequest(BaseRequest):
    """Request to create an Election Key Pair."""

    owner_id: str
    sequence_order: int
    quorum: int
    nonce: Optional[str] = None


class CreateElectionKeyPairResponse(BaseResponse):
    """Returns an ElectionKeyPair."""

    election_key_pair: ElectionKeyPair


class CreateAuxiliaryKeyPairRequest(BaseRequest):
    """Request to create an AuxiliaryKeyPair."""

    owner_id: str
    sequence_order: int


class CreateAuxiliaryKeyPairResponse(BaseResponse):
    """Returns an AuxiliaryKeyPair."""

    auxiliary_key_pair: AuxiliaryKeyPair


class GuardianPublicKeysResponse(BaseResponse):
    """Returns a set of public auxiliary and election keys"""

    public_keys: PublicKeySet


class GuardianBackupRequest(BaseRequest):
    """Request to generate ElectionPartialKeyBackups for the given PublicKeySets."""

    guardian_id: str
    quorum: int
    public_keys: List[PublicKeySet]
    override_rsa: bool = False


class GuardianBackupResponse(BaseResponse):
    """Returns a collection of ElectionPartialKeyBackups to be shared with other guardians."""

    guardian_id: str
    backups: List[ElectionPartialKeyBackup]


class BackupVerificationRequest(BaseRequest):
    """Request to verify the associated backups shared with the guardian."""

    guardian_id: str
    backup: ElectionPartialKeyBackup
    override_rsa: bool = False


class BackupVerificationResponse(BaseResponse):
    """Returns a collection of verifications."""

    verification: ElectionPartialKeyVerification


class BackupChallengeRequest(BaseRequest):
    """Request to challenge a specific backup."""

    guardian_id: str
    backup: ElectionPartialKeyBackup


class BackupChallengeResponse(BaseResponse):
    """Returns a challenge to a given backup."""

    challenge: ElectionPartialKeyChallenge


class ChallengeVerificationRequest(BaseRequest):
    """Request to verify a challenge."""

    verifier_id: str
    challenge: ElectionPartialKeyChallenge


# pylint:disable=protected-access
def to_sdk_guardian(api_guardian: Guardian) -> electionguard.guardian.Guardian:
    """
    Convert an API Guardian model to a fully-hydrated SDK Guardian model.
    """

    guardian = electionguard.guardian.Guardian(
        api_guardian.guardian_id,
        api_guardian.sequence_order,
        api_guardian.number_of_guardians,
        api_guardian.quorum,
    )

    guardian._auxiliary_keys = read_json_object(
        api_guardian.auxiliary_keys, electionguard.auxiliary.AuxiliaryKeyPair
    )
    guardian._election_keys = read_json_object(
        api_guardian.election_keys, electionguard.key_ceremony.ElectionKeyPair
    )

    cohort_keys = {
        owner_id: read_json_object(key_set, electionguard.key_ceremony.PublicKeySet)
        for (owner_id, key_set) in api_guardian.cohort_public_keys.items()
    }

    guardian._guardian_auxiliary_public_keys = {
        owner_id: key_set.auxiliary for (owner_id, key_set) in cohort_keys.items()
    }

    guardian._guardian_election_public_keys = {
        owner_id: key_set.election for (owner_id, key_set) in cohort_keys.items()
    }

    guardian._guardian_election_partial_key_backups = {
        owner_id: read_json_object(
            backup, electionguard.key_ceremony.ElectionPartialKeyBackup
        )
        for (owner_id, backup) in api_guardian.cohort_backups.items()
    }

    guardian._guardian_election_partial_key_verifications = {
        owner_id: read_json_object(
            verification, electionguard.key_ceremony.ElectionPartialKeyVerification
        )
        for (owner_id, verification) in api_guardian.cohort_verifications.items()
    }

    return guardian
