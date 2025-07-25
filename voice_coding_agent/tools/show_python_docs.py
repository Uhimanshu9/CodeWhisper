from langchain_core.tools import tool

@tool
def show_python_docs(topic: str):
    """
    Opens the pydoc documentation for a given Python module or function.
    """
    import subprocess
    try:
        result = subprocess.check_output(f"pydoc {topic}", shell=True, universal_newlines=True)
        return result
    except subprocess.CalledProcessError:
        return f"No documentation found for '{topic}'."
    except Exception as e:
        return f"Error showing documentation: {str(e)}"
