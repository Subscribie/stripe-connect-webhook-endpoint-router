# Runbooks

## How do I replay failed webhook events?

> Remember Stripe will _automatically_ retries failed events. You only might need this if your alerting is so bad that all automatic webhook event retries exhaust their retries and move from a retying -> failed state from Stripe -> Subscribie's webhook endpoint router.

To replay failed Stripe webhook events. See [replay-failed-events.py](./replay-failed-events.py)

## Setup


```bash

python3 -m venv venv
pip install -r requirements.txt
source ./venv/bin/activate
```

### Configure

```
cp .env.example .env
# populate .env
```

### Run
```
source ./venv/bin/activate
source .env
python replay-failed-events.py
```
