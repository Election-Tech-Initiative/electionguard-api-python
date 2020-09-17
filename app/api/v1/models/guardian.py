from typing import Any, List, Optional

import electionguard.election_polynomial
import electionguard.elgamal
import electionguard.guardian
import electionguard.key_ceremony
import electionguard.schnorr
from electionguard.serializable import read_json_object

from .base import Base
from .key import AuxiliaryKeyPair, AuxiliaryPublicKey, ElectionKeyPair

__all__ = [
    "ElectionPolynomial",
    "ElectionPartialKeyBackup",
    "ElectionPartialKeyChallenge",
    "Guardian",
    "GuardianRequest",
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


class Guardian(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    election_key_pair: ElectionKeyPair
    auxiliary_key_pair: AuxiliaryKeyPair


class GuardianRequest(Base):
    id: str
    sequence_order: int
    number_of_guardians: int
    quorum: int
    nonce: Optional[str] = None
    auxiliary_key_pair: Optional[AuxiliaryKeyPair] = None


class GuardianBackup(Base):
    id: str
    election_partial_key_backups: List[ElectionPartialKeyBackup]


class GuardianBackupRequest(Base):
    guardian_id: str
    quorum: int
    election_polynomial: ElectionPolynomial
    auxiliary_public_keys: List[AuxiliaryPublicKey]
    override_rsa: bool = False


class BackupVerificationRequest(Base):
    verifier_id: str
    election_partial_key_backup: ElectionPartialKeyBackup
    auxiliary_key_pair: AuxiliaryKeyPair
    override_rsa: bool = False


class BackupChallengeRequest(Base):
    election_partial_key_backup: ElectionPartialKeyBackup
    election_polynomial: ElectionPolynomial


class ChallengeVerificationRequest(Base):
    verifier_id: str
    election_partial_key_challenge: ElectionPartialKeyChallenge


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
    guardian._auxiliary_keys = electionguard.key_ceremony.AuxiliaryKeyPair(
        api_guardian.auxiliary_key_pair.public_key,
        api_guardian.auxiliary_key_pair.secret_key,
    )
    guardian._election_keys = electionguard.key_ceremony.ElectionKeyPair(
        read_json_object(
            guardian._election_keys.key_pair, electionguard.elgamal.ElGamalKeyPair
        ),
        read_json_object(
            guardian._election_keys.proof, electionguard.schnorr.SchnorrProof
        ),
        read_json_object(
            guardian._election_keys.polynomial,
            electionguard.election_polynomial.ElectionPolynomial,
        ),
    )

    return guardian
