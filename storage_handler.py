# storage_handler.py

"""
Storage Handler Module

This module manages saving of call responses to a MongoDB database.
It should:
  - Connect to MongoDB using MONGODB_URI.
  - Provide a function to store the final user response, along with metadata like call id and question id.
"""

def save_response(call_id: str, question_id: str, response_text: str):
    # TODO: Implement the database insertion logic.
    # Steps:
    #   1. Connect to MongoDB using the MONGODB_URI from credentials.py.
    #   2. Insert a document with:
    #       - call_id: Unique call identifier.
    #       - question_id: e.g., "Q1", "Q2", etc.
    #       - response_text: The final text that needs to be stored.
    pass
