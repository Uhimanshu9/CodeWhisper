from langchain_core.tools import tool


@tool
def search_in_files(search_term: str):
    """
    Searches for a given term in all files in the current directory recursively.
    """
    import subprocess
    try:
        result = subprocess.check_output(f'grep -rn "{search_term}" .', shell=True, universal_newlines=True)
        return result if result else "No matches found."
    except subprocess.CalledProcessError:
        return "No matches found."
    except Exception as e:
        return f"Error searching files: {str(e)}"
