from electionguard.elgamal import elgamal_combine_public_keys
from electionguard.serializable import write_json_object
from electionguard.group import int_to_p_unchecked
from fastapi import APIRouter
from ..models import (
    ElectionJointKey,
    CombineElectionKeysRequest,
)
from ..tags import KEY_CEREMONY

router = APIRouter()


@router.post("/election/combine", response_model=ElectionJointKey, tags=[KEY_CEREMONY])
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
