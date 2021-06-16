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

# TODO: remove all optional colections in favor of empty
class Guardian(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_keys: ElectionKeyPair
    auxiliary_keys: AuxiliaryKeyPair
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_election_keys: Dict[GUARDIAN_ID, ElectionPublicKey] = {}
    cohort_auxiliary_keys: Dict[GUARDIAN_ID, AuxiliaryPublicKey] = {}
    cohort_backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_verifications: Dict[GUARDIAN_ID, ElectionPartialKeyVerification]
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


class GuardianBackupResponse(BaseResponse):
    guardian_id: str
    election_partial_key_backups: List[ElectionPartialKeyBackup]


class GuardianBackupRequest(BaseRequest):
    guardian_id: str
    quorum: int
    auxiliary_public_keys: List[AuxiliaryPublicKey]
    override_rsa: bool = False


class BackupReceiveVerificationRequest(BaseRequest):
    guardian_id: str
    election_partial_key_backup: ElectionPartialKeyBackup
    override_rsa: bool = False


class BackupVerificationRequest(BaseRequest):
    verifier_id: str
    election_partial_key_backup: ElectionPartialKeyBackup
    election_public_key: ElectionPublicKey
    auxiliary_key_pair: AuxiliaryKeyPair
    override_rsa: bool = False


class BackupVerificationResponse(BaseResponse):
    verification: ElectionPartialKeyVerification


class BackupChallengeRequest(BaseRequest):
    guardian_id: str
    election_partial_key_backup: ElectionPartialKeyBackup


class BackupChallengeResponse(BaseResponse):
    challenge: ElectionPartialKeyChallenge


class ChallengeVerificationRequest(BaseRequest):
    verifier_id: str
    election_partial_key_challenge: ElectionPartialKeyChallenge


# pylint:disable=protected-access
def to_sdk_guardian(api_guardian: Guardian) -> electionguard.guardian.Guardian:
    """
    Convert an API Guardian model to a fully-hydrated SDK Guardian model.
    """

    guardian = electionguard.guardian.Guardian(
        api_guardian.id,
        api_guardian.sequence_order,
        api_guardian.number_of_guardians,
        api_guardian.quorum,
    )

    guardian._auxiliary_keys = electionguard.auxiliary.AuxiliaryKeyPair(
        api_guardian.id,
        api_guardian.sequence_order,
        api_guardian.auxiliary_keys.public_key,
        api_guardian.auxiliary_keys.secret_key,
    )

    election_public_key = read_json_object(
        api_guardian.election_keys.key_pair["public_key"],
        electionguard.group.ElementModP,
    )
    election_secret_key = read_json_object(
        api_guardian.election_keys.key_pair["secret_key"],
        electionguard.group.ElementModQ,
    )
    guardian._election_keys = electionguard.key_ceremony.ElectionKeyPair(
        api_guardian.id,
        api_guardian.sequence_order,
        electionguard.elgamal.ElGamalKeyPair(election_secret_key, election_public_key),
        read_json_object(
            api_guardian.election_keys.polynomial,
            electionguard.election_polynomial.ElectionPolynomial,
        ),
    )

    # TODO: backups and things

    return guardian
