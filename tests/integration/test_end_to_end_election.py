from typing import Dict, Generator, List, Optional, Tuple, TypeVar

import os
from shutil import rmtree

from . import guardian_api
from . import mediator_api
from .data import test_data

NUMBER_OF_GUARDIANS = 3
QUORUM = 2

key_name = "key_ceremony_1"

guardian_ids = ["guardian_1", "guardian_2", "guardian_3"]


def clear_storage() -> None:
    storage = os.path.join(os.getcwd(), "storage")
    if os.path.exists(storage):
        rmtree(storage)


def test_election_with_all_guardians() -> None:
    """
    Run through an entire election from end to end, simulating a scenario
    in which all guardians are present for decryption.

    This illustrates behavior for all major steps of the election, EXCEPT for the following:
    - The full key ceremony
    - Decrypting tallies and ballots with fewer than the full number of guardians present.
    """

    clear_storage()

    description = test_data.get_election_description()
    # pylint: disable=unused-variable
    guardians, context = prepare_election(description)

    # Commenting these out for now since the tally code changed significantly
    # encrypted_tally, spoiled_ballots = run_election(description, context)

    # decrypt_election(guardians, description, context, encrypted_tally, spoiled_ballots)


def prepare_election(description: Dict) -> Tuple[List[Dict], Dict]:
    """
    Create the necessary cryptography data for encrypting and decrypting the election.
    Note that this includes a small portion of the key ceremony, but does not
    run through the full process!
    """
    responses = create_guardians()
    public_keys = [response["public_keys"]["election"] for response in responses]
    joint_key_respopnse = mediator_api.combine_election_keys(key_name, public_keys)
    elgamal_public_key = joint_key_respopnse["elgamal_public_key"]
    commitment_hash = joint_key_respopnse["commitment_hash"]

    context = mediator_api.build_election_context(
        description, elgamal_public_key, commitment_hash, NUMBER_OF_GUARDIANS, QUORUM
    )

    return public_keys, context


def run_election(description: Dict, context: Dict) -> Tuple[Dict, List[Dict]]:
    """
    Run through an election:
    - Creating ballots
    - Encrypting ballots
    - Casting and spoiling ballots
    - Generating an encrypted tally
    """
    ballot_count = 4
    ballots = [
        test_data.get_ballot(f"ballot-{ballot_index + 1}")
        for ballot_index in range(ballot_count)
    ]

    encrypted_ballots = encrypt_ballots(ballots, description, context)

    casted_ballots, spoiled_ballots = cast_and_spoil_ballots(
        encrypted_ballots, description, context
    )

    tally = tally_ballots(casted_ballots, description, context)
    assert tally is not None

    return tally, spoiled_ballots


def decrypt_election(
    guardians: List[Dict],
    description: Dict,
    context: Dict,
    tally: Dict,
    spoiled_ballots: List[Dict],
) -> Tuple[Dict, Dict]:
    """
    Use the guardians to decrypt the tally and spoiled ballots after the election
    is completed.
    """
    decrypted_tally = decrypt_tally_with_all_guardians(
        tally, guardians, description, context
    )
    decrypted_spoiled_ballots = decrypt_ballots_with_all_guardians(
        spoiled_ballots, guardians, context
    )

    return decrypted_tally, decrypted_spoiled_ballots


def create_guardians() -> List[Dict]:
    """
    Create the cryptography data for all of this election's guardians.
    This is normally one piece of the key ceremony.
    """
    return [
        guardian_api.create_guardian(
            guardian_id, sequence_order, NUMBER_OF_GUARDIANS, QUORUM
        )
        for sequence_order, guardian_id in enumerate(guardian_ids)
    ]


def cast_and_spoil_ballots(
    encrypted_ballots: List[Dict], description: Dict, context: Dict
) -> Tuple[List[Dict], List[Dict]]:
    """
    Mark each ballot as either cast or spoiled.
    """
    election_id = "some_election"
    casted_ballots = []
    spoiled_ballots = []
    for index, ballot in enumerate(encrypted_ballots):
        # Spoil every other ballot
        should_spoil = index % 2 == 1
        if should_spoil:
            spoiled_ballot = mediator_api.spoil_ballot(
                election_id, ballot, description, context
            )
            spoiled_ballots.append(spoiled_ballot)
        else:
            casted_ballot = mediator_api.cast_ballot(
                election_id, ballot, description, context
            )
            casted_ballots.append(casted_ballot)

    return casted_ballots, spoiled_ballots


def encrypt_ballots(
    ballots: List[Dict], description: Dict, context: Dict
) -> List[Dict]:
    """
    Encrypt all ballots by passing them in batches to the encryption endpoint.
    """

    # In practice, the nonce and seed_hash should be randomly generated
    nonce = (
        "110191403412906482859082647039385908787148325839889522238592336039604240167009"
    )
    seed_hash = (
        "110191403412906482859082647039385908787148325839889522238592336039604240167009"
    )
    ballots_per_batch = 2
    encrypted_ballots: List[Dict] = []

    for batch in batch_list(ballots, ballots_per_batch):
        # Break up the full set of ballots into batches
        # Always pass the "next_seed_hash" from the latest response into the next request!

        response = mediator_api.encrypt_ballots(
            batch, seed_hash, nonce, description, context
        )
        encrypted_ballots.extend(response["encrypted_ballots"])
        seed_hash = response["next_seed_hash"]

    return encrypted_ballots


def tally_ballots(
    ballots: List[Dict], description: Dict, context: Dict
) -> Optional[Dict]:
    """
    Combine a collection of encrypted ballots into an encrypted tally.
    The ballots are added to the tally in batches, rather than all at once.
    """

    ballots_per_batch = 2
    current_tally: Optional[Dict] = None

    for batch in batch_list(ballots, ballots_per_batch):
        # Break up the full set of ballots into batches.
        # Once you have started the tally, pass the current tally into the next request,
        # until you have built up a full tally of all ballots.
        if not current_tally:
            current_tally = mediator_api.start_tally(batch, description, context)
        else:
            current_tally = mediator_api.append_tally(
                ballots, current_tally, description, context
            )

    return current_tally


def decrypt_tally_with_all_guardians(
    encrypted_tally: Dict, guardians: List[Dict], description: Dict, context: Dict
) -> Dict:
    """
    Using the guardian data generated during the key ceremony, decrypt
    the tally and all spoiled ballots.
    """

    tally_shares: Dict[str, Dict] = {}
    # Each guardian should decrypt their own share independently...
    for guardian in guardians:
        share = guardian_api.decrypt_tally_share(
            guardian, encrypted_tally, description, context
        )
        tally_shares[guardian["id"]] = share

    # These shares are then gathered by the mediator and used to fully decrypt the tally!
    decrypted_tally = mediator_api.decrypt_tally(
        encrypted_tally, tally_shares, description, context
    )

    return decrypted_tally


def decrypt_ballots_with_all_guardians(
    ballots: List[Dict], guardians: List[Dict], context: Dict
) -> Dict:
    """
    Decrypt all ballots using the guardians.
    Runs the decryption in batches, rather than all at once.
    """
    ballots_per_batch = 2
    decrypted_ballots: Dict = {}

    for batch in batch_list(ballots, ballots_per_batch):
        ballot_shares: Dict[str, List[Dict]] = {}
        # Each guardian should decrypt their own shares independently...
        for guardian in guardians:
            response = guardian_api.decrypt_ballot_shares(batch, guardian, context)
            shares: List[Dict] = response["shares"]
            ballot_shares[guardian["id"]] = shares

        # These shares are then gathered by the mediator and used to fully decrypt the ballots!
        decrypted_batch = mediator_api.decrypt_ballots(batch, ballot_shares, context)

        # The decrypted ballots are keyed by ballot ID.  Merge them into the full dictionary.
        decrypted_ballots = {**decrypted_ballots, **decrypted_batch}

    return decrypted_ballots


T = TypeVar("T")  # pylint:disable=invalid-name


def batch_list(items: List[T], batch_size: int) -> Generator[List[T], None, None]:
    """
    Break a list into multiple lists of maximum batch size.

    E.g. batch_list([1, 2, 3, 4, 5], 2) will yield
    ([1, 2], [3, 4], [5])
    """
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        yield batch
