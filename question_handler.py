# question_handler.py

"""
Question Handler Module

This module holds 12 questions for the call workflow. Each question is defined with an ID (Q1 to Q12).
Fill in the actual question text later.
"""

QUESTIONS = {
    "Q1": "",   # TODO: Enter question text for Q1
    "Q2": "",   # TODO: Enter question text for Q2
    "Q3": "",   # TODO: Enter question text for Q3
    "Q4": "",   # TODO: Enter question text for Q4
    "Q5": "",   # TODO: Enter question text for Q5
    "Q6": "",   # TODO: Enter question text for Q6
    "Q7": "",   # TODO: Enter question text for Q7
    "Q8": "",   # TODO: Enter question text for Q8
    "Q9": "",   # TODO: Enter question text for Q9
    "Q10": "",  # TODO: Enter question text for Q10
    "Q11": "",  # TODO: Enter question text for Q11
    "Q12": ""   # TODO: Enter question text for Q12
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
