from flask import Flask, request, Response
import requests
import redis
import os
import stripe
from dotenv import load_dotenv
import logging

load_dotenv(verbose=True)

PYTHON_LOG_LEVEL = os.environ.get("PYTHON_LOG_LEVEL", "WARNING")

REDIS_HOSTNAME = os.environ.get("REDIS_HOSTNAME")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_TIMEOUT_SECS = int(os.environ.get("REDIS_TIMEOUT_SECS"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_WEBHOOK_PATH = os.environ.get("STRIPE_WEBHOOK_PATH")

print(f"PYTHON_LOG_LEVEL is: {PYTHON_LOG_LEVEL}")

logging.basicConfig(level=PYTHON_LOG_LEVEL)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def route_stripe_connect_webhook():
    """Recieve stripe connect webhook & route to shop based on account id
    Looks up shop address via redis using account_id as key.

    - Sends to webhook to the correct stop
    - Returns status code & response body from shop
      - (Only returns 200 if the shop returns 200, otherwise return 400)
    """

    load_dotenv(verbose=True)
    redisConn = redis.Redis(
        host=REDIS_HOSTNAME,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        socket_timeout=REDIS_TIMEOUT_SECS,  # noqa E501
    )
    try:
        stripe_connect_account_id = request.json["account"]
    except KeyError as e:
        logging.error(e)
        msg = f"Not a connect request.\
              No 'account' property in payload\n\n{request.json}"
        logging.error(msg)
        return msg, 422
    try:
        stripe_connect_account_id = request.json["account"]

        # Get shop url from redis via stripe connect account id
        site_url = redisConn.get(stripe_connect_account_id)
        logging.debug(f"Routing for account: {stripe_connect_account_id}")
        logging.debug(f"Will be routing webhook to: {site_url}")

        if site_url is not None:
            # Verify stripe signature header
            # Proxy stripe webhook to site_url (the shop)
            # and await response code
            # then forward response code and body back to stripe
            sig_header = request.headers.get("Stripe-Signature", None)
            event = None
            try:
                event = stripe.Webhook.construct_event(
                    request.data, sig_header, STRIPE_WEBHOOK_SECRET
                )
            except ValueError as e:
                logging.error(
                    "ValueError when attempting to get Stripe-Signature header"
                )
                logging.error(e)
                return e, 400
            except stripe.error.SignatureVerificationError as e:
                logging.error("Stripe SignatureVerificationError")
                logging.error(e)
                return "Stripe SignatureVerificationError", 400

            post_url = site_url.decode("utf-8") + STRIPE_WEBHOOK_PATH
            logging.debug(f"Posting webhook to: {post_url}")

            resp = requests.post(
                post_url,
                json=event,
            )
            # Return (proxying) whatever the site (shop) responds
            # including the return code
            logging.debug(f"{resp.status_code}, {resp.text}")
            return resp.text, resp.status_code
        else:
            msg = f"{{'msg': 'No site_url for that account id', \
'account id': {stripe_connect_account_id}'}}"

            logging.error(msg)
            return Response(msg, status=500, mimetype="application/json")

    except redis.exceptions.ResponseError as e:
        logging.error("Redis ResponseError")
        logging.error(e)
    except redis.exceptions.ConnectionError as e:
        logging.error("Redis ConnectionError")
        logging.error(e)
    except redis.exceptions.TimeoutError as e:
        logging.error("Redis timeout")
        logging.error(e)
    except Exception as e:
        logging.error("Error processing stripe webhook request")
        logging.error(e)
    return "Invalid request to route_stripe_connect_webhook", 400
