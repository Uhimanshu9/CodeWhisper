from langchain_core.tools import tool

@tool
def list_processes():
    """
    Lists processes currently running for the user.
    """
    import subprocess
    try:
        result = subprocess.check_output("ps aux", shell=True, universal_newlines=True)
        return result
    except Exception as e:
        return f"Failed to list processes: {str(e)}"
