"""LangChain tools that expose the visual version-control backend to the agent."""

from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import tool

from tools.tool_trace import trace_tool
from version_preview.service import VersionPreviewError, VersionPreviewService


def _call(method: str, *args, **kwargs) -> str:
    try:
        result = getattr(VersionPreviewService(), method)(*args, **kwargs)
        return json.dumps(result, ensure_ascii=False)
    except VersionPreviewError as error:
        return f"Error: {error}"


@tool
@trace_tool
def create_version_checkpoint(message: str, prompt: str = "") -> str:
    """Commit the generated UI after the user accepts a meaningful edit."""
    return _call("create_checkpoint", message, prompt)


@tool
@trace_tool
def list_project_versions(limit: int = 30) -> str:
    """List Git checkpoints, branches, and the most recent preview state."""
    return _call("versions", limit)


@tool
@trace_tool
def branch_from_version(commit_sha: str, branch_name: Optional[str] = None) -> str:
    """Create an isolated branch/worktree from a selected checkpoint for new edits."""
    return _call("branch_from_version", commit_sha, branch_name)


@tool
@trace_tool
def preview_version(commit_sha: str) -> str:
    """Start a resource-limited Docker preview for a committed static UI version."""
    return _call("preview_version", commit_sha)


@tool
@trace_tool
def stop_version_preview(preview_id: str) -> str:
    """Stop an isolated Docker preview and remove its materialised snapshot."""
    return _call("stop_preview", preview_id)


@tool
@trace_tool
def get_preview_logs(preview_id: str) -> str:
    """Read the latest logs for a Docker preview."""
    return _call("preview_logs", preview_id)
