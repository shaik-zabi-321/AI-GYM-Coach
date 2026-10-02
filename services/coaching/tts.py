from io import BytesIO
from gtts import gTTS


class texttoSpeech:
    def speak(Self, text, lang='en'):
        cleaned = (text or "").strip()
        if not cleaned:
            return None
        buffer = BytesIO()
        gTTS(text=cleaned, lang=lang).write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
