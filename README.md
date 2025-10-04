# 🎙️ Voice Coding Agent

> Transform your voice into code with an AI-powered coding assistant that understands natural language commands and executes them intelligently.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://github.com/langchain-ai/langgraph)
[![MongoDB](https://img.shields.io/badge/MongoDB-Persistence-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

Voice Coding Agent is an intelligent assistant that allows developers to code, debug, and manage projects using voice commands or text input. Built with LangGraph and powered by Google's Gemini 2.0 Flash, it features persistent conversation memory, RAG-based code understanding, and a suite of powerful development tools.

### ✨ Key Features

- 🎤 **Voice & Text Input**: Switch seamlessly between voice commands and text input
- 🧠 **Persistent Memory**: Conversations are saved using MongoDB for context continuity
- 🔧 **Smart Tool Execution**: Execute shell commands, search files, push to GitHub, and more
- 📚 **RAG Integration**: Index and query your codebase for intelligent context-aware responses
- 🤖 **AI-Powered**: Leverages Google Gemini 2.0 Flash for natural language understanding
- 🛡️ **Safety First**: Confirmation prompts for potentially destructive operations

## 🎯 Use Cases

- **Hands-Free Coding**: Code while away from keyboard or with mobility constraints
- **Rapid Prototyping**: Quickly scaffold projects with voice commands
- **Code Navigation**: Search and understand large codebases through natural queries
- **Documentation Lookup**: Get Python documentation without leaving your workflow
- **Git Automation**: Push changes to GitHub with simple voice commands
- **Process Management**: Monitor and manage running processes

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or remote)
- Google API credentials for Gemini
- Microphone (for voice input)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Uhimanshu9/voice-coding-agent.git
   cd voice-coding-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r voice_coding_agent/requirement.txt
   ```

3. **Set up MongoDB**
   ```bash
   docker-compose up -d
   ```
   Or use your own MongoDB instance.

4. **Configure environment variables**
   
   Create a `.env` file in the `voice_coding_agent` directory:
   ```env
   MONGODB_URI=mongodb://admin:admin@localhost:27017
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Run the agent**
   ```bash
   cd voice_coding_agent
   python audio_test.py
   ```

## 🎮 Usage

### Text Mode (Default)
```python
python audio_test.py
# Type your commands when prompted
💬 Please type your message...
```

### Voice Mode
Uncomment the voice input line in `audio_test.py`:
```python
voice_input()  # Uncomment this line
# text_input()  # Comment this line
```

### Example Commands

**Code Generation:**
```
"Create a Python function to calculate fibonacci numbers"
"Write a REST API endpoint for user authentication"
```

**File Operations:**
```
"Search for the word 'database' in all Python files"
"Show me the documentation for os.path module"
```

**Git Operations:**
```
"Push my changes to GitHub with message 'Added new feature'"
```

**Process Management:**
```
"List all running Python processes"
"Show me system resource usage"
```

**Project Understanding:**
```
"Update the project index with latest changes"
"Explain how the authentication module works"
```

## 🛠️ Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `run_command_with_confirmation` | Execute shell commands with safety checks | "Run npm install" |
| `list_processes` | View running system processes | "Show all processes" |
| `push_to_github` | Commit and push changes to repository | "Push to GitHub" |
| `search_in_files` | Search for patterns across project files | "Find all TODO comments" |
| `show_python_docs` | Display Python module documentation | "Show docs for requests" |
| `update_project_index` | Index codebase for RAG queries | "Update project index" |

## 🏗️ Architecture

```
voice-coding-agent/
├── voice_coding_agent/
│   ├── audio_test.py          # Main entry point with voice/text handlers
│   ├── code_graph.py           # LangGraph state machine and tool binding
│   ├── tools/                  # Custom tools for development tasks
│   │   ├── run_command.py
│   │   ├── list_processes.py
│   │   ├── push_to_github.py
│   │   ├── search_in_files.py
│   │   └── show_python_docs.py
│   ├── rag/                    # RAG implementation for code understanding
│   ├── ai_arena_temp/          # Workspace for generated files
│   └── docker-compose.yml      # MongoDB setup
```

### How It Works

1. **Input Processing**: Voice is converted to text using Google Speech Recognition or text is taken directly
2. **Intent Understanding**: Gemini 2.0 Flash interprets the natural language command
3. **Tool Selection**: LangGraph routes to appropriate tools based on intent
4. **Execution**: Tools execute with safety confirmations when needed
5. **Memory**: Conversation state is persisted to MongoDB for context continuity
6. **Response**: AI provides natural language feedback and results

## 🔧 Configuration

### MongoDB Connection
Update the MongoDB URI in `audio_test.py`:
```python
MONGODB_URI = "mongodb://your-host:27017"
```

### Conversation Thread
Change the thread ID to start a new conversation:
```python
config = {"configurable": {"thread_id": "your-thread-id"}}
```

### Model Selection
Switch AI models in `code_graph.py`:
```python
llm = init_chat_model("google_genai:gemini-2.0-flash")
# or
llm = init_chat_model("openai:gpt-4")
```

## 📊 System Requirements

- **Memory**: Minimum 4GB RAM recommended
- **Storage**: 500MB for dependencies
- **Network**: Internet connection for API calls
- **Audio**: Microphone with clear input (for voice mode)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## 🐛 Troubleshooting

**Voice Recognition Not Working:**
- Ensure microphone permissions are granted
- Check ambient noise levels
- Verify PyAudio installation: `pip install pyaudio`

**MongoDB Connection Failed:**
- Verify MongoDB is running: `docker ps`
- Check connection string in `.env`
- Ensure port 27017 is not blocked

**API Errors:**
- Verify Google API key is valid
- Check API quota and billing
- Ensure network connectivity

## 🗺️ Roadmap

- [ ] Support for more LLM providers (OpenAI, Anthropic, local models)
- [ ] Web interface for easier interaction
- [ ] Multi-language code generation support
- [ ] IDE plugin integration (VS Code, PyCharm)
- [ ] Enhanced RAG with semantic code search
- [ ] Team collaboration features
- [ ] Custom tool creation framework
- [ ] Voice command customization
- [ ] Docker containerization for easy deployment

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agentic workflow framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) for powerful language understanding
- [MongoDB](https://www.mongodb.com/) for reliable conversation persistence
- The open-source community for inspiration and tools

## 📧 Contact

**Himanshu Dahiya** - [@Uhimanshu9](https://github.com/Uhimanshu9)

Project Link: [https://github.com/Uhimanshu9/voice-coding-agent](https://github.com/Uhimanshu9/voice-coding-agent)

---

⭐ If you find this project helpful, please consider giving it a star!

**Built with ❤️ by developers, for developers**
