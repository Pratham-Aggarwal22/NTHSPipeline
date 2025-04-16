# speech_handler.py
import io
from google.cloud import speech
from credentials import GOOGLE_SPEECH_CREDENTIALS

def speech_to_text(audio_data: bytes) -> str:
    """
    Convert the provided audio_data (in bytes) to text using Google Speech-to-Text.
    
    Steps:
      1. Create a SpeechClient instance using the service account file.
      2. Configure the recognition settings (encoding, sample rate, language, etc.).
      3. Call the recognize method with the audio data.
      4. Return the transcript from the first (or best) result.
    """
    # Create a SpeechClient using the provided credentials
    client = speech.SpeechClient.from_service_account_file(GOOGLE_SPEECH_CREDENTIALS)
    
    # Prepare the audio data for the API
    audio = speech.RecognitionAudio(content=audio_data)
    
    # Set up recognition configuration. (Adjust these parameters as needed.)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US"
    )
    
    # Make the API call to transcribe the audio.
    response = client.recognize(config=config, audio=audio)
    
    # Return the transcript of the first result if available.
    if response.results:
        transcript = response.results[0].alternatives[0].transcript
        return transcript
    else:
        return ""
