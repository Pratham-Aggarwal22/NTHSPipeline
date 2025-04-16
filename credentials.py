# credentials.py
import os

# Google Speech-to-Text API Credentials (point to your JSON key file)
GOOGLE_SPEECH_CREDENTIALS = os.getenv("GOOGLE_SPEECH_CREDENTIALS", "path/to/google_credentials.json")

# Hugging Face API Token (for your LLM integration)
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "your_huggingface_token_here")

# MongoDB URI for database connectivity
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/your_database")

# Get Twilio credentials from environment variables (or add them to credentials.py as needed)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_twilio_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_twilio_auth_token")
TWILIO_CALLER_NUMBER = os.getenv("TWILIO_CALLER_NUMBER", "+10000000000")
# BASE_URL should point to your publicly accessible server (e.g., using ngrok during development)
BASE_URL = os.getenv("BASE_URL", "http://your_public_domain.com")

# Additional imports you might need:
# import pymongo
# from google.cloud import speech
# from transformers import pipeline  # For Hugging Face models
