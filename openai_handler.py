# openai_handler.py
import openai
from config import OPENAI_API_KEY

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# System prompt defines the assistant's behavior:
SYSTEM_PROMPT = (
    "You are a friendly travel survey assistant talking casually like a human friend."
    " Use simple English, contractions, and occasional filler words (um, uh)."
    " When given the survey question and the user's answer:"  
    " - If the answer fully addresses the question, reply with a brief, warm affirmation that mentions"
    " the user's response."
    " - If the user opts out or has no preference, say 'No problem, let's move on.'"
    " - If the answer is unclear or missing details, ask one clear follow-up question."
    " Do not ask any other questions or generate the next survey question."
)

class OpenAIConversation:
    def __init__(self):
        # Begin with the system prompt
        self.history = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    def user_message(self, text: str):
        # Append the user's question or answer
        self.history.append({'role': 'user', 'content': text})

    def get_response(self) -> str:
        # Stream the response to reduce latency
        response_stream = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=self.history,
            temperature=0.7,
            max_tokens=50,
            top_p=0.9,
            stream=True
        )
        reply = ""
        for chunk in response_stream:
            delta = chunk.choices[0].delta.get('content', '')
            if delta:
                reply += delta
        reply = reply.strip()
        # Save assistant reply in history
        self.history.append({'role': 'assistant', 'content': reply})
        return reply
