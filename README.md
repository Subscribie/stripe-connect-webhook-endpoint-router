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

## Debug

Listen for webhooks using stripe cli (forwarding to *this* app)
Also, on another port, run a shop locally on another port (e.g. flask run --port 5001)
Then start the checkout process to generate events.

```
stripe listen --forward-to 127.0.0.1:5000
```
