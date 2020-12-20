"""
Create initial connect webhook listening only for
the events required.

Returns the endpoint secret, needed for Stripe webhook validation
"""

import stripe

stripe_api_key = input("Stripe api key:")
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
