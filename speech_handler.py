# speech_handler.py
import io
from google.cloud import speech
from credentials import GOOGLE_SPEECH_CREDENTIALS

def speech_to_text(audio_data: bytes) -> str:
    """
    Convert the provided audio_data (in bytes) to text using Google Speech-to-Text.
    
    Parameters:
        - audio_data (bytes): Raw WAV audio bytes from Twilio recording (.wav format).
    
    Returns:
        - str: Transcribed text or empty string if transcription fails.
    """
    try:
        # Create a SpeechClient using the service account credentials file
        client = speech.SpeechClient.from_service_account_file(GOOGLE_SPEECH_CREDENTIALS)
        
        # Prepare the audio data for the API
        audio = speech.RecognitionAudio(content=audio_data)
        
        # Set up recognition configuration
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=8000,  # Twilio default call sample rate
            language_code="en-US",
            audio_channel_count=1,  # Twilio records in mono
            enable_automatic_punctuation=True
        )
        
        # Perform the speech-to-text transcription
        response = client.recognize(config=config, audio=audio)
        
        if response.results:
            transcript = response.results[0].alternatives[0].transcript.strip()
            print(f"[DEBUG] Transcription: {transcript}")
            return transcript
        else:
            return ""
        
    except Exception as e:
        print(f"Speech recognition failed: {e}")
        return ""
