from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal



# AIzaSyA1ZM9TvZNw0ReDDyacsaLIkKD-05Tq5uY

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool


class DetectCallResponse(BaseModel):
    is_coding_question: bool

class CodingAIResponse(BaseModel):
    answer: str



# todo creata routing node that decide if the question is coding or not
def detect_query(state : State)-> State:
    # call gemini mini model to decide id the user question is coding or not

    user_message = state["user_message"]  

    SYSTEM_INSTRUCTION = (
        "You are an AI assistant. Your job is to detect if the user's query is related "
        "to coding question or not. Return the response in specified JSON boolean only. "
        'For example: {"is_coding_question": true} or {"is_coding_question": false}.'
    )  

    client = genai.Client(api_key="AIzaSyA1ZM9TvZNw0ReDDyacsaLIkKD-05Tq5uY")
    contents = [
    types.Content(
        role="user", parts=[types.Part(text=user_message)]
    )
    ]
    generate_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    response_mime_type="application/json",
    response_schema=DetectCallResponse,
)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents= contents,
        config=generate_config
    )
    state["is_coding_question"] = response.parsed.is_coding_question
    return state


def route_edge(state: State)->Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")

    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"


def solve_coding_question(state: State) -> State:
    # Here you would implement the logic to solve coding questions
    user_message = state["user_message"]
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to resolve the user query based on coding 
    problem he is facing
    """
    client = genai.Client(api_key="AIzaSyA1ZM9TvZNw0ReDDyacsaLIkKD-05Tq5uY")
    contents = [
    types.Content(
        role="user", parts=[types.Part(text=user_message)]
        )
    ]
    generate_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    response_mime_type="application/json",
    response_schema=CodingAIResponse,
)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents= contents,
        config=generate_config
    )
    state["ai_message"] = response.parsed.answer
    return state

def solve_simple_question(state: State) -> State:
    # Here you would implement the logic to solve coding questions
    user_message = state["user_message"]
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to chat with user
    """
    client = genai.Client(api_key="AIzaSyA1ZM9TvZNw0ReDDyacsaLIkKD-05Tq5uY")
    contents = [
    types.Content(
        role="user", parts=[types.Part(text=user_message)]
        )
    ]
    generate_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    response_mime_type="application/json",
    response_schema=CodingAIResponse,
)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents= contents,
        config=generate_config
    )
    state["ai_message"] = response.parsed.answer
    return state

# //////////////////////////////////////////////////////////////////

# graph = StateGraph[State]()
graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)

graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()



def main():
    state = {
        "user_message": "write a function to add two numbers",
        "ai_message": "",
        "is_coding_question": True
    }
    # print(detect_query(state))
    result = graph.invoke(state)
    

    print("Final Result", result["ai_message"])
    

main()