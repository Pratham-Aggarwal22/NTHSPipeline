from google.cloud import speech

class SpeechRecognizer:
    def __init__(self):
        self.client = speech.SpeechClient()
        self.request = {
            'config': {
                'encoding': 'MULAW',
                'sampleRateHertz': 8000,
                'languageCode': 'en-US',
            },
            'interimResults': False
        }

    def stream_recognize(self, audio_buffer, callback):
        # stream audio chunks to Google STT
        stream = self.client.streaming_recognize(self.request)
        for result in stream:
            if not result.results:
                continue
            res = result.results[0]
            if res.is_final:
                text = res.alternatives[0].transcript
                callback(text)
