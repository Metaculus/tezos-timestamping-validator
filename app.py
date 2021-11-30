import requests
from hashlib import sha256
import json
import click

# question_id = 1 # 2513
# date_str = '2021-11-30'

base_url = 'https://metaculus.com/'
base_url = 'http://127.0.0.1:8000/'


def get_merkle_root_for_date(date_str):
    url = base_url + 'api2/tezos/?timestamp=' + date_str
    r = requests.get(url)
    r_data = r.json()[0]
    return r_data['merkle_root']


def get_prediction_for_date(question_id, date_str, type='CP'):
    if not type in ['CP', 'MP']:
        raise Exception("Invalid prediction type")
    
    url = base_url + f'api2/questions/{question_id}/prediction-for-date/?date={date_str}'
    r = requests.get(url)
    r_data = r.json()

    pred = r_data[type.lower()]
    if not pred:
        raise Exception(type +' for this day doesn\'t exist or is not accessible')
    return pred

def compute_hash(data: str) -> str:
    data = data.encode('utf-8')
    return sha256(data).hexdigest()

def get_hash_for_prediction(question_id, prediction, type='CP'):
    prediction = {f"{question_id}:{type}": prediction}
    prediction_hash = compute_hash(json.dumps(prediction))
    return prediction_hash

def get_audit_trail(merkle_root, hashed_prediction):
    url = base_url + f'api2/tezos/audit-trail/?merkle_root={merkle_root}&hashed_prediction={hashed_prediction}'
    r = requests.get(url)
    r_data = r.json()
    if not r_data['verified']:
        raise Exception("Remote verification error")
    return r_data['audit_trail']

def verify_audit_trail(chunk_hash, audit_trail):
    """
    Performs the audit-proof from the audit_trail received
    from the trusted server.
    """
    proof_till_now = chunk_hash
    for node in audit_trail[:-1]: # remove last item (Merkle Root)
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
@click.option('--question_id', prompt='Enter question id', help="Question ID")
@click.option('--date_str', prompt='Enter date of forecast', help="Date string in YYYY-MM-DD format")
def run(question_id, date_str):
    merkle_root = get_merkle_root_for_date(date_str)
    prediction = get_prediction_for_date(question_id, date_str)
    hashed_prediction = get_hash_for_prediction(question_id, prediction)
    audit_trail = get_audit_trail(merkle_root, hashed_prediction)
    verified = verify_audit_trail(hashed_prediction, audit_trail)

    if not verified:
        raise Exception("Audit trail verification failed")

    print("Hash verified")

if __name__ == '__main__':
    run()