

import speech_recognition as sr

def voice_input():
    """
    Capture audio input from the microphone and convert it to text.
    """
    # Initialize the recognizer
    recognizer = sr.Recognizer()

        
    with sr.Microphone() as source:
        print("🎙️ Please say something...")

        
        recognizer.adjust_for_ambient_noise(source)

        audio_data = recognizer.listen(source)

        print("🔍 Recognizing...")

        try:
            text = recognizer.recognize_google(audio_data)
            print("📝 You said:", text)
        except sr.UnknownValueError:
            print("Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
