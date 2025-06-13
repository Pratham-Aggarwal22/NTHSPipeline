# question_handler.py

"""
Question Handler Module

This module holds 3 sample questions for testing the call workflow.
Each question is defined with an ID (Q1 to Q3).
"""

QUESTIONS = {
    "Q1": "Do you own a vehicle?",
    "Q2": "What is the make or brand of your vehicle?",
    "Q3": "What is the manufacturing year of your vehicle?"
}

def get_question(question_id: str) -> str:
    """
    Retrieve the question text for the given question ID.
    
    Parameters:
      - question_id (str): e.g., "Q1", "Q2", etc.
      
    Returns:
      - str: The corresponding question text.
    """
    return QUESTIONS.get(question_id, "No question found for this ID.")
