from typing import Any, List
from electionguard.auxiliary import AuxiliaryKeyPair, AuxiliaryPublicKey
from electionguard.election_polynomial import ElectionPolynomial
from electionguard.group import int_to_q_unchecked
from electionguard.key_ceremony import (
    ElectionKeyPair,
    ElectionPublicKey,
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
from electionguard.serializable import read_json_object, write_json_object
from fastapi import APIRouter, HTTPException

from ..models import (
    BaseQueryRequest,
    BaseResponse,
    BackupChallengeRequest,
    BackupVerificationRequest,
    ChallengeVerificationRequest,
    Guardian,
    CreateGuardianRequest,
    GuardianBackup,
    GuardianBackupRequest,
)
from ..tags import KEY_CEREMONY

router = APIRouter()

identity = lambda message, key: message


@router.post("", response_model=Guardian, tags=[KEY_CEREMONY])
def create_guardian(request: CreateGuardianRequest) -> Guardian:
    """
    Create a guardian for the election process with the associated keys
    """
    election_keys = generate_election_key_pair(
        request.id,
        request.sequence_order,
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if request.auxiliary_key_pair is None:
        auxiliary_keys = generate_rsa_auxiliary_key_pair(
            request.id, request.sequence_order
        )
    else:
        auxiliary_keys = read_json_object(request.auxiliary_key_pair, AuxiliaryKeyPair)
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
            owner_id=request.id,
            sequence_order=request.sequence_order,
            key_pair=write_json_object(election_keys.key_pair),
            polynomial=write_json_object(election_keys.polynomial),
        ),
        auxiliary_key_pair=AuxiliaryKeyPair(
            owner_id=request.id,
            sequence_order=request.sequence_order,
            public_key=auxiliary_keys.public_key,
            secret_key=auxiliary_keys.secret_key,
        ),
    )


@router.post("/backup", response_model=GuardianBackup, tags=[KEY_CEREMONY])
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


@router.post("/backup/verify", tags=[KEY_CEREMONY])
def verify_backup(request: BackupVerificationRequest) -> BaseResponse:
    """aaa"""
    decrypt = identity if request.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        request.verifier_id,
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(request.election_public_key, ElectionPublicKey),
        read_json_object(request.auxiliary_key_pair, AuxiliaryKeyPair),
        decrypt,
    )
    if not verification:
        raise HTTPException(
            status_code=500, detail="Backup verification process failed"
        )
    return write_json_object(verification)


@router.post("/challenge", tags=[KEY_CEREMONY])
def create_backup_challenge(request: BackupChallengeRequest) -> BaseResponse:
    """aaa"""
    challenge = generate_election_partial_key_challenge(
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(request.election_polynomial, ElectionPolynomial),
    )
    if not challenge:
        raise HTTPException(
            status_code=500, detail="Backup challenge generation failed"
        )

    return write_json_object(challenge)


@router.post("/challenge/verify", tags=[KEY_CEREMONY])
def verify_challenge(request: ChallengeVerificationRequest) -> BaseResponse:
    """aaa"""
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
