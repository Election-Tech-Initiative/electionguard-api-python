from typing import Any, List, Optional

import electionguard.auxiliary
import electionguard.election_polynomial
import electionguard.elgamal
import electionguard.group
import electionguard.guardian
import electionguard.key_ceremony
import electionguard.schnorr
from electionguard.serializable import read_json_object

from .base import Base, BaseRequest, BaseResponse

__all__ = [
    "ElectionPolynomial",
    "ElectionPartialKeyBackup",
    "ElectionPartialKeyChallenge",
    "Guardian",
    "CreateGuardianRequest",
    "GuardianBackup",
    "GuardianBackupRequest",
    "BackupVerificationRequest",
    "BackupChallengeRequest",
    "ChallengeVerificationRequest",
    "convert_guardian",
]

ElectionPolynomial = Any
ElectionPartialKeyBackup = Any
ElectionPartialKeyChallenge = Any
GuardianId = Any

ElectionKeyPair = Any
AuxiliaryKeyPair = Any

AuxiliaryPublicKey = Any
ElectionPublicKey = Any


class Guardian(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_key_pair: ElectionKeyPair
    auxiliary_key_pair: AuxiliaryKeyPair


class CreateGuardianRequest(BaseRequest):

    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
    auxiliary_key_pair: Optional[AuxiliaryKeyPair] = None


class GuardianBackup(BaseRequest):
    id: str
    election_partial_key_backups: List[ElectionPartialKeyBackup]


class GuardianBackupRequest(BaseRequest):
    guardian_id: str
    quorum: int
    election_polynomial: ElectionPolynomial
    auxiliary_public_keys: List[AuxiliaryPublicKey]
    override_rsa: bool = False


class BackupVerificationRequest(BaseRequest):
    verifier_id: str
    election_partial_key_backup: ElectionPartialKeyBackup
    election_public_key: ElectionPublicKey
    auxiliary_key_pair: AuxiliaryKeyPair
    override_rsa: bool = False


class BackupChallengeRequest(BaseRequest):
    election_partial_key_backup: ElectionPartialKeyBackup
    election_polynomial: ElectionPolynomial


class ChallengeVerificationRequest(BaseRequest):
    verifier_id: str
    election_partial_key_challenge: ElectionPartialKeyChallenge


# pylint:disable=protected-access
def convert_guardian(api_guardian: Guardian) -> electionguard.guardian.Guardian:
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
        api_guardian.auxiliary_key_pair.public_key,
        api_guardian.auxiliary_key_pair.secret_key,
    )

    election_public_key = read_json_object(
        api_guardian.election_key_pair.key_pair["public_key"],
        electionguard.group.ElementModP,
    )
    election_secret_key = read_json_object(
        api_guardian.election_key_pair.key_pair["secret_key"],
        electionguard.group.ElementModQ,
    )
    guardian._election_keys = electionguard.key_ceremony.ElectionKeyPair(
        api_guardian.id,
        api_guardian.sequence_order,
        electionguard.elgamal.ElGamalKeyPair(election_secret_key, election_public_key),
        read_json_object(
            api_guardian.election_key_pair.polynomial,
            electionguard.election_polynomial.ElectionPolynomial,
        ),
    )

    return guardian
