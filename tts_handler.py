# tts_handler.py
import re, uuid
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_NAME, STORAGE_PATH
from elevenlabs.client import ElevenLabs
from utils import save_audio

class TextToSpeech:
    def __init__(self):
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        voices = self.client.voices.search().voices
        matches = [v for v in voices if v.name == ELEVENLABS_VOICE_NAME]
        self.voice_id = matches[0].voice_id if matches else voices[0].voice_id

    def synthesize(self, text: str) -> str:
        # 1) inject natural “…” pauses after fillers
        def repl(m): return m.group(0) + '… '
        filled = re.sub(r"\b(um|uh|you know|like)\b", repl, text,
                        flags=re.IGNORECASE)

        # 2) wrap in SSML to slow it down and add emotional prosody
        ssml = f"""
        <speak>
          <prosody rate="85%" pitch="medium">
            {filled}
          </prosody>
        </speak>
        """

        # 3) generate with expressive stability & similarity boosts
        audio_stream = self.client.text_to_speech.convert(
            text=ssml,
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_22050_32",
            voice_settings={
                "stability": 0.30,        # a bit more dynamic
                "similarity_boost": 0.75  # closer to the chosen voice
            }
        )

        # 4) accumulate bytes and save
        audio_bytes = b"".join(audio_stream)
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        return save_audio(audio_bytes, filename)
