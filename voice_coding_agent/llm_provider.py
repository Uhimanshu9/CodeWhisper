"""LiteLLM-backed chat model used by the LangGraph agent.

The rest of the application expects a LangChain-style object with
``bind_tools`` and ``invoke``.  LiteLLM exposes a provider-neutral completion
API, so this adapter translates between the two message/tool formats while
keeping the graph and ToolNode unchanged.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from litellm import completion


load_dotenv(Path(__file__).resolve().with_name(".env"))

DEFAULT_MODEL = "openai/gpt-4.1"


def _read(value: Any, key: str, default: Any = None) -> Any:
    """Read a field from either LiteLLM's objects or plain dictionaries."""
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _tool_call_to_openai(call: Any) -> Dict[str, Any]:
    """Convert LangChain's internal tool-call shape to OpenAI's shape."""
    function = _read(call, "function", {}) or {}
    name = _read(call, "name") or _read(function, "name")
    arguments = _read(call, "args")
    if arguments is None:
        arguments = _read(function, "arguments", {})
    if not isinstance(arguments, str):
        arguments = json.dumps(arguments or {})

    return {
        "id": _read(call, "id"),
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def _message_to_openai(message: Any) -> Dict[str, Any]:
    """Convert a LangChain message (or a plain message dictionary)."""
    if isinstance(message, Mapping):
        role = message.get("role", "user")
        content = message.get("content", "")
        tool_calls = message.get("tool_calls")
        tool_call_id = message.get("tool_call_id")
    else:
        role = getattr(message, "type", "user")
        content = getattr(message, "content", "")
        tool_calls = getattr(message, "tool_calls", None)
        tool_call_id = getattr(message, "tool_call_id", None)

    role = {"human": "user", "ai": "assistant"}.get(role, role)
    converted: Dict[str, Any] = {"role": role, "content": content}

    if tool_calls:
        converted["tool_calls"] = [_tool_call_to_openai(call) for call in tool_calls]
    if tool_call_id:
        converted["tool_call_id"] = tool_call_id

    return converted


def _messages_to_openai(messages: Sequence[Any]) -> List[Dict[str, Any]]:
    """Convert messages and remove interrupted tool calls from old threads.

    If the process stops after the model emits a tool call but before the tool
    result is checkpointed, MongoDB can contain an assistant tool-call message
    with no matching ``tool`` message. OpenAI rejects that history. Removing
    only the unfinished assistant call lets the conversation recover while
    retaining all completed messages.
    """
    converted: List[Dict[str, Any]] = []
    pending_tool_ids = set()
    pending_assistant_index: Optional[int] = None

    for message in messages:
        current = _message_to_openai(message)
        role = current.get("role")

        if role == "assistant" and current.get("tool_calls"):
            if pending_assistant_index is not None:
                converted.pop(pending_assistant_index)
            pending_tool_ids = {
                call.get("id")
                for call in current["tool_calls"]
                if call.get("id")
            }
            pending_assistant_index = len(converted)
            converted.append(current)
            continue

        if role == "tool":
            tool_call_id = current.get("tool_call_id")
            if tool_call_id in pending_tool_ids:
                pending_tool_ids.remove(tool_call_id)
                converted.append(current)
                if not pending_tool_ids:
                    pending_assistant_index = None
            else:
                converted.append(current)
            continue

        if pending_tool_ids:
            if pending_assistant_index is not None:
                converted.pop(pending_assistant_index)
            pending_tool_ids = set()
            pending_assistant_index = None
        converted.append(current)

    if pending_tool_ids and pending_assistant_index is not None:
        converted.pop(pending_assistant_index)

    return converted


def _tool_schema(tool: Any) -> Dict[str, Any]:
    """Convert a LangChain tool into an OpenAI function declaration."""
    args_schema = getattr(tool, "args_schema", None)
    if hasattr(args_schema, "model_json_schema"):
        parameters = args_schema.model_json_schema()
    elif hasattr(args_schema, "schema"):
        parameters = args_schema.schema()
    else:
        # LangChain's ``tool.args`` is only the properties map, while the
        # OpenAI tools API requires a complete object JSON Schema.
        parameters = {
            "type": "object",
            "properties": getattr(tool, "args", None) or {},
        }

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": getattr(tool, "description", "") or "",
            "parameters": parameters,
        },
    }


def _tool_calls_from_response(message: Any) -> List[Dict[str, Any]]:
    """Convert LiteLLM/OpenAI tool calls into LangChain AIMessage calls."""
    converted: List[Dict[str, Any]] = []
    for call in _read(message, "tool_calls", []) or []:
        function = _read(call, "function", {}) or {}
        arguments = _read(function, "arguments", "{}")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}

        converted.append(
            {
                "name": _read(function, "name"),
                "args": arguments or {},
                "id": _read(call, "id"),
                "type": "tool_call",
            }
        )
    return converted


class LiteLLMChatModel:
    """Small synchronous LangChain-compatible wrapper around LiteLLM."""

    def __init__(self, model: Optional[str] = None, tools: Iterable[Any] = ()) -> None:
        self.model = model or os.getenv("LITELLM_MODEL", DEFAULT_MODEL)
        self._tools = tuple(tools)

    def bind_tools(self, tools: Iterable[Any], **_: Any) -> "LiteLLMChatModel":
        """Return a copy configured with the tools available to the agent."""
        return type(self)(model=self.model, tools=tools)

    def invoke(self, messages: Sequence[Any], **kwargs: Any) -> AIMessage:
        """Call LiteLLM and return the AIMessage expected by LangGraph."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to voice_coding_agent/.env "
                "or export it before starting CodeWhisper."
            )

        request: Dict[str, Any] = {
            "model": self.model,
            "messages": _messages_to_openai(messages),
            "api_key": api_key,
        }
        if self._tools:
            request["tools"] = [_tool_schema(tool) for tool in self._tools]
        request.update(kwargs)

        response = completion(**request)
        choices = _read(response, "choices", []) or []
        if not choices:
            raise RuntimeError("LiteLLM returned no choices for the chat request.")

        response_message = _read(choices[0], "message", {}) or {}
        content = _read(response_message, "content", "") or ""
        return AIMessage(
            content=content,
            tool_calls=_tool_calls_from_response(response_message),
        )


__all__ = ["LiteLLMChatModel"]
