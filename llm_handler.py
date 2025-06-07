# The funtion that reads the repsonse from the speech_handler takes the question from the call_handler (sends the id of question for which the response was generated) and then checks the response

# IF-else condition, if answer is correct, return "Next" to the call_handler and sends the exact answer to be stored to the storage_handler
# if answer is incorrect, generates the follow-up question, sends the "No" to call_handler, sneds the follow-up question to Speech_handler (to covnert from text to speech)


# llm_handler.py

from huggingface_hub import InferenceClient

# Initialize the LLM client
client = InferenceClient(
    provider="fireworks-ai",
    api_key="***********"  # Replace with the api key
)

def analyze_response(question_text: str, user_response: str) -> dict:
    """
    This function takes the user's speech-to-text response and the original question text,
    then uses an LLM to validate the response.

    Workflow:
    - If the answer is valid: return status "correct", and the original answer to store.
    - If the answer is invalid: return status "follow-up", and a new follow-up question.
    """

    # Step 1: Validate the user's answer using an LLM
    validation_prompt = (
        f"Question: {question_text}\n"
        f"Answer: {user_response}\n"
        "Instruction: Is this answer valid and clearly answer the question? "
        "Respond with 'Valid' or 'Invalid'."
    )

    validation_response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3-0324",
        messages=[{"role": "user", "content": validation_prompt}],
        max_tokens=100,
    ).choices[0].message.content.strip()

    print(f"[LLM Validation Response] {validation_response}")

    # Step 2: If valid, return to call_handler to move to next question
    if "Valid" in validation_response:
        return {
            "status": "correct",
            "stored_response": user_response
        }

    # Step 3: If invalid, generate follow-up question for clarification
    followup_prompt = (
        f"The user was asked: '{question_text}'\n"
        f"Their answer was: '{user_response}', which seems invalid or unclear.\n"
        "Generate a follow-up question that will help clarify or correct their response."
    )

    follow_up = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3-0324",
        messages=[{"role": "user", "content": followup_prompt}],
        max_tokens=100,
    ).choices[0].message.content.strip()

    print(f"[LLM Follow-up Question] {follow_up}")

    return {
        "status": "follow-up",
        "message": follow_up
    }
