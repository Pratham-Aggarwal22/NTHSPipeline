from openai import OpenAI
from credentials import OPENAI_API_KEY

# OpenAI API key should be set via environment variable or passed explicitly here if needed
client = OpenAI(api_key=OPENAI_API_KEY)  # This uses OPENAI_API_KEY from env

def analyze_response(question_text: str, user_response: str) -> dict:
    validation_prompt = (
        f"Question: {question_text}\n"
        f"Answer: {user_response}\n"
        "Instruction: Is this answer valid and clearly answer the question? "
        "Respond with 'Valid' or 'Invalid'."
    )

    try:
        # Call GPT-4.1-nano for validation
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are a strict survey answer validator. Only respond with 'Valid' or 'Invalid'."},
                {"role": "user", "content": validation_prompt}
            ],
            max_tokens=20,
            temperature=0
        )
        validation_response = response.choices[0].message.content.strip()
        print(f"[LLM Validation Response] {validation_response}")

        if "Valid" in validation_response:
            return {
                "status": "correct",
                "stored_response": user_response
            }

        # If response is not valid, generate a follow-up
        followup_prompt = (
            f"The user was asked: '{question_text}'\n"
            f"Their answer was: '{user_response}', which is unclear.\n"
            "Generate a follow-up question to help clarify their answer."
        )

        followup_response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rewrites vague survey answers into follow-up questions."},
                {"role": "user", "content": followup_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        follow_up = followup_response.choices[0].message.content.strip()
        print(f"[LLM Follow-up Question] {follow_up}")

        return {
            "status": "follow-up",
            "message": follow_up
        }

    except Exception as e:
        print(f"[ERROR] LLM failure: {e}")
        return {
            "status": "error",
            "message": "There was an error validating the response."
        }
