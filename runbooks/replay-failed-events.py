import stripe
import os
import subprocess

"""
Purpose: Replay completly failed webhook events

The above should not happen (due to retries)
But if all retries fail, then eventually no more retries
are performed. (Aka do better monitoring/alerting)

See
https://docs.stripe.com/webhooks/process-undelivered-events?locale=en-GB
"""

# Settings
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# All subscribie shops sign-up through the 'master' subscribie shop
# because dogfooding https://en.wikipedia.org/wiki/Eating_your_own_dog_food
SUBSCRIBIE_MASTER_CONNECT_ACCOUNT_ID = os.getenv(
    "SUBSCRIBIE_MASTER_CONNECT_ACCOUNT_ID"
)  # noqa: E501
WEBHOOK_ID = os.getenv("WEBHOOK_ID")  # the endpoint prod webhook router

EVENTS_ENDING_BEFORE_EVENT_ID = os.getenv("EVENTS_ENDING_BEFORE_EVENT_ID")

stripe.api_key = STRIPE_API_KEY

events = stripe.Event.list(
    ending_before=EVENTS_ENDING_BEFORE_EVENT_ID,  # Specify an event ID that was sent just before the webhook endpoint became unavailable. # noqa:E501
    # types=["payment_intent.succeeded", "payment_intent.payment_failed"], # all by default  # noqa: E501
    delivery_success=False,
    stripe_account=SUBSCRIBIE_MASTER_CONNECT_ACCOUNT_ID,
)

for event in events.auto_paging_iter():
    cmd = f"stripe  events resend --live --api-key {STRIPE_API_KEY} --account={SUBSCRIBIE_MASTER_CONNECT_ACCOUNT_ID} {event.id} --webhook-endpoint={WEBHOOK_ID}",  # noqa: E501
    subprocess.run(
        cmd,
        shell=True,
    )
