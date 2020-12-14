from flask import Flask, request
import requests
import redis
import os
import stripe
from dotenv import load_dotenv
import logging

load_dotenv(verbose=True)

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_WEBHOOK_PATH = os.environ.get("STRIPE_WEBHOOK_PATH")

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
    redisConn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    try:
        stripe_connect_account_id = request.json["account"]
        # Get shop url from redis via stripe connect account id
        site_url = redisConn.get(stripe_connect_account_id)
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

            headers = request.headers
            resp = requests.post(
                site_url.decode("utf-8") + STRIPE_WEBHOOK_PATH,
                json=event,
                headers=headers,
            )
            # Return (proxying) whatever the site (shop) responds
            # including the return code
            return resp.text, resp.status_code
        else:
            return (
                f"Could not locate site_url for shop using account id\
                  {stripe_connect_account_id}",
                422,
            )
    except Exception as e:
        logging.error("Error processing stripe webhook request")
        logging.error(e)
    return "Invalid request to route_stripe_connect_webhook", 400
