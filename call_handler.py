# call_handler.py
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os

# Import modules from other files
import question_handler  # for get_question()
from speech_handler import speech_to_text  # full implementation provided above
import llm_handler     # for analyze_response() [stub with comments]
import storage_handler # for save_response() [stub with comments]



client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
app = Flask(__name__)

@app.route("/initiate_call", methods=["POST"])
def initiate_call():
    """
    Initiates a phone call to the given number.
    
    - Retrieves the phone number from POST data.
    - Initiates the call via Twilio.
    - The call starts with question Q1 (retrieved via Question Handler).
    
    Called from your external service or manually for testing.
    """
    phone_number = request.form.get("phone_number")
    call = client.calls.create(
        to=phone_number,
        from_=TWILIO_CALLER_NUMBER,
        url=f"{BASE_URL}/ask_question?question_id=Q1"  # Start with question Q1
    )
    return {"status": "calling", "call_sid": call.sid}

@app.route("/ask_question", methods=["GET", "POST"])
def ask_question():
    """
    Endpoint used by Twilio to get instructions (Twiml) to ask a question.
    
    Workflow:
    - Retrieves the current question ID from the query parameters.
    - Gets the question text from the Question Handler.
    - Uses text-to-speech (<Say>) to ask the question.
    - Records the user's answer (<Record>), then sends it to /process_answer.
    """
    question_id = request.args.get("question_id", "Q1")
    call_sid = request.values.get("CallSid", "")
    
    # Retrieve question text from Question Handler.
    question_text = question_handler.get_question(question_id)
    
    resp = VoiceResponse()
    resp.say(question_text)
    
    # Record the response, then POST the recording to /process_answer.
    resp.record(
        action=f"{BASE_URL}/process_answer?question_id={question_id}",
        method="POST",
        max_length=10,  # adjust maximum length of the response as needed
        play_beep=True
    )
    
    return Response(str(resp), mimetype="text/xml")

@app.route("/process_answer", methods=["POST"])
def process_answer():
    """
    Processes the recorded answer from Twilio.
    
    Steps:
    1. Download the recorded audio using the Recording URL provided by Twilio.
    2. Use Speech Handler (speech_to_text) to convert audio to text.
    3. Retrieve the current question text from the Question Handler.
    4. Call LLM Handler (analyze_response) with the question and transcribed answer.
       - If the LLM returns a 'correct' status:  
             • Save the final answer via the Storage Handler.
             • Instruct the Call Handler to ask the next question.
       - If the LLM returns a 'follow-up' status:
             • Play the follow-up message and record the response again.
    """
    question_id = request.args.get("question_id", "Q1")
    call_sid = request.values.get("CallSid", "")
    recording_url = request.values.get("RecordingUrl")
    
    # Twilio's RecordingUrl does not include a file extension; append .wav for compatibility.
    audio_url = recording_url + ".wav"
    
    # Download audio data from Twilio
    r = requests.get(audio_url)
    audio_data = r.content
    
    # 1. Speech Handler: Convert the audio to text.
    transcribed_text = speech_to_text(audio_data)
    
    # 2. Retrieve question text for context.
    question_text = question_handler.get_question(question_id)
    
    # 3. LLM Handler: Analyze the user response together with the current question.
    analysis = llm_handler.analyze_response(question_text, transcribed_text)
    
    # 4. Process LLM analysis:
    if analysis.get("status") == "correct":
        # If response is correct, save the final response via Storage Handler.
        storage_handler.save_response(call_sid, question_id, analysis.get("stored_response", transcribed_text))
        
        # Determine the next question.
        next_question_id = get_next_question_id(question_id)
        
        # Redirect the call flow to the next question.
        resp = VoiceResponse()
        resp.redirect(f"{BASE_URL}/ask_question?question_id={next_question_id}", method="GET")
        return Response(str(resp), mimetype="text/xml")
    else:
        # If a follow-up is needed, use the follow-up message from LLM Handler.
        follow_up_message = analysis.get("message", "Please repeat your answer.")
        resp = VoiceResponse()
        resp.say(follow_up_message)
        resp.record(
            action=f"{BASE_URL}/process_answer?question_id={question_id}",
            method="POST",
            max_length=10,
            play_beep=True
        )
        return Response(str(resp), mimetype="text/xml")

def get_next_question_id(current_question_id: str) -> str:
    """
    Helper function to calculate the next question id.
    For example, if current_question_id is "Q1", return "Q2", and so on until "Q12".
    If there are no more questions, you could return a special id (e.g., "end").
    """
    try:
        number = int(current_question_id.strip("Q"))
        next_number = number + 1
        if next_number > 12:
            return "end"  # End-of-call signal (handle as desired)
        return f"Q{next_number}"
    except Exception as e:
        # If unable to determine next id, default to Q1.
        return "Q1"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
