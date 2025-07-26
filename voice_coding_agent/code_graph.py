import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain.schema import SystemMessage
from tools.run_command import run_command_with_confirmation
from tools.list_processes import list_processes
from tools.push_to_github import push_to_github
from tools.search_in_files import search_in_files
from tools.show_python_docs import show_python_docs

class State(TypedDict):
    messages: Annotated[list, add_messages]


tools=[
        run_command_with_confirmation , 
        list_processes ,
        push_to_github , 
        search_in_files ,
        show_python_docs
        ]

llm = init_chat_model("google_genai:gemini-2.0-flash")

llm_with_tool = llm.bind_tools(tools=tools)

def chatbot(state: State):
    system_prompt = SystemMessage(content=
    """
        You are an AI Coding assistant. Whenever generating a command that creates or modifies files, you must always use the folder ai_arena/.
          Assume it always exists or create it, but do NOT ask the user to choose the folder. 
          Always auto-create ai_arena/ if missing.

    """)

    message = llm_with_tool.invoke([system_prompt] + state["messages"])
    # assert len(message.tool_calls) <= 1
    return {"messages": [message]}

tool_node = ToolNode(tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

# 

def create_chat_graph(checkpointer):
    # if(checkpointer is None):
    #     return graph_builder.compile()
    return graph_builder.compile(checkpointer=checkpointer)


# create_chat_graph(None)