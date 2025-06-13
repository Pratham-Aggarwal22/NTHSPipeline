"""
Storage Handler Module

This module manages saving of call responses to a MongoDB database.
"""

from pymongo import MongoClient
from credentials import MONGODB_URI  

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client["nhts_survey"]            # Use the correct database
collection = db["responses"]          # Target collection for responses

def save_response(call_id: str, question_id: str, response_text: str):
    """
    Save a user response to the database.

    Parameters:
      - call_id (str): Unique Twilio call session identifier.
      - question_id (str): Question identifier (e.g., Q1, Q2).
      - response_text (str): Transcribed user response.
    """
    try:
        document = {
            "call_id": call_id,
            "question_id": question_id,
            "response": response_text
        }
        collection.insert_one(document)
        print(f"[DB] Successfully saved: {document}")
    except Exception as e:
        print(f"[DB Error] Failed to store response: {e}")
