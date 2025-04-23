import pyttsx3
import speech_recognition as sr

def speak(text, voice_settings):
    """Text-to-speech function"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', voice_settings["rate"])
        engine.setProperty('volume', voice_settings["volume"])
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        return f"❌ TTS Error: {e}"

def listen_for_input():
    """Speech-to-text with error handling"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except Exception as e:
            return f"❌ Error: {e}"
