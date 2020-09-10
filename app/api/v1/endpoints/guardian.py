from electionguard.auxiliary import AuxiliaryPublicKey
from electionguard.election_polynomial import ElectionPolynomial
from electionguard.group import int_to_q_unchecked
from electionguard.key_ceremony import (
    ElectionPartialKeyBackup,
    ElectionPartialKeyChallenge,
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
    generate_election_partial_key_backup,
    generate_election_partial_key_challenge,
    verify_election_partial_key_backup,
    verify_election_partial_key_challenge,
)
from electionguard.rsa import rsa_decrypt, rsa_encrypt
from electionguard.serializable import write_json_object
from fastapi import APIRouter, HTTPException
from typing import Any, List

from ..models import (
    AuxiliaryKeyPair,
    BackupChallengeRequest,
    BackupVerificationRequest,
    ChallengeVerificationRequest,
    ElectionKeyPair,
    Guardian,
    GuardianRequest,
    GuardianBackup,
    GuardianBackupRequest,
)
from app.utils import read_json_object
from ..tags import GUARDIAN_ONLY

router = APIRouter()

identity = lambda message, key: message


@router.post("", response_model=Guardian, tags=[GUARDIAN_ONLY])
def create_guardian(request: GuardianRequest) -> Guardian:
    """
    Create a guardian for the election process with the associated keys
    """
    election_keys = generate_election_key_pair(
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if request.auxiliary_key_pair is None:
        auxiliary_keys = generate_rsa_auxiliary_key_pair()
    else:
        auxiliary_keys = request.auxiliary_key_pair
    if not election_keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    if not auxiliary_keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    return Guardian(
        id=request.id,
        sequence_order=request.sequence_order,
        number_of_guardians=request.number_of_guardians,
        quorum=request.quorum,
        election_key_pair=ElectionKeyPair(
            public_key=str(election_keys.key_pair.public_key),
            secret_key=str(election_keys.key_pair.secret_key),
            proof=write_json_object(election_keys.proof),
            polynomial=write_json_object(election_keys.polynomial),
        ),
        auxiliary_key_pair=AuxiliaryKeyPair(
            public_key=auxiliary_keys.public_key, secret_key=auxiliary_keys.secret_key
        ),
    )


@router.post("/backup", response_model=GuardianBackup, tags=[GUARDIAN_ONLY])
def create_guardian_backup(request: GuardianBackupRequest) -> GuardianBackup:
    """
    Generate all election partial key backups based on existing public keys
    :param request: Guardian backup request
    :return: Guardian backup
    """
    encrypt = identity if request.override_rsa else rsa_encrypt
    backups: List[Any] = []
    for auxiliary_public_key in request.auxiliary_public_keys:
        backup = generate_election_partial_key_backup(
            request.guardian_id,
            read_json_object(request.election_polynomial, ElectionPolynomial),
            AuxiliaryPublicKey(
                auxiliary_public_key.owner_id,
                auxiliary_public_key.sequence_order,
                auxiliary_public_key.key,
            ),
            encrypt,
        )
        if not backup:
            raise HTTPException(status_code=500, detail="Backup failed to be generated")
        backups.append(write_json_object(backup))

    return GuardianBackup(
        id=request.guardian_id,
        election_partial_key_backups=backups,
    )


@router.post("/backup/verify", tags=[GUARDIAN_ONLY])
def verify_backup(request: BackupVerificationRequest) -> Any:
    decrypt = identity if request.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        request.verifier_id,
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(request.auxiliary_key_pair, AuxiliaryKeyPair),
        decrypt,
    )
    if not verification:
        raise HTTPException(
            status_code=500, detail="Backup verification process failed"
        )
    return write_json_object(verification)


@router.post("/challenge", tags=[GUARDIAN_ONLY])
def create_backup_challenge(request: BackupChallengeRequest) -> Any:
    challenge = generate_election_partial_key_challenge(
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(request.election_polynomial, ElectionPolynomial),
    )
    if not challenge:
        raise HTTPException(
            status_code=500, detail="Backup challenge generation failed"
        )
    # FIXME Challenge value is ElementModQ converted to int that is too large
    challenge._replace(value=str(challenge.value))
    return write_json_object(challenge)


@router.post(
    "/challenge/verify",
    tags=[GUARDIAN_ONLY],
)
def verify_challenge(request: ChallengeVerificationRequest) -> Any:
    verification = verify_election_partial_key_challenge(
        request.verifier_id,
        read_json_object(
            request.election_partial_key_challenge, ElectionPartialKeyChallenge
        ),
    )
    if not verification:
        raise HTTPException(
            status_code=500, detail="Challenge verification process failed"
        )
    return write_json_object(verification)
