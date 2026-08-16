from langchain_core.tools import tool
import os

from tools.tool_trace import format_process_result, run_traced_process, trace_tool
from version_preview.service import active_agent_working_directory


@tool
@trace_tool
def search_in_files(search_term: str):
    """
    Searches for a given term in all files in the current directory recursively.
    """
    result = run_traced_process(
        ["grep", "-rn", "--", search_term, "."],
        cwd=active_agent_working_directory(os.getcwd()),
        tool_name="search_in_files",
        success_codes=(0, 1),
    )
    if result.returncode == 1:
        return "No matches found."
    return format_process_result(result)
