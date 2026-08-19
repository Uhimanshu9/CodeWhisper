from langchain_core.tools import tool
import os

from tools.tool_trace import format_process_result, run_traced_process, trace_tool
from version_preview.service import active_agent_working_directory

@tool
@trace_tool
def run_command_with_confirmation(cmd: str):
    """
    Takes a command line prompt and executes it on the user's machine and 
    returns the output of the command.
    Example: run_command(cmd="ls") where ls is the command to list the files.
    """
    result = run_traced_process(
        cmd,
        cwd=active_agent_working_directory(os.getcwd()),
        tool_name="run_command_with_confirmation",
        shell=True,
    )
    return format_process_result(result)
