# Recieve connect webhooks from Stripe & forward them to the correct shop


### Install 

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
``` 

## Configure

```
cp .env.example .env
```
## Run (locally)

```
export FLASK_APP=main.py
export FLASK_DEBUG=1
flask run
```

## Deploy

See apache example config & wsgi config example in repo. (assumes mod wsgi is installed & enabled on apache)

## Smoke test

```
curl -H 'Content-Type: application/json' -d '{"account":"-1"}' <host> | grep "No site_url for that account id"
```

## Debug / Local development

Listen for webhooks using stripe cli (forwarding to *this* app)
Also, on another port, run a shop locally on another port (e.g. flask run --port 5001)
Then start the checkout process to generate events.

Listen locally to only the events which need to be processed using stripe cli:
```
stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5001
```
