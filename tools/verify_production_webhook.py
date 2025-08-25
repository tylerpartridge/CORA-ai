import json
import requests

URL = "https://coraai.tech/api/payments/webhook"

# Minimal Stripe-like payload. This will NOT have a valid signature,
# so expect 400/401 if your handler enforces signatures.
payload = {
    "id": "evt_test_webhook",
    "object": "event",
    "type": "payment_intent.succeeded",
    "data": {"object": {"id": "pi_test_12345", "object": "payment_intent", "status": "succeeded"}}
}

headers = {"Content-Type": "application/json"}  # No Stripe-Signature on purpose

resp = requests.post(URL, data=json.dumps(payload), headers=headers)
print("HTTP", resp.status_code)
print(resp.text)
