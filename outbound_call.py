# outbound_call.py

import sys
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

if len(sys.argv) != 2:
    print("Usage: python outbound_call.py +1RECIPIENT_NUMBER")
    sys.exit(1)

to_number = sys.argv[1]

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

call = client.calls.create(
    to=to_number,
    from_=TWILIO_PHONE_NUMBER,
    # this must be reachable (ngrok or your deployed URL)
    url= "https://98d7-129-8-223-193.ngrok-free.app/voice"
)

print(f"✅ Outbound call initiated, Call SID: {call.sid}")
