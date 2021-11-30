## Introduction

This repository contains python scripts for verifications of Metaculus and Community Predictions by using [Tezos]() blockchain and [TzStamp]().


## How to use this

Tested with python 3.8

- Install requirements.txt `pip install -r requirements.txt`
- Run `python app.py`

For example 
```
python app.py --question_id=1 --date_str='2021-11-30'
```

## How it works

Everyday we take all standing MP/CP and create [Merkle Tree](). Resulting [Merkle Root]() is timestamped on Tezos by TzStamp service. We [publish]() Merkle Root on our website and tweet it using [dedicated account]().

Our simple verification interface allows you to generate [audit trail]() and perform verification.

(TODO: copy verification text from report)


notes
we need to recalculate CP to match floating points

```
from all_models import *

questions = Question.objects.filter(type='forecast')

for q in questions:
    q.update_community_prediction()
    q.update_metaculus_prediction()
    q.save(update_fields=["community_prediction", "metaculus_prediction"])
```
