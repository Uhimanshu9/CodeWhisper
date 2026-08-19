import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from code_graph import create_chat_graph
from terminal_ui import print_ai_message, print_banner, print_error, print_status, prompt

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
                print_status("Listening for your command...")
                audio_data = recognizer.listen(source)
                print_status("Recognizing speech...")

                try:
                    text = recognizer.recognize_google(audio_data)
                    print_status(f"You said: {text}")
                except sr.UnknownValueError:
                    print_error("Speech recognition could not understand the audio.")
                    continue
                except sr.RequestError as e:
                    print_error(f"Speech recognition request failed: {e}")
                    continue

                # Listen for 'stop' to break out of the loop
                if text.strip().lower() == "stop":
                    print("🛑 Stopping voice assistant as requested.")
                    break

                for event in graph.stream({"messages": [{"role": "user", "content": text}]}, config=config, stream_mode="values"):
                    if "messages" in event:
                        last_message = event["messages"][-1]
                        if last_message.type == "ai":
                            print_ai_message(last_message)


def text_input():
    """
    Capture text from the keyboard and interact with the assistant.
    If the user types 'stop', halt all execution and exit the loop.
    """
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer)

        while True:
            text = prompt()

            # Listen for 'stop' to break out of the loop
            if text.strip().lower() == "stop":
                print_status("Stopping text assistant as requested.")
                break

            for event in graph.stream({"messages": [{"role": "user", "content": text}]}, config=config, stream_mode="values"):
                # if "messages" in event:
                #     event['messages'][-1].pretty_print()
                if "messages" in event:
                    last_message = event["messages"][-1]
                    if last_message.type == "ai":
                        print_ai_message(last_message)

if __name__ == "__main__":
    print_banner()
    try:
        # voice_input() can be enabled here when microphone mode is desired.
        text_input()
    except (EOFError, KeyboardInterrupt):
        print()
        print_status("Session ended.")

