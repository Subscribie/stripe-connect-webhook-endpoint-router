import stripe
import os
import subprocess

"""
Purpose: Replay completely failed (all retried exhausted) webhook events.

The above should not happen (due to retries- remember Stripe
automatically retries webhook event sends to the registered webhook
- but not forever!

If **all** retries fail, then eventually no more retries
are performed. (Aka do better monitoring/alerting)

USAGE:

# setup
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# Configure .env / or export for:
# STRIPE_API_KEY
# WEBHOOK_ID

# run
. venv/bin/activate
python3 replay-failed-events.py

See also
https://docs.stripe.com/webhooks/process-undelivered-events?locale=en-GB
Why can't we simply get all events accross platform accounts without iterating stripe
account ids?
Answer: Product gap: https://insiders.stripe.dev/t/api-to-fetch-all-events-across-connected-accounts/471
"""

from dotenv import load_dotenv

load_dotenv(verbose=True)  # take environment variables

# Settings
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# Each webhook event at the webhook events delivery page (insert link here)
# needs to extract the account id of the event from that failed webhook- it changes based on the shop it pertains to.
# Solution
# 1. List all connected accounts
# 2. For each connected account, list all their events
# 3. Iterate over all their events, if pending_webhooks > 0
#    then replay the event

WEBHOOK_ID = os.getenv("WEBHOOK_ID")  # the endpoint prod webhook router
stripe.api_key = STRIPE_API_KEY


print("Finding connect accounts")
for connect_account in stripe.Account.list().auto_paging_iter():
    # (Guard) Only process express account types
    if connect_account.type != "express":
        continue
    if connect_account.charges_enabled != True:
        continue
    print(f"Processing account id: {connect_account.id}")
    print(f"Processing account name: {connect_account.company['name']}")
    # Get events for this connect account,
    # Identify unsuccessfully delivered events to webhook(s)
    # https://docs.stripe.com/webhooks/process-undelivered-events?locale=en-GB#list-events
    for event in stripe.Event.list(stripe_account=connect_account.id, delivery_success=False).auto_paging_iter():
        print(f"Identified unsuccessfully delivered event: {event.id} for shop {connect_account.id}")
        print(f"Resending the event {event.id} for account {connect_account.id}, {connect_account.company['name']}")
        redrive_command = f"stripe  events resend --live --api-key {STRIPE_API_KEY} --account={connect_account.id} {event.id} --webhook-endpoint={WEBHOOK_ID}",  # noqa: E501
        print(f"Running: {redrive_command}")
        subprocess.run(redrive_command, shell=True)

