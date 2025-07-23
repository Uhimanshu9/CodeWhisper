import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from code_graph import create_chat_graph

MONGODB_URI = "mongodb://admin:admin@localhost:27017"
config ={"configurable":{"thread_id":"1"}}


def voice_input():
    """
    Capture audio input from the microphone and convert it to text.
    """
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer)
    # Initialize the recognizer
        recognizer = sr.Recognizer()

        
        with sr.Microphone() as source:
            

            
            recognizer.adjust_for_ambient_noise(source)
            recognizer.pause_threshold = 2

            while True:
                print("🎙️ Please say something...")

                audio_data = recognizer.listen(source)

                print("🔍 Recognizing...")

                try:
                    text = recognizer.recognize_google(audio_data)
                    print("📝 You said:", text)
                except sr.UnknownValueError:
                    print("Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                
                for event in graph.stream({"messages": [{"role": "user", "content": text}]}, config=config , stream_mode= "values" ):
                    if "messages" in event:
                        event['messages'][-1].pretty_print()

voice_input()