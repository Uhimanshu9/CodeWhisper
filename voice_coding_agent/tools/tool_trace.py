"""Shared tracing for LangChain tools and subprocess-backed operations."""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import threading
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, Optional, Sequence, Union


Command = Union[Sequence[str], str]
DEFAULT_MAX_CHARS = 4_000
TRACE_FILE_ENV = "CODEWHISPER_TRACE_FILE"
DEFAULT_TRACE_FILE = Path(__file__).resolve().parents[1] / ".runtime" / "tool_traces.jsonl"
TRACE_LOCK = threading.Lock()
SENSITIVE_VALUE = re.compile(
    r"(?i)(api[_-]?key|token|password|secret|authorization|credential)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)


def _max_chars() -> int:
    try:
        return max(200, int(os.getenv("CODEWHISPER_TRACE_MAX_CHARS", DEFAULT_MAX_CHARS)))
    except ValueError:
        return DEFAULT_MAX_CHARS


def _command_timeout() -> int:
    """Return the maximum runtime for a tool-launched process."""
    try:
        return max(1, int(os.getenv("CODEWHISPER_COMMAND_TIMEOUT_SECONDS", "120")))
    except ValueError:
        return 120


def _redact(value: str) -> str:
    return SENSITIVE_VALUE.sub(r"\1\2<redacted>", value)


def _truncate(value: str) -> str:
    value = _redact(value)
    limit = _max_chars()
    if len(value) <= limit:
        return value
    return value[:limit] + "…<truncated>"


def _safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _truncate(str(value))


def _trace_path() -> Path:
    configured_path = os.getenv(TRACE_FILE_ENV)
    path = Path(configured_path) if configured_path else DEFAULT_TRACE_FILE
    return path.expanduser().resolve()


def _write_trace(record: Dict[str, Any]) -> None:
    """Append a trace record without allowing logging failures to break a tool."""
    try:
        path = _trace_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_LOCK:
            with path.open("a", encoding="utf-8") as trace_file:
                trace_file.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, TypeError, ValueError):
        pass


def _new_record(event: str, tool_name: str) -> Dict[str, Any]:
    return {
        "trace_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "tool": tool_name,
    }


def _trace_summary(record: Dict[str, Any]) -> str:
    summary = {
        "trace_id": record["trace_id"],
        "status": record.get("status"),
        "duration_ms": record.get("duration_ms"),
        "trace_file": str(_trace_path()),
    }
    return json.dumps(summary, ensure_ascii=False)


def _with_trace(result: Any, record: Dict[str, Any]) -> str:
    if isinstance(result, str):
        output = result
    else:
        output = json.dumps(_safe_value(result), ensure_ascii=False)
    return f"{output}\n\n[tool_trace] {_trace_summary(record)}"


def trace_tool(function: Callable[..., Any]) -> Callable[..., str]:
    """Trace a tool invocation and return its result with trace metadata."""
    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> str:
        record = _new_record("tool", function.__name__)
        record["arguments"] = _safe_value({"args": args, "kwargs": kwargs})
        started = perf_counter()
        try:
            result = function(*args, **kwargs)
            record["status"] = "success"
            record["result"] = _safe_value(result)
        except Exception as error:  # Keep the error visible to the model as a tool result.
            result = f"Error in {function.__name__}: {error}"
            record["status"] = "error"
            record["error"] = _truncate(str(error))
        record["duration_ms"] = round((perf_counter() - started) * 1000, 2)
        _write_trace(record)
        return _with_trace(result, record)

    return wrapped


def run_traced_process(
    command: Command,
    *,
    cwd: Union[str, os.PathLike[str]],
    tool_name: str,
    shell: bool = False,
    check: bool = False,
    success_codes: Sequence[int] = (0,),
) -> subprocess.CompletedProcess:
    """Run a process, capture its streams, and save a command-level trace."""
    started = perf_counter()
    command_text = command if isinstance(command, str) else shlex.join(str(item) for item in command)
    record = _new_record("command", tool_name)
    record["command"] = _truncate(command_text)
    record["cwd"] = _truncate(os.path.abspath(os.fspath(cwd)))

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=_command_timeout(),
        )
    except subprocess.TimeoutExpired as error:
        timeout = _command_timeout()
        stdout = str(error.stdout or "")
        stderr = f"Command timed out after {timeout} seconds."
        record.update(
            {
                "status": "error",
                "exit_code": 124,
                "stdout": _truncate(stdout),
                "stderr": stderr,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            }
        )
        _write_trace(record)
        return subprocess.CompletedProcess(command, 124, stdout=stdout, stderr=stderr)
    except Exception as error:
        record["status"] = "error"
        record["error"] = _truncate(str(error))
        record["duration_ms"] = round((perf_counter() - started) * 1000, 2)
        _write_trace(record)
        raise

    record.update(
        {
            "status": "success" if result.returncode in success_codes else "error",
            "exit_code": result.returncode,
            "stdout": _truncate(result.stdout or ""),
            "stderr": _truncate(result.stderr or ""),
            "duration_ms": round((perf_counter() - started) * 1000, 2),
        }
    )
    _write_trace(record)

    if check and result.returncode not in success_codes:
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def format_process_result(result: subprocess.CompletedProcess) -> str:
    """Format captured process output for the model without losing the exit code."""
    parts = [f"exit_code: {result.returncode}"]
    if result.stdout:
        parts.append("stdout:\n" + _truncate(result.stdout.rstrip()))
    if result.stderr:
        parts.append("stderr:\n" + _truncate(result.stderr.rstrip()))
    return "\n".join(parts)
