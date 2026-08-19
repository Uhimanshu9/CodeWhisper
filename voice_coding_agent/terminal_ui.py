"""Small, dependency-free terminal presentation helpers for CodeWhisper."""

from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Any


RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[38;5;46m"
DIM_GREEN = "\033[38;5;71m"
MID_GREEN = "\033[38;5;40m"
BRIGHT_GREEN = "\033[38;5;82m"
RED = "\033[38;5;203m"

BIG_TITLE = r"""
  ___ ___  ___  _____      ___  _  _ ___ ___ ___ ___ ___
 / __/ _ \|   \| __\ \    / / || |_ _/ __| _ \ __| _ \
| (_| (_) | |) | _| \ \/\/ /| __ || |\__ \  _/ _||   /
 \___\___/|___/|___| \_/\_/ |_||_|___|___/_| |___|_|_\
"""

# Generated from the supplied reference image at terminal-friendly resolution.
# Character density preserves the bright and dark texture without image support.
PIXEL_LOGO = r"""
                        ......... ..
                  .....::::.:..::.. .:...
                  :::.:++...:..+x:.+:+:...:.
             ..:::+:: +Ax:+:. .:A:x###x:::+:::.
           ..  +#xxx+:xA#:x#+xxx#x##A:+:.+x+:.::.
          ..:..+Ax+xAxxx#xxx+#x#+x##x#A::#xxx+x+::
        ...:::++##x##x++x:+x:xxx+#xxx#x#AA::+##+:::.
         ::+x#xxx++::xx++:::++:::++:x+#AAx...xA##x::.
     ..  +x#x#AAAx::++++:.. .  ..:::xx#+xA##A###x+:.:.
       ..:xxxx###x:.::..            ::+x#x#AAA#+.+++::
      .++#####x++xx+:.               .::+x#AAx..:::+:::
    . .:x##xx++++++::                ..+xA##x+x##AAx: :
     .::.+x#xxx+xx++.                 .+x##xxx#AAAA#+.:.
   ..::. :x#x++xx++x.                 :++xx#A#AO#xx#+:::
      .+xx#xxx+x+:x#+                 x#xAAx#AA#x###+::.
    . :++::xAA##xx###+.             .x+x#A###AO#:+xx:.:
     ..:xxxxxA#x###xx#x+.         ::x#x#AAAAAOOOA#+: ..
     . .++:+##xxxx+:##Axxxx++++:+x##x+####AA##xx+#x:.:
       .::::::x#x+++Axx++x#A##x+xxA#x##A##AOx::++x+::
       ...:. ++:+A####xxxAA##+x#:##AA#+xAOOOAA#xx+::
          . :+:.#AxAA#+xxxA#x.xA++#x#AOx#OAAAAAx...
          ....:+x++AAxx##xA##x#Axx#x#OO#:+#+::+x:.
             .:. ++:++..:.#AA#+xA#AO##xx:++..:..
                 :::++:..+xAO+  x#+#x+:+.:x+...
                  . .:+:x::#x::.:x+:  ..:..
                     ...:..:. .  ..:
"""


def _supports_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _style(value: Any, color: str = GREEN, bold: bool = False) -> str:
    text = str(value)
    if not _supports_color():
        return text
    prefix = color + (BOLD if bold else "")
    return f"{prefix}{text}{RESET}"


def _style_logo_line(line: str) -> str:
    if not _supports_color():
        return line

    styles = {
        ".": DIM_GREEN,
        ":": MID_GREEN,
        "+": GREEN,
        "x": GREEN,
        "#": BRIGHT_GREEN + BOLD,
        "A": BRIGHT_GREEN + BOLD,
        "O": BRIGHT_GREEN + BOLD,
    }
    rendered = []
    active_style = None
    for character in line:
        character_style = styles.get(character)
        if character_style != active_style:
            if active_style is not None:
                rendered.append(RESET)
            if character_style is not None:
                rendered.append(character_style)
            active_style = character_style
        rendered.append(character)
    if active_style is not None:
        rendered.append(RESET)
    return "".join(rendered)


def _centered_logo_lines(width: int) -> list[str]:
    lines = PIXEL_LOGO.strip("\n").splitlines()
    non_empty = [line for line in lines if line.strip()]
    common_indent = min(len(line) - len(line.lstrip()) for line in non_empty)
    normalized = [line[common_indent:].rstrip() for line in lines]
    logo_width = max(len(line) for line in normalized)
    padding = " " * max(0, (width - logo_width) // 2)
    return [(padding + line)[:width] for line in normalized]


def print_banner() -> None:
    """Print the CodeWhisper identity banner once at startup."""
    width = shutil.get_terminal_size((88, 24)).columns
    width = max(64, min(width, 100))
    inner_width = width - 2
    title_lines = BIG_TITLE.strip("\n").splitlines()
    title_width = max(len(line) for line in title_lines)
    title_padding = " " * max(0, (width - title_width) // 2)
    dashboard_url = os.getenv("CODEWHISPER_DASHBOARD_URL", "http://127.0.0.1:4090")

    print()
    if title_width <= width:
        for line in title_lines:
            print(_style(title_padding + line, BRIGHT_GREEN, True))
    else:
        print(_style("CODEWHISPER".center(width), BRIGHT_GREEN, True))
    print(_style("AI CODING ASSISTANT  /  LITELLM + OPENAI".center(width), DIM_GREEN))
    print()
    print(_style(f"╭{'─' * inner_width}╮", GREEN, True))
    for line in _centered_logo_lines(inner_width):
        content = line.ljust(inner_width)
        print(f"{_style('│', GREEN, True)}{_style_logo_line(content)}{_style('│', GREEN, True)}")
    print(_style(f"├{'─' * inner_width}┤", GREEN, True))
    status = f"● MongoDB online   ● Dashboard {dashboard_url}"
    print(
        f"{_style('│', GREEN, True)}"
        f"{_style(status.center(inner_width), MID_GREEN)}"
        f"{_style('│', GREEN, True)}"
    )
    print(_style(f"╰{'─' * inner_width}╯", GREEN, True))
    print(_style("  Type 'stop' to end the session · Ctrl+C to interrupt", DIM_GREEN))
    print()


def print_status(message: str) -> None:
    print(f"{_style('•', GREEN, True)} {_style(message, DIM_GREEN)}")


def print_error(message: str) -> None:
    print(f"{_style('×', RED, True)} {_style(message, RED)}")


def prompt() -> str:
    return input(f"{_style('CODEWHISPER', GREEN, True)} {_style('›', GREEN, True)} ")


def _message_text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return str(content).strip() if content else ""


def print_ai_message(message: Any) -> None:
    """Render an AI response or tool call without LangChain's verbose box."""
    tool_calls = getattr(message, "tool_calls", None) or []
    content = _message_text(message)

    if tool_calls:
        print(f"\n{_style('╭─ tools', GREEN, True)}")
        for call in tool_calls:
            name = call.get("name", "unknown_tool") if isinstance(call, dict) else str(call)
            arguments = call.get("args", {}) if isinstance(call, dict) else {}
            rendered_args = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
            print(
                f"{_style('│', DIM_GREEN)} {_style(name, GREEN, True)} "
                f"{_style(rendered_args, DIM_GREEN)}"
            )
        if content:
            print(f"{_style('│', DIM_GREEN)} {_style(content)}")
        print(_style("╰─", GREEN, True))
        return

    if content:
        print(f"\n{_style('╭─ CODEWHISPER', GREEN, True)}")
        print(content)
        print(_style("╰─", GREEN, True))
