import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from code_graph import create_chat_graph

MONGODB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": "2"}}

def voice_input():
    """
    Capture audio from the microphone, convert to text, and interact with the assistant.
    If the user says 'stop', halt all execution and exit the loop.
    """
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer)
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
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    continue

                # Listen for 'stop' to break out of the loop
                if text.strip().lower() == "stop":
                    print("🛑 Stopping voice assistant as requested.")
                    break

                for event in graph.stream({"messages": [{"role": "user", "content": text}]}, config=config, stream_mode="values"):
                    if "messages" in event:
                        event['messages'][-1].pretty_print()

voice_input()
