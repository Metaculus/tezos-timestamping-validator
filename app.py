import json
import logging
from hashlib import sha256

import click
import requests

logging.basicConfig()
logger = logging.getLogger()

BASE_URL = "https://www.metaculus.com/api2"


def get_merkle_root_for_date(date_str: str) -> str:
    response = requests.get(f"{BASE_URL}/tezos/", params={"timestamp": date_str})
    response.raise_for_status()
    data = response.json()
    if not data:
        raise RuntimeError("No Metaculus tezos stamp found")
    return data[0]["merkle_root"], data[0]["timestamp"][:19]


def get_prediction_for_date(question_id: str, date_str: str) -> dict:
    url = f"{BASE_URL}/questions/{question_id}/prediction-for-date/"

    response = requests.get(url, params={"date": date_str})
    response.raise_for_status()
    data = response.json()

    pred = data["cp"]  # cp stands for community prediction
    if not pred:
        raise RuntimeError(type + " for this day doesn't exist or is not accessible")
    return pred


def compute_hash(data: str) -> str:
    return sha256(data.encode("utf-8")).hexdigest()


def get_hash_for_prediction(question_id, prediction, type="CP"):
    prediction = {f"{question_id}:{type}": prediction}
    prediction_hash = compute_hash(json.dumps(prediction))
    return prediction_hash


def get_audit_trail(merkle_root: str, hashed_prediction: str):
    url = f"{BASE_URL}/tezos/audit-trail/"
    response = requests.get(
        url, params={"merkle_root": merkle_root, "hashed_prediction": hashed_prediction}
    )
    try:
        response.raise_for_status()
    except Exception as ex:
        raise RuntimeError(
            f"Metaculus wasn't able to proceed with verification. {response.json()}"
        ) from ex

    data = response.json()
    if not data["verified"]:
        raise RuntimeError("Remote verification error")
    return data["audit_trail"]


def verify_audit_trail(chunk_hash, audit_trail) -> bool:
    """
    Performs the audit-proof from the audit_trail received
    from the trusted server.
    """
    proof_till_now = chunk_hash
    for node in audit_trail[:-1]:  # remove last item (Merkle Root)
        node_hash = node[0]
        is_left = node[1]
        if is_left:
            # the order of hash concatenation depends on whether the
            # the node is a left child or right child of its parent
            proof_till_now = compute_hash(node_hash + proof_till_now)
        else:
            proof_till_now = compute_hash(proof_till_now + node_hash)

    # verifying the computed root hash against the actual root hash
    return proof_till_now == audit_trail[-1]


@click.command()
@click.option(
    "--question-id",
    prompt="Enter question id",
    help="Question ID (e.g. 2513)",
    type=click.INT,
)
@click.option(
    "--for-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    prompt="Enter date of forecast",
    help="Date string in YYYY-MM-DD format (e.g. 2021-11-30)",
)
def run(question_id: int, for_date: str):
    merkle_root, timestamp = get_merkle_root_for_date(for_date)
    prediction = get_prediction_for_date(question_id, timestamp)
    hashed_prediction = get_hash_for_prediction(question_id, prediction)
    print(prediction, hashed_prediction)
    audit_trail = get_audit_trail(merkle_root, hashed_prediction)
    verified = verify_audit_trail(hashed_prediction, audit_trail)

    if not verified:
        raise RuntimeError("Audit trail verification failed")

    click.echo("Hash verified")


if __name__ == "__main__":
    run()
