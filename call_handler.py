# call_handler.py
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os

# Import modules from other files
import question_handler  # for get_question()
from speech_handler import speech_to_text  # for converting audio to text
import llm_handler     # for analyze_response()
import storage_handler # for save_response()
from credentials import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_CALLER_NUMBER, BASE_URL

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
app = Flask(__name__)

@app.route("/initiate_call", methods=["POST"])
def initiate_call():
    """
    Function: Initiates a phone call to the user
    
    What it does:
    - Takes a phone number from the POST request
    - Starts a Twilio call to that number
    - Directs the call to begin with greetings
    
    Parameters expected:
    - phone_number: The phone number to call (from POST form data)
    
    Returns:
    - JSON response with call status and call SID
    """
    phone_number = request.form.get("phone_number")
    
    # Create the call using Twilio
    call = client.calls.create(
        to=phone_number,
        from_=TWILIO_CALLER_NUMBER,
        url=f"{BASE_URL}/start_call"  # Start with greetings
    )
    
    return {"status": "calling", "call_sid": call.sid}

@app.route("/start_call", methods=["GET", "POST"])
def start_call():
    """
    Function: Handles the initial call greeting
    
    What it does:
    - Plays a greeting message when the call connects
    - Redirects to ask the first question (Q1)
    
    Parameters expected:
    - CallSid: Automatically provided by Twilio
    
    Returns:
    - TwiML response with greeting and redirect to first question
    """
    resp = VoiceResponse()
    
    # Greeting message
    greeting = "Hello! Thank you for taking our survey. We have a few questions for you. Let's begin."
    resp.say(greeting)
    
    # Redirect to first question
    resp.redirect(f"{BASE_URL}/ask_question?question_id=Q1", method="GET")
    
    return Response(str(resp), mimetype="text/xml")

@app.route("/ask_question", methods=["GET", "POST"])
def ask_question():
    """
    Function: Asks a specific question to the user
    
    What it does:
    - Gets the question ID from URL parameters
    - Retrieves the question text from question_handler
    - Speaks the question to the user
    - Records the user's response
    
    Parameters expected:
    - question_id: The ID of the question to ask (Q1, Q2, etc.)
    - CallSid: Automatically provided by Twilio
    
    Returns:
    - TwiML response that speaks the question and records the answer
    """
    question_id = request.args.get("question_id", "Q1")
    call_sid = request.values.get("CallSid", "")
    
    # Get the question text from question handler
    question_text = question_handler.get_question(question_id)
    
    # Check if we've reached the end
    if question_id == "end":
        resp = VoiceResponse()
        resp.say("Thank you for completing our survey. Have a great day!")
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")
    
    # Create TwiML response
    resp = VoiceResponse()
    resp.say(question_text)
    
    # Record the user's response
    resp.record(
        action=f"{BASE_URL}/process_answer?question_id={question_id}",
        method="POST",
        max_length=30,  # Allow up to 30 seconds for response
        play_beep=True,
        timeout=5  # Wait 5 seconds of silence before stopping
    )
    
    return Response(str(resp), mimetype="text/xml")

@app.route("/process_answer", methods=["POST"])
def process_answer():
    """
    Function: Processes the user's recorded answer
    
    What it does:
    - Downloads the recorded audio from Twilio
    - Converts audio to text using speech_handler
    - Sends question and answer to LLM for verification
    - Based on LLM response, either moves to next question or asks follow-up
    
    Parameters expected:
    - question_id: The ID of the question that was answered
    - CallSid: Automatically provided by Twilio
    - RecordingUrl: URL of the recorded audio (provided by Twilio)
    
    Returns:
    - TwiML response that either asks next question or follow-up question
    """
    question_id = request.args.get("question_id", "Q1")
    call_sid = request.values.get("CallSid", "")
    recording_url = request.values.get("RecordingUrl")
    
    # Download the recorded audio from Twilio
    audio_url = recording_url + ".wav"  # Twilio recordings need .wav extension
    audio_response = requests.get(audio_url)
    audio_data = audio_response.content
    
    # Convert audio to text using speech handler
    user_response_text = speech_to_text(audio_data)
    print(f"[DEBUG] User said: {user_response_text}")
    
    # Get the original question text
    question_text = question_handler.get_question(question_id)
    
    # Send to LLM handler for verification
    llm_analysis = llm_handler.analyze_response(question_text, user_response_text)
    print(f"[DEBUG] LLM analysis: {llm_analysis}")
    
    # Process LLM response
    if llm_analysis.get("status") == "correct":
        # Answer is correct - save to database and move to next question
        storage_handler.save_response(call_sid, question_id, llm_analysis.get("stored_response", user_response_text))
        
        # Get next question ID
        next_question_id = get_next_question_id(question_id)
        
        # Redirect to next question
        resp = VoiceResponse()
        resp.redirect(f"{BASE_URL}/ask_question?question_id={next_question_id}", method="GET")
        return Response(str(resp), mimetype="text/xml")
    
    else:
        # Answer needs clarification - ask follow-up question
        follow_up_message = llm_analysis.get("message", "I didn't understand your answer. Could you please repeat it?")
        
        resp = VoiceResponse()
        resp.say(follow_up_message)
        
        # Record the response again for the same question
        resp.record(
            action=f"{BASE_URL}/process_answer?question_id={question_id}",
            method="POST",
            max_length=30,
            play_beep=True,
            timeout=5
        )
        
        return Response(str(resp), mimetype="text/xml")

def get_next_question_id(current_question_id: str) -> str:
    """
    Function: Determines the next question ID in sequence
    
    What it does:
    - Takes the current question ID (like "Q1")
    - Returns the next question ID (like "Q2")
    - Returns "end" if all questions are completed
    
    Parameters expected:
    - current_question_id: Current question ID (string like "Q1", "Q2", etc.)
    
    Returns:
    - Next question ID (string) or "end" if survey is complete
    """
    try:
        # Extract number from question ID (Q1 -> 1, Q2 -> 2, etc.)
        current_number = int(current_question_id.replace("Q", ""))
        next_number = current_number + 1
        
        # Check if we've completed all 12 questions
        if next_number > 12:
            return "end"
        
        return f"Q{next_number}"
    
    except (ValueError, AttributeError):
        # If there's an error parsing, default to Q1
        print(f"[ERROR] Could not parse question ID: {current_question_id}")
        return "Q1"

if __name__ == "__main__":
    """
    Function: Runs the Flask application
    
    What it does:
    - Starts the web server on port 5000
    - Makes it accessible from any IP address
    - Enables debug mode for development
    """
    app.run(host="0.0.0.0", port=5000, debug=True)