# credentials.py
import os

# Google Speech-to-Text API Credentials (point to your JSON key file)
GOOGLE_SPEECH_CREDENTIALS = os.getenv("GOOGLE_SPEECH_CREDENTIALS", "json file here")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "**********")

# MongoDB URI for database connectivity
MONGODB_URI = os.getenv("MONGODB_URI", "mongo url here")

# Get Twilio credentials from environment variables (or add them to credentials.py as needed)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "*****")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "*****")
TWILIO_CALLER_NUMBER = os.getenv("TWILIO_CALLER_NUMBER", "+1234567890")  # Replace with your Twilio number

# BASE_URL should point to your publicly accessible server (e.g., using ngrok during development)
BASE_URL = os.getenv("BASE_URL", "base url here")

# Additional imports you might need:
# import pymongo
# from google.cloud import speech
# from transformers import pipeline  # For Hugging Face models
