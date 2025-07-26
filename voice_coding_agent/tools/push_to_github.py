from langchain_core.tools import tool


@tool
def push_to_github(commit_message: str):
    """
    Stages all changes, commits with a message, and pushes to the current Git remote.
    """
    import subprocess
    commands = [
        "git add .",
        f'git commit -m "{commit_message}"',
        "git push origin main"
    ]
    try:
        for cmd in commands:
            subprocess.check_output(cmd, shell=True, universal_newlines=True)
        return "Code has been pushed to GitHub successfully."
    except subprocess.CalledProcessError as e:
        return f"Error in pushing to GitHub: {e.output if e.output else e}"
