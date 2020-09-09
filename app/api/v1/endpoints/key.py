from electionguard.key_ceremony import (
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
)
from electionguard.elgamal import elgamal_combine_public_keys
from electionguard.serializable import write_json_object
from electionguard.group import int_to_q_unchecked, int_to_p_unchecked
from fastapi import APIRouter, HTTPException
from app.models import (
    AuxiliaryKeyPair,
    ElectionKeyPair,
    ElectionKeyPairRequest,
    ElectionJointKey,
    CombineElectionKeysRequest,
)

router = APIRouter()


@router.post(
    "/election/generate", response_model=ElectionKeyPair, tags=["Guardian Only"]
)
def generate_election_keys(request: ElectionKeyPairRequest) -> ElectionKeyPair:
    """
    Generate election key pairs for use in election process
    :param request: Election key pair request
    :return: Election key pair
    """
    keys = generate_election_key_pair(
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if not keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    return ElectionKeyPair(
        public_key=str(keys.key_pair.public_key),
        secret_key=str(keys.key_pair.secret_key),
        proof=write_json_object(keys.proof),
        polynomial=write_json_object(keys.polynomial),
    )


@router.post(
    "/auxiliary/generate", response_model=AuxiliaryKeyPair, tags=["Guardian Only"]
)
def generate_auxiliary_keys() -> AuxiliaryKeyPair:
    """
    Generate auxiliary key pair for auxiliary uses during process
    :return: Auxiliary key pair
    """
    keys = generate_rsa_auxiliary_key_pair()
    if not keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    return AuxiliaryKeyPair(public_key=keys.public_key, secret_key=keys.secret_key)


@router.post("/election/combine", response_model=ElectionJointKey)
def combine_election_keys(request: CombineElectionKeysRequest) -> ElectionJointKey:
    """
    Combine public election keys into a final one
    :return: Combine Election key
    """
    public_keys = []
    for key in request.election_public_keys:
        public_keys.append(int_to_p_unchecked(key))
    joint_key = elgamal_combine_public_keys(public_keys)
    return ElectionJointKey(joint_key=write_json_object(joint_key))
