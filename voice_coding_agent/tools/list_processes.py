from langchain_core.tools import tool
import os

from tools.tool_trace import format_process_result, run_traced_process, trace_tool

@tool
@trace_tool
def list_processes():
    """
    Lists processes currently running for the user.
    """
    result = run_traced_process(
        ["ps", "aux"],
        cwd=os.getcwd(),
        tool_name="list_processes",
    )
    return format_process_result(result)
