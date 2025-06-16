# main.py
import os
import requests
from flask import Flask, request, Response, url_for, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from speech_handler import SpeechRecognizer
from tts_handler import TextToSpeech
from openai_handler import OpenAIConversation
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, STORAGE_PATH

app = Flask(__name__)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Predefined survey questions
static_questions = [
    "Hi! thanks for joining. First, where are you traveling to?",
    "When will you be traveling?",
    "Who are you traveling with?",
    "What's your top priority for this trip?",
    "Any special requirements or questions for us?"
]

# In-memory state per call
# call_sid -> { 'q_index': int, 'ai': OpenAIConversation, 'tts': TextToSpeech, 'no_count': int }
conversations = {}
NO_RESPONSES = {'no', 'nothing', 'nope', 'n/a', 'none'}

@app.route('/voice', methods=['POST'])
def voice():
    call_sid = request.form.get('CallSid')
    # Initialize state for this call
    conversations[call_sid] = {
        'q_index': 0,
        'ai': OpenAIConversation(),
        'tts': TextToSpeech(),
        'no_count': 0
    }
    conv = conversations[call_sid]

    # Synthesize and play the first question
    question = static_questions[0]
    audio_file = conv['tts'].synthesize(question)
    audio_url = url_for('serve_audio', filename=os.path.basename(audio_file), _external=True)

    resp = VoiceResponse()
    # Start recording via REST API (no beep)
    try:
        client.calls(call_sid).recordings.create(
            recording_channels='dual',
            recording_status_callback=url_for('recording_callback', _external=True),
            recording_status_callback_event=['completed']
        )
    except Exception as e:
        app.logger.warning(f"Recording API error: {e}")

    # Play question and open Gather for responses
    gather = Gather(input='speech', action='/gather', method='POST', speech_timeout='auto')
    gather.play(audio_url)
    resp.append(gather)
    # If no input, repeat the same question
    resp.redirect('/voice')

    return Response(str(resp), mimetype='text/xml')

@app.route('/gather', methods=['POST'])
def gather():
    call_sid = request.form.get('CallSid')
    conv = conversations.get(call_sid)
    if not conv:
        return Response(status=400)

    user_answer = request.form.get('SpeechResult', '').strip()
    q_idx = conv['q_index']
    print(f"Q{q_idx}: {static_questions[q_idx]}")
    print(f"A: {user_answer}")

    # Handle simple 'no' responses
    if user_answer.lower() in NO_RESPONSES:
        conv['no_count'] += 1
        # First 'no': skip without commentary
        if conv['no_count'] < 2:
            conv['q_index'] += 1
            return ask_question(call_sid)
        # Second 'no': give brief acknowledgement
        conv['no_count'] = 0
        reply = "Alright, no worries."
        conv['q_index'] += 1
        return ask_affirmation(call_sid, reply)

    # Reset no_count on normal answer
    conv['no_count'] = 0
    # LLM processes the answer for clarification or affirmation
    conv['ai'].user_message(static_questions[q_idx])
    conv['ai'].user_message(user_answer)
    reply = conv['ai'].get_response()
    print(f"LLM reply: {reply}")

    # If clarification needed (question mark), repeat same index
    if reply.endswith('?'):
        return ask_followup(call_sid, reply)

    # Affirmation and move to next question
    conv['q_index'] += 1
    # If more questions remain
    if conv['q_index'] < len(static_questions):
        return ask_affirmation(call_sid, reply)

    # Finally, play closing reply and hang up
    audio_file = conv['tts'].synthesize(reply)
    audio_url = url_for('serve_audio', filename=os.path.basename(audio_file), _external=True)
    resp = VoiceResponse()
    resp.play(audio_url)
    resp.say("Thanks for your time!", voice='alice')
    resp.hangup()
    return Response(str(resp), mimetype='text/xml')

# Helpers

def ask_question(call_sid):
    conv = conversations[call_sid]
    question = static_questions[conv['q_index']]
    audio_file = conv['tts'].synthesize(question)
    audio_url = url_for('serve_audio', filename=os.path.basename(audio_file), _external=True)

    resp = VoiceResponse()
    gather = Gather(input='speech', action='/gather', method='POST', speech_timeout='auto')
    gather.play(audio_url)
    resp.append(gather)
    resp.redirect('/voice')
    return Response(str(resp), mimetype='text/xml')

def ask_followup(call_sid, text):
    conv = conversations[call_sid]
    audio_file = conv['tts'].synthesize(text)
    audio_url = url_for('serve_audio', filename=os.path.basename(audio_file), _external=True)

    resp = VoiceResponse()
    gather = Gather(input='speech', action='/gather', method='POST', speech_timeout='auto')
    gather.play(audio_url)
    resp.append(gather)
    resp.redirect('/voice')
    return Response(str(resp), mimetype='text/xml')

def ask_affirmation(call_sid, affirmation):
    conv = conversations[call_sid]
    next_q = static_questions[conv['q_index']]
    combined = f"{affirmation} <break time='300ms'/> {next_q}"
    audio_file = conv['tts'].synthesize(combined)
    audio_url = url_for('serve_audio', filename=os.path.basename(audio_file), _external=True)

    resp = VoiceResponse()
    gather = Gather(input='speech', action='/gather', method='POST', speech_timeout='auto')
    gather.play(audio_url)
    resp.append(gather)
    resp.redirect('/voice')
    return Response(str(resp), mimetype='text/xml')

# Serve audio files
@app.route(f'/{STORAGE_PATH}<path:filename>')
def serve_audio(filename):
    return send_from_directory(os.path.join(os.getcwd(), STORAGE_PATH), filename)

# Recording callback accepts both GET and POST
@app.route('/recording', methods=['GET','POST'])
def recording_callback():
    """Downloads the completed call recording securely using Twilio credentials."""
    sid = request.values.get('RecordingSid')
    # Build the MP3 URL for the recording
    recording_url = request.values.get('RecordingUrl') + '.mp3'
    os.makedirs('recordings', exist_ok=True)
    # Authenticate when fetching the recording file
    response = requests.get(
        recording_url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    if response.status_code == 200:
        file_path = f"recordings/trial 1 - {sid}.mp3"
        with open(file_path, 'wb') as f:
            f.write(response.content)
        app.logger.info(f"Recording saved: {file_path}")
    else:
        app.logger.error(
            f"Failed to download recording {sid}: {response.status_code} {response.text}"
        )
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    app.run(host='0.0.0.0', port=5000)
