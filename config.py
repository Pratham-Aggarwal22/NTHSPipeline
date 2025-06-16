# config.py
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load credentials
here = os.path.dirname(__file__)
with open(os.path.join(here, 'credentials.json')) as f:
    creds = json.load(f)

# Twilio
TWILIO_ACCOUNT_SID = creds['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = creds['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = creds.get('TWILIO_PHONE_NUMBER')

# Google
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds['GOOGLE_APPLICATION_CREDENTIALS']

# OpenAI
OPENAI_API_KEY = creds['OPENAI_API_KEY']

# TTS settings: dynamic voice selection and prosody
TTS_VOICE_NAME = creds.get('TTS_VOICE_NAME', 'en-US-Neural2-J')  # richer voice
TTS_RATE = creds.get('TTS_RATE', 0.96)  # slower human pace (90%)
TTS_PITCH = creds.get('TTS_PITCH', 0)  # neutral pitch

# ElevenLabs
ELEVENLABS_API_KEY    = creds['11Labs']                 
ELEVENLABS_VOICE_NAME = creds.get('ELEVENLABS_VOICE_NAME', 'Bella') 
# Optional: specify a particular voice ID instead of using the name
ELEVENLABS_VOICE_ID = creds.get('ELEVENLABS_VOICE_ID', None)



# Storage
STORAGE_PATH = creds.get('STORAGE_PATH', 'audio/')
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)