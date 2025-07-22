from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = init_chat_model("google_genai:gemini-2.0-flash")
def chatbot(state: State):
    messages = state["messages"]
    response = llm.invoke(messages)
    state["messages"].append(response)
    return state


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# graph = graph_builder.compile()

def graph(checkpointer=None):
    if checkpointer is None:
        return graph_builder.compile()
    else:
        return graph_builder.compile(checkpointer)
# graph = graph(checkpointer=checkpoint_saver)
