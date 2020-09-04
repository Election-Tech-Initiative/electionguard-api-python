from electionguard.election_polynomial import ElectionPolynomial
from electionguard.group import int_to_q_unchecked
from electionguard.key_ceremony import (
    AuxiliaryPublicKey,
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
    generate_election_partial_key_backup,
)
from electionguard.serializable import write_json_object, set_deserializers
from fastapi import APIRouter, HTTPException
from jsons import load
from typing import Any, cast, List

from app.models import (
    AuxiliaryKeyPair,
    ElectionKeyPair,
    Guardian,
    GuardianRequest,
    GuardianBackup,
    GuardianBackupRequest,
)
from app.utils import read_json_object

router = APIRouter()


@router.post("", response_model=Guardian)
def create_guardian(request: GuardianRequest) -> Guardian:
    """
    Create a guardian for the election process with the associated keys
    """
    election_keys = generate_election_key_pair(
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    auxiliary_keys = generate_rsa_auxiliary_key_pair()
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


@router.post("/backup", response_model=GuardianBackup)
def create_guardian_backup(request: GuardianBackupRequest) -> GuardianBackup:
    """
    Generate all election partial key backups based on existing public keys
    :param request: Guardian backup request
    :return: Guardian backup
    """
    backups: List[Any] = []
    for auxiliary_public_key in request.auxiliary_public_keys:
        backup = generate_election_partial_key_backup(
            request.guardian_id,
            read_json_object(request.election_polynomial, ElectionPolynomial),
            read_json_object(auxiliary_public_key, AuxiliaryPublicKey),
        )
        if backup is None:
            raise HTTPException(status_code=500, detail="Backup failed to be generated")
        backups.append(write_json_object(backup))

    return GuardianBackup(
        id=request.guardian_id,
        election_partial_key_backups=backups,
    )

