from langchain_core.tools import tool
import os

from tools.tool_trace import format_process_result, run_traced_process, trace_tool

@tool
@trace_tool
def show_python_docs(topic: str):
    """
    Opens the pydoc documentation for a given Python module or function.
    """
    result = run_traced_process(
        ["pydoc", topic],
        cwd=os.getcwd(),
        tool_name="show_python_docs",
    )
    return format_process_result(result)
