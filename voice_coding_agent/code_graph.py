from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage
from llm_provider import LiteLLMChatModel
from tools.run_command import run_command_with_confirmation
from tools.list_processes import list_processes
from tools.push_to_github import push_to_github
from tools.search_in_files import search_in_files
from tools.show_python_docs import show_python_docs
from tools.version_preview import (
    branch_from_version,
    create_version_checkpoint,
    get_preview_logs,
    list_project_versions,
    preview_version,
    stop_version_preview,
)
from rag.rag import update_project_index

class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [
    run_command_with_confirmation,
    list_processes,
    push_to_github,
    search_in_files,
    show_python_docs,
    create_version_checkpoint,
    list_project_versions,
    preview_version,
    branch_from_version,
    get_preview_logs,
    stop_version_preview,
    update_project_index,
]

# LiteLLM routes the OpenAI-prefixed model to OpenAI using OPENAI_API_KEY.
llm = LiteLLMChatModel()

llm_with_tool = llm.bind_tools(tools=tools)

def chatbot(state: State):
    system_prompt = SystemMessage(content=
    """
        You are an AI Coding assistant. Whenever generating a command that creates or modifies files, you must always use the folder ai_arena/.
          Assume it always exists or create it, but do NOT ask the user to choose the folder. 
          Always auto-create ai_arena/ if missing.
        Never use interactive commands, heredocs, or commands that wait for stdin. Use non-interactive file-writing commands.
        When the user explicitly accepts a meaningful UI edit or asks to save it, use create_version_checkpoint.
        When the user asks to revisit an older design, use list_project_versions, then branch_from_version before editing.
        Use preview_version only for a committed static application that has ai_arena/index.html.

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
