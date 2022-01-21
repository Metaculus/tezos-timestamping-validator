## Introduction

This repository contains python scripts for verifications of Metaculus and Community Predictions by using [Tezos](https://tezos.com/) blockchain and [TzStamp](https://tzstamp.io/). See https://www.metaculus.com/tezos/ for mor information.


## How to use this

Tested with python 3.8

- (optional) create a virtual environment and activate it via `python -m venv .venv && source .venv/bin/active`
- Install requirements.txt `pip install -r requirements.txt`
- Run `python app.py`

For example:
```
python app.py --question-id 1 --for-date 2022-01-20
```

## How it works

Everyday we take all standing MP/CP and create [Merkle Tree](https://brilliant.org/wiki/merkle-tree/). Resulting root of the tree is timestamped on Tezos by TzStamp service. We [publish](https://www.metaculus.com/tezos/) Merkle Root on our website and tweet it using [dedicated account](https://twitter.com/tezos_forecasts).

Our simple verification interface allows you to generate [audit trail](https://www.codeproject.com/Articles/1176140/Understanding-Merkle-Trees-Why-Use-Them-Who-Uses-T#DataVerification9) and perform verification. You can go through the verification process yourself by following the tutorial below or using our example [implementation](https://github.com/Metaculus/tezos-timestamping-validator).

## Verification

To verify existence of the prediction, here is what you need to do:

* Verify TzStamp proof
* Verify uniqueness of hash for a day
* Get prediction hash for a given day
* Perform Merkle Tree audit proof 


1\. **Verify TzStamp proof**

- download the proof from our website https://www.metaculus.com/tezos/ for the given day
- Go to "verify and stamp" section https://tzstamp.io/ 
- Enter Merkle Root into SHA-256 Hash and select Proof
- Click verify

Example response:
```
Verified!
Hash existed at 24/11/2021, 14:10:32
Block hash: BM4wrLDDanvhHkJynUkGGd2hEovYEHhvC32Rp48UVRyDG6HQwiW
```

2\. **Verify uniqueness of hash for a day**

We tweet unique hash every day at https://twitter.com/tezos_forecasts

3\. **Get prediction hash for a given day**

First call api endpoint (`date_str` is in format `YYYY-MM-DD`)

```
https://www.metaculus.com/api2/questions/{question_id}/prediction-for-date/?date={date_str}
```

Then create hash (using `python`):

```python
from hashlib import sha256
import json

prediction = {"question_id:CP": <forecast_values>}
data = json.dumps(prediction)
data = data.encode('utf-8')
hashed_prediction = sha256(data).hexdigest()
```

where the `<forecast_values>` is a dict (hashmap) with key-values ordered in the following order `"y", "q1", "q2", "q3"` followed by optional `"low", "high"` for some question types. So e.g.:

```
{"y": ..., "q1": ..., , "q2": ..., "q3": ..., "low": ..., "high": ...}
```

The JSON format is with a space after `:`, e.g. `{"x": 3}`.

4\. **Perform Merkle Tree audit proof**

Once you your sha256 have hash, you need to perform Merkle Tree audit proof. You might start verification process by clicking "Start" in the above table. We will return you audit trail, to be used for verification.

Example python code to perform verification:

```python
def compute_hash(data):
    return sha256(data.encode('utf-8')).hexdigest()

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
        print(proof_till_now)

    # verifying the computed root hash against the actual root hash
    return proof_till_now == audit_trail[-1]
```

You can use any other MerkleTree library for audit proof verification, as long as it can handle the following format:

```
# pseudo example
[
    ('leafHash', isLeft=True), 
    ('leafHash', isLeft=False), 
    'merkleRoot'
]

# example with data
[
    ('5ad918ad1558058c08c009801ef35649072114d181aac0b3c852b5b10eb6cc83', False), 
    ('81984e745bfb445153dc097fdcff7d3e8b110f6df054b94d834e64d989f92b45', True), 
    '8b288237a5f6c12d92253bdd3f36f42d5c0b067debeabde28185cb819bdd5da2'
] 
```

## Example

First question on Metaculus is [Will advanced LIGO announce discovery of gravitational waves by Jan. 31 2016?](http://www.metaculus.com/questions/1/will-advanced-ligo-announce-discovery-of-gravitational-waves-by-jan-31-2016/). It's already closed, so it's easy to verify because closing prediction will be part of every Merkle Tree. 

![Screenshot from 2021-11-25 13-46-03](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2Fmypersonaldb%2FDdK9BPmWnG.png?alt=media&token=c9292e2b-b8b9-4a5c-9a76-1772f2328929)

You can see that Community Prediction was 65% at resolution. But since our data are more complex - we store distributions and histogram of individual forecasts - resulting data looks like this.

```
{'y': [...numbers...], 'q1': 0.6, 'q2': 0.65, 'q3': 0.7}
```

To access this data for a given day you can use our `api` endpoint as described above.

By sha256 hashing the following string (encoded as `utf-8`):
```
{"1:CP": {"y": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.23925, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.85021, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.31277, 0.0, 0.0, 0.71616, 0.0, 1.39605, 0.0, 0.0, 0.0, 0.0, 1.08686, 0.0, 0.0, 0.0, 0.0, 0.28917, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "q1": 0.6, "q2": 0.65, "q3": 0.7}}
```

we get `af04f9fe178f6d5bfcc85b1166154d4cbbb684cb9666711b913be02447a8f44c`.

Now let's plug in into our interface

![Screenshot from 2021-11-25 13-52-18](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2Fmypersonaldb%2FKXyDToh8Qf.png?alt=media&token=d1ef39f7-d67a-4700-8585-fb3a6b04e4f1)

Our prediction is part of Merkle Root. We did this verification on the backend, but everyone can verify it themselves using standard Merkle Tree audit proof approach described above. Required audit trial if public.

![Screenshot from 2021-11-25 13-53-01](https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2Fmypersonaldb%2FrB2lTay9EH.png?alt=media&token=50cb83c2-68c0-47c9-ad26-ed07e38f7d2f)

## Current limitations & Improvement ideas

To make this better we could

- Make it work with any single prediction update on the platform. Currently we are stamping only 1 CP and MP per day, which seems to be sufficient for practical purposes. 
- Allow users to stamp their predictions. 
- Stamp all past predictions. Currently we stamped all last standing at time of this release.

If you are interested these improvements or you have ideas for future improvements, please let us know by using contact form or tweeting at us.
