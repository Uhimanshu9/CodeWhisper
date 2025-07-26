from langchain_core.tools import tool
import re
import subprocess


COMMAND_WARNINGS = {
    "rm": {
        "message": "Warning: 'rm' deletes files/folders permanently and can cause data loss!",
        "severity": "high",
    },
    "sudo": {
        "message": "Warning: 'sudo' runs commands with superuser privileges which can affect system stability.",
        "severity": "high",
    },
    "mv": {
        "message": "Warning: 'mv' moves files and may overwrite existing ones.",
        "severity": "medium",
    },
    "touch": {
        "message": "Warning: 'touch' creates empty files or updates file timestamps.",
        "severity": "low",
    },
    "mkdir": {
        "message": "Warning: 'mkdir' creates directories.",
        "severity": "low",
    },
    "npx create-react-app": {
        "message": "Warning: 'npx create-react-app' scaffolds a new React project. This will create many files.",
        "severity": "medium",
    },
    "rm -rf": {
        "message": "Warning: 'rm -rf' is a very destructive command that deletes directories recursively without confirmation.",
        "severity": "critical",
    },
    # Add more commands or patterns here...
}


def get_warning_for_command(cmd: str) -> dict | None:
    cmd_lower = cmd.lower()
    for key, warning_info in COMMAND_WARNINGS.items():
        if " " in key:
            if key in cmd_lower:
                return warning_info
        else:
            if re.search(r'\b' + re.escape(key) + r'\b', cmd_lower):
                return warning_info
    return None



@tool
def run_command_with_confirmation(cmd: str):
    """
    Takes a command line prompt and executes it on the user's machine and 
    returns the output of the command.
    Example: run_command(cmd="ls") where ls is the command to list the files.
    """
    
    warning_info = get_warning_for_command(cmd)
    if warning_info is not None:
        print(warning_info["message"])
        confirmation = input(f"Proceed? Severity: {warning_info['severity']} (yes/y to confirm): ").strip().lower()
        if confirmation not in ("yes", "y"):
            return "Command execution cancelled by user."

    try:
        result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        return f"Command executed successfully:\n{result}"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.output if e.output else e}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
