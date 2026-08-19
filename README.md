# CodeWhisper

CodeWhisper is a local AI coding-agent prototype with a terminal interface and visual version control for generated web interfaces. You describe a change in natural language, the LangGraph agent uses LiteLLM and OpenAI to select development tools, and the result can be saved as a Git checkpoint, previewed in Docker, or used as the starting point for a new branch.

![CodeWhisper terminal interface](docs/images/codewhisper-terminal.png)

## What the project does

CodeWhisper brings two connected workflows into one project:

1. **Conversational coding agent** — accepts text commands in the terminal, calls development tools, captures command output, and keeps conversation checkpoints in MongoDB.
2. **Visual UI version control** — displays Git history as a visual timeline, previews a selected static UI, and creates an isolated branch/worktree when you continue from an older checkpoint.

The default generated-UI workspace is [`voice_coding_agent/ai_arena`](voice_coding_agent/ai_arena). A previewable version must contain an `index.html` file in that directory and must be committed as a checkpoint.

## Current features

| Feature | Status | What it provides |
| --- | --- | --- |
| Terminal chat | Supported | Clean green terminal UI with a text prompt and formatted agent responses |
| LiteLLM + OpenAI | Supported | LiteLLM routes the configured model to OpenAI using `OPENAI_API_KEY` |
| Agent tools | Supported | Shell commands, file search, process inspection, Python documentation, Git push, and version-preview operations |
| Persistent conversations | Supported | LangGraph checkpoints stored in MongoDB |
| Tool traces | Supported | Tool arguments, results, command output, status, and duration recorded under `.runtime` |
| Git checkpoints | Supported | Saves accepted changes from `voice_coding_agent/ai_arena` as Git commits |
| Version timeline | Supported | Browser dashboard for inspecting commits, branches, prompts, and preview state |
| Continue from an old version | Supported | Creates a new Git branch and isolated worktree from the selected commit |
| Docker preview | Static UI only | Serves committed HTML/CSS/JavaScript through a restricted Nginx container |
| Voice input | Optional/manual | Voice-input code exists, but text mode is enabled by default |
| RAG indexing | Legacy/optional | Not required for normal startup; the remaining legacy indexing tool requires a Gemini key if called |
| Dynamic backend previews | Not implemented | The preview runtime does not execute generated server-side application code |

## Visual version control

![CodeWhisper visual version-control dashboard](docs/images/version-control-dashboard.png)

The dashboard treats Git as the source of truth:

- **Save checkpoint** commits the generated UI workspace.
- **Start preview** materializes the selected commit and serves its static files in Docker.
- **Continue from here** creates a branch and worktree from an older checkpoint, then directs later agent tools to that workspace.
- Selecting a checkpoint shows its commit, branch, date, recorded prompt, and preview state.

For implementation and API details, see the [visual version-control documentation](voice_coding_agent/version_preview/README.md).

## Quick start

### Prerequisites

- Git
- Python 3.11 or newer
- Docker Desktop or another Docker installation with `docker compose`
- An OpenAI API key
- macOS or Linux shell environment for `start.sh`

### 1. Clone and create the virtual environment

```bash
git clone https://github.com/Uhimanshu9/CodeWhisper.git
cd CodeWhisper

python3 -m venv .venv
source .venv/bin/activate
pip install -r voice_coding_agent/requirement.txt
```

### 2. Configure the application

```bash
cp voice_coding_agent/.env.example voice_coding_agent/.env
```

Open `voice_coding_agent/.env` and replace the placeholder API key:

```env
MONGODB_URI=mongodb://admin:admin@localhost:27017
OPENAI_API_KEY=your_openai_api_key_here
LITELLM_MODEL=openai/gpt-4.1
VERSION_PREVIEW_PORT=4090
VERSION_PREVIEW_CONTENT_DIR=voice_coding_agent/ai_arena
```

Do not commit `.env` or share your API key.

### 3. Start everything

From the repository root, run:

```bash
./start.sh
```

This single command:

1. Starts MongoDB with Docker Compose.
2. Starts the visual version-control dashboard.
3. Opens the CodeWhisper terminal agent in the current terminal.

The dashboard is available at [http://127.0.0.1:4090](http://127.0.0.1:4090).

Type a request after the `CODEWHISPER ›` prompt. Type `stop` or press `Ctrl+C` to end the terminal session. The agent and dashboard stop, while MongoDB remains running so its data is preserved.

To stop MongoDB later:

```bash
docker compose -f voice_coding_agent/docker-compose.yml down
```

## Basic workflow

### Create or edit a UI

Ask the terminal agent for a static web page, for example:

```text
Create a clean todo application in ai_arena with index.html, styles.css, and app.js.
```

The agent is instructed to place generated files under `voice_coding_agent/ai_arena`.

### Save the accepted design

After checking the result, ask the agent to save a checkpoint or use **Save checkpoint** in the dashboard. Give the checkpoint a useful description such as `Add compact todo dashboard`.

### Preview a version

1. Open [http://127.0.0.1:4090](http://127.0.0.1:4090).
2. Select a checkpoint in the timeline.
3. Choose **Start preview**.
4. Use the preview shown in the Inspector panel.

Only committed static applications containing `voice_coding_agent/ai_arena/index.html` can currently be previewed.

### Return to an older design

1. Select the older checkpoint.
2. Choose **Continue from here**.
3. CodeWhisper creates a new branch and isolated worktree.
4. Continue editing through the terminal agent; supported tools now operate in that worktree.

This keeps the newer version intact and creates a new line of development from the selected design.

## Architecture

```mermaid
flowchart LR
    User["User"] --> Terminal["Terminal UI"]
    Terminal --> Graph["LangGraph agent"]
    Graph --> Model["LiteLLM → OpenAI"]
    Graph --> Tools["Development and version tools"]
    Graph <--> MongoDB["MongoDB checkpoints"]
    Tools --> Workspace["Project files / active Git worktree"]
    Tools --> Traces["Tool and command traces"]

    Browser["Visual version-control dashboard"] --> API["Local preview API"]
    API --> Git["Git commits, branches, worktrees"]
    API --> Docker["Restricted static Docker preview"]
    Git --> Workspace
```

### Request flow

1. `audio_test.py` receives terminal text and sends it to the compiled LangGraph conversation.
2. `llm_provider.py` converts LangChain messages and tool schemas into LiteLLM requests.
3. OpenAI returns either a response or one or more tool calls.
4. LangGraph executes tools and returns their captured output to the model.
5. MongoDB stores the conversation checkpoint, while tool traces are written locally.
6. The version-preview service uses Git for history and Docker for static UI previews.

## Project structure

```text
CodeWhisper/
├── start.sh                              # Starts MongoDB, dashboard, and terminal agent
├── docs/images/                          # README screenshots
└── voice_coding_agent/
    ├── audio_test.py                     # Text and optional voice input loops
    ├── terminal_ui.py                    # Green terminal interface
    ├── code_graph.py                     # LangGraph workflow and tool registration
    ├── llm_provider.py                   # LiteLLM/OpenAI adapter
    ├── docker-compose.yml                # Local MongoDB
    ├── ai_arena/                         # Generated static UI workspace
    ├── tools/
    │   ├── run_command.py                # Non-interactive subprocess execution
    │   ├── search_in_files.py            # Project search
    │   ├── list_processes.py             # Process inspection
    │   ├── show_python_docs.py           # Python documentation lookup
    │   ├── push_to_github.py             # Git commit/push helper
    │   ├── tool_trace.py                 # Tool and subprocess tracing
    │   └── version_preview.py            # Agent-facing checkpoint/preview tools
    └── version_preview/
        ├── app.py                        # Local dashboard HTTP server/API
        ├── service.py                    # Git, worktree, and Docker operations
        ├── static/                       # Dashboard frontend
        └── docker/                       # Restricted Nginx preview image
```

## Manual startup

Use these commands when you want to run components separately.

Start MongoDB:

```bash
docker compose -f voice_coding_agent/docker-compose.yml up -d
```

Start the dashboard:

```bash
cd voice_coding_agent
../.venv/bin/python -m version_preview.app
```

Start the terminal agent in another terminal:

```bash
cd voice_coding_agent
../.venv/bin/python audio_test.py
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://admin:admin@localhost:27017` | Documents the local checkpoint database URI; the current CLI expects the matching Docker Compose credentials |
| `OPENAI_API_KEY` | none | Required for the default OpenAI model |
| `LITELLM_MODEL` | `openai/gpt-4.1` | LiteLLM model identifier |
| `VERSION_PREVIEW_PORT` | `4090` | Local dashboard port |
| `VERSION_PREVIEW_CONTENT_DIR` | `voice_coding_agent/ai_arena` | Directory committed and previewed as generated UI |
| `CODEWHISPER_NO_CLEAR` | `0` | Set to `1` to preserve startup logs instead of clearing the terminal |
| `CODEWHISPER_COMMAND_TIMEOUT_SECONDS` | `120` | Timeout for subprocess-backed agent tools |
| `CODEWHISPER_TRACE_FILE` | internal `.runtime` path | Optional custom JSONL trace destination |

Example with startup logs visible:

```bash
CODEWHISPER_NO_CLEAR=1 ./start.sh
```

## Troubleshooting

### `OPENAI_API_KEY is not set`

Ensure `voice_coding_agent/.env` exists and contains a valid `OPENAI_API_KEY`, then restart the project.

### MongoDB does not start

Make sure Docker is running, then inspect the container:

```bash
docker compose -f voice_coding_agent/docker-compose.yml ps
docker compose -f voice_coding_agent/docker-compose.yml logs mongodb
```

### Port 4090 is already in use

Use a different dashboard port:

```bash
VERSION_PREVIEW_PORT=4091 ./start.sh
```

### A preview cannot be started

Confirm the selected version is committed and contains:

```text
voice_coding_agent/ai_arena/index.html
```

Docker must also be running. Preview logs are available from the dashboard and its local API.

## Safety and current scope

CodeWhisper is a development prototype. The command tool executes generated shell commands on the host in the active agent workspace, so inspect the project and use it only in an environment you trust. Tool execution is non-interactive, time-limited, and traced, but it is not a complete host sandbox.

Static previews receive additional Docker restrictions: a non-root user, read-only snapshot and filesystem, resource limits, dropped capabilities, and `no-new-privileges`. The current preview runtime is intentionally limited to static HTML/CSS/JavaScript served by Nginx.
