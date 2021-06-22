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
    "BackupReceiveVerificationRequest",
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

# TODO: remove all optional colections in favor of empty
class Guardian(Base):
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

    guardian_id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
    auxiliary_key_pair: Optional[AuxiliaryKeyPair] = None


class CreateElectionKeyPairRequest(BaseRequest):

    owner_id: str
    sequence_order: int
    quorum: int
    nonce: Optional[str] = None


class CreateElectionKeyPairResponse(BaseResponse):
    election_key_pair: ElectionKeyPair


class CreateAuxiliaryKeyPairRequest(BaseRequest):
    owner_id: str
    sequence_order: int


class CreateAuxiliaryKeyPairResponse(BaseResponse):
    auxiliary_key_pair: AuxiliaryKeyPair


class GuardianPublicKeysResponse(BaseResponse):
    """A set of public auxiliary and election keys"""

    public_keys: PublicKeySet


class GuardianBackupRequest(BaseRequest):
    guardian_id: str
    quorum: int
    public_keys: List[PublicKeySet]
    override_rsa: bool = False


class GuardianBackupResponse(BaseResponse):
    guardian_id: str
    backups: List[ElectionPartialKeyBackup]


class BackupReceiveVerificationRequest(BaseRequest):
    guardian_id: str
    backup: ElectionPartialKeyBackup
    override_rsa: bool = False


class BackupVerificationRequest(BaseRequest):
    verifier_id: str
    backup: ElectionPartialKeyBackup
    election_public_key: ElectionPublicKey
    auxiliary_key_pair: AuxiliaryKeyPair
    override_rsa: bool = False


class BackupVerificationResponse(BaseResponse):
    verification: ElectionPartialKeyVerification


class BackupChallengeRequest(BaseRequest):
    guardian_id: str
    backup: ElectionPartialKeyBackup


class BackupChallengeResponse(BaseResponse):
    challenge: ElectionPartialKeyChallenge


class ChallengeVerificationRequest(BaseRequest):
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

    # TODO: backups and things

    return guardian
