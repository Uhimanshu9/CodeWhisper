from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Sequence

from langchain_core.tools import tool
from tools.tool_trace import run_traced_process, trace_tool
from version_preview.service import active_agent_working_directory


def _run_git(args: Sequence[str], cwd: str) -> str:
    """Run Git without a shell and return its trimmed stdout."""
    result = run_traced_process(
        ["git", *args],
        cwd=cwd,
        tool_name="push_to_github",
        check=True,
    )
    return result.stdout.strip()


def _try_git(args: Sequence[str], cwd: str) -> Optional[str]:
    """Return Git output when a command succeeds, otherwise return None."""
    result = run_traced_process(
        ["git", *args],
        cwd=cwd,
        tool_name="push_to_github",
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


@tool
@trace_tool
def push_to_github(
    commit_message: str,
    remote: Optional[str] = None,
    branch: Optional[str] = None,
    repo_path: str = ".",
) -> str:
    """
    Stage, commit, and push the current repository changes.

    The repository root, current branch, upstream remote, and configured remotes
    are discovered at runtime. ``remote``, ``branch``, and ``repo_path`` can be
    supplied when the caller needs to override the detected values.
    """
    if not commit_message.strip():
        return "Error: commit_message cannot be empty."

    if repo_path == ".":
        repo_path = str(active_agent_working_directory(Path.cwd()))

    try:
        repo_root = _run_git(["rev-parse", "--show-toplevel"], repo_path)
        current_branch = _try_git(["symbolic-ref", "--quiet", "--short", "HEAD"], repo_root)
        if not current_branch and not branch:
            return "Error: the repository is in a detached HEAD state; specify a branch explicitly."

        configured_remotes = [
            item for item in _run_git(["remote"], repo_root).splitlines() if item
        ]
        if not configured_remotes:
            return f"Error: no Git remotes are configured for {repo_root}."

        upstream_remote = None
        if current_branch:
            upstream_remote = _try_git(
                ["config", "--get", f"branch.{current_branch}.remote"],
                repo_root,
            )
        selected_remote = remote or upstream_remote or (
            "origin" if "origin" in configured_remotes else configured_remotes[0]
        )
        if selected_remote not in configured_remotes:
            available = ", ".join(configured_remotes)
            return f"Error: remote '{selected_remote}' is not configured. Available remotes: {available}."

        selected_branch = branch or current_branch

        _run_git(["add", "--all"], repo_root)
        staged_check = run_traced_process(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_root,
            tool_name="push_to_github",
            success_codes=(0, 1),
        )
        if staged_check.returncode == 0:
            return f"No changes to commit in {repo_root}."
        if staged_check.returncode != 1:
            error = staged_check.stderr.strip() or staged_check.stdout.strip()
            return f"Error: could not inspect staged changes: {error}"

        _run_git(["commit", "-m", commit_message], repo_root)
        commit_hash = _run_git(["rev-parse", "--short", "HEAD"], repo_root)
        push_output = _run_git(
            ["push", selected_remote, f"HEAD:refs/heads/{selected_branch}"],
            repo_root,
        )

        destination = f"{selected_remote}/{selected_branch}"
        details = f"\n{push_output}" if push_output else ""
        return f"Pushed commit {commit_hash} from {repo_root} to {destination}.{details}"
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or error.stdout.strip() or str(error)
        return f"Error in pushing to GitHub: {details}"
    except OSError as error:
        return f"Error in pushing to GitHub: {error}"
