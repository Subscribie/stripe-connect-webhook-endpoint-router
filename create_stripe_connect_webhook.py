"""
Create initial connect webhook listening only for
the events required.

Returns the endpoint secret, needed for Stripe webhook validation

Note: Stripe livemode is *always* true for Stripe connect. Why?

Because Stripe connect accounts can either be in live or test mode so
the live/test mode config is moved to each Stipe connect account (and
they can change their account to be in live or test mode).
"""

import stripe

stripe_api_key = input("Stripe secret api key:")
endpoint_url = input("Webhook url:")

stripe.api_key = stripe_api_key

webhook = stripe.WebhookEndpoint.create(
    connect=True,
    url=endpoint_url,
    enabled_events=[
        "checkout.session.completed",
        "payment_intent.succeeded",
    ],
)

print(webhook)
