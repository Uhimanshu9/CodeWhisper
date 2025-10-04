# 🎙️ CodeWhisper

> **Whisper your ideas, watch them become code.** An AI-powered voice coding assistant that transforms natural language into executable code, making development faster, hands-free, and more accessible.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://github.com/langchain-ai/langgraph)
[![MongoDB](https://img.shields.io/badge/MongoDB-Persistence-brightgreen.svg)](https://www.mongodb.com/)
[![AI](https://img.shields.io/badge/AI-Gemini%202.0-orange.svg)](https://deepmind.google/technologies/gemini/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Why CodeWhisper?

CodeWhisper isn't just another coding tool—it's your intelligent pair programmer that listens, understands, and executes. Whether you're prototyping at lightning speed, coding with accessibility needs, or simply want a hands-free development experience, CodeWhisper makes it effortless.

### 💡 The Problem We Solve

- ⌨️ **Tired of typing?** Code fatigue is real. Give your fingers a rest.
- ♿ **Accessibility matters**: Empowering developers with mobility challenges or RSI.
- 🚀 **Speed is everything**: Think it, say it, build it—no context switching.
- 🧠 **Context is king**: Never lose your train of thought while searching docs or files.
- 🎯 **Focus on logic**: Describe what you want, not how to type it.

---

## ✨ Powerful Features

### 🎤 **Dual Input Modes**
Switch seamlessly between voice commands and text input. Perfect for when you're heads-down coding or presenting.

### 🧠 **Persistent Memory with MongoDB**
Your conversations aren't lost. Pick up exactly where you left off, maintaining full context across sessions.

### 🔧 **Smart Tool Ecosystem**
- **Execute Shell Commands**: Run any terminal command with safety confirmations
- **Intelligent File Search**: Find code patterns across your entire project instantly
- **GitHub Integration**: Commit and push with a simple voice command
- **Live Process Monitoring**: Track system resources and running processes
- **Python Documentation**: Instant access to module docs without leaving your flow
- **Codebase Indexing**: RAG-powered understanding of your entire project

### 🤖 **AI-Powered by Gemini 2.0**
Leverages Google's latest Gemini 2.0 Flash for lightning-fast natural language understanding and code generation.

### 🛡️ **Safety First Design**
Destructive operations require confirmation. Your codebase stays protected while you explore.

### 📚 **RAG-Enhanced Intelligence**
CodeWhisper indexes your codebase, understands relationships, and provides context-aware suggestions based on YOUR code style.

---

## 🎯 Perfect For

| Use Case | How CodeWhisper Helps |
|----------|----------------------|
| 🏃 **Rapid Prototyping** | Scaffold entire projects with conversational commands |
| ♿ **Accessibility** | Code without keyboard—voice is your interface |
| 🎥 **Live Coding/Demos** | Present and code simultaneously without switching focus |
| 📖 **Learning to Code** | Describe what you want and learn from AI-generated solutions |
| 🔍 **Code Exploration** | Navigate large codebases through natural language queries |
| ⚡ **Productivity Boost** | Reduce context switching with hands-free documentation lookup |
| 🤝 **Pair Programming** | Your AI co-pilot that never gets tired |

---

## 🚀 Quick Start

### Prerequisites

```bash
✅ Python 3.8 or higher
✅ MongoDB instance (local or remote)
✅ Google API credentials (Gemini)
✅ Microphone (for voice mode)
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Uhimanshu9/CodeWhisper.git
cd CodeWhisper

# 2. Install dependencies
pip install -r voice_coding_agent/requirement.txt

# 3. Start MongoDB (using Docker)
docker-compose up -d

# 4. Configure environment
cd voice_coding_agent
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Create `.env` file:
```env
MONGODB_URI=mongodb://admin:admin@localhost:27017
GOOGLE_API_KEY=your_google_api_key_here
```

### Run CodeWhisper

```bash
cd voice_coding_agent
python audio_test.py
```

**Switch to Voice Mode**: Edit `audio_test.py` and uncomment `voice_input()`

---

## 🎮 Usage Examples

### 🎤 Voice Commands

```
🗣️ "Create a FastAPI endpoint for user registration with email validation"

🗣️ "Search for all TODO comments in Python files"

🗣️ "Show me the documentation for the requests library"

🗣️ "Push my changes to GitHub with message 'Added authentication'"

🗣️ "List all running Python processes"

🗣️ "Update the project index with my latest changes"

🗣️ "Explain how the database connection works in this project"
```

### 💬 Text Commands

```bash
💬 Write a Python function to validate email addresses
💬 Create a React component for a login form
💬 Debug why my database connection is failing
💬 Refactor this code to use async/await
💬 Generate unit tests for the authentication module
```

---

## 🛠️ Tool Arsenal

| Tool | Superpower | Example Command |
|------|------------|-----------------|
| 🔨 `run_command_with_confirmation` | Execute shell commands safely | "Install numpy using pip" |
| 📊 `list_processes` | Monitor system resources | "Show memory usage" |
| 🚀 `push_to_github` | One-command Git workflow | "Push changes to main" |
| 🔍 `search_in_files` | Find anything in your codebase | "Find all API endpoints" |
| 📖 `show_python_docs` | Instant documentation | "Show pandas DataFrame docs" |
| 🧠 `update_project_index` | RAG-powered code understanding | "Index my React components" |

---

## 🏗️ Architecture

```
CodeWhisper/
├── voice_coding_agent/
│   ├── audio_test.py          # 🎤 Voice/Text input handler
│   ├── code_graph.py           # 🧠 LangGraph orchestration
│   ├── tools/                  # 🔧 Development superpowers
│   │   ├── run_command.py      # Shell execution
│   │   ├── list_processes.py   # Process monitoring
│   │   ├── push_to_github.py   # Git automation
│   │   ├── search_in_files.py  # Code search
│   │   └── show_python_docs.py # Doc lookup
│   ├── rag/                    # 📚 Codebase intelligence
│   ├── ai_arena_temp/          # 🎨 Generated code workspace
│   └── docker-compose.yml      # 🐳 MongoDB setup
```

### 🔄 How It Works

```
1. 🎤 Input → Voice/Text captured
2. 🧠 Understanding → Gemini interprets intent
3. 🎯 Routing → LangGraph selects appropriate tools
4. ⚡ Execution → Tools run with safety checks
5. 💾 Memory → State persisted to MongoDB
6. 💬 Response → Natural language feedback
```

---

## 🔧 Advanced Configuration

### Switch AI Models
```python
# In code_graph.py
llm = init_chat_model("google_genai:gemini-2.0-flash")

# Alternatives:
# llm = init_chat_model("openai:gpt-4")
# llm = init_chat_model("anthropic:claude-3-opus")
```

### Customize Conversation Threads
```python
# Start new conversation
config = {"configurable": {"thread_id": "project-alpha"}}

# Resume conversation
config = {"configurable": {"thread_id": "existing-id"}}
```

### Adjust Voice Recognition
```python
recognizer.pause_threshold = 2  # Seconds of silence before processing
recognizer.adjust_for_ambient_noise(source, duration=1)
```

---

## 📊 Performance & Requirements

| Component | Specification |
|-----------|--------------|
| **RAM** | 4GB minimum, 8GB recommended |
| **Storage** | 500MB for dependencies + codebase |
| **Network** | Required for AI API calls |
| **Microphone** | Any USB or built-in mic (48kHz+ recommended) |
| **OS** | Windows, macOS, Linux (Ubuntu tested) |

---

## 🤝 Contributing

We'd love your help making CodeWhisper even better! 

### How to Contribute

1. 🍴 Fork the repository
2. 🌿 Create your feature branch: `git checkout -b feature/AmazingFeature`
3. 💬 Commit your changes: `git commit -m 'Add AmazingFeature'`
4. 📤 Push to the branch: `git push origin feature/AmazingFeature`
5. 🎉 Open a Pull Request

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

### Ideas for Contributions

- 🌐 Add support for more LLMs (Anthropic, Ollama, local models)
- 🎨 Build a web interface
- 🔌 Create IDE plugins (VS Code, JetBrains)
- 🌍 Multi-language support
- 📝 Improve documentation
- 🐛 Fix bugs and improve error handling

---

## 🐛 Troubleshooting

<details>
<summary><b>🎤 Voice Recognition Not Working</b></summary>

- Verify microphone permissions in system settings
- Test microphone: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
- Reduce ambient noise
- Install PyAudio properly: `pip install pyaudio`
</details>

<details>
<summary><b>🔌 MongoDB Connection Failed</b></summary>

- Check if MongoDB is running: `docker ps`
- Verify connection string in `.env`
- Ensure port 27017 is not blocked by firewall
- Test connection: `mongosh mongodb://localhost:27017`
</details>

<details>
<summary><b>🤖 AI API Errors</b></summary>

- Verify Google API key is valid and active
- Check API quota at Google Cloud Console
- Ensure billing is enabled
- Test with a simple curl request to verify connectivity
</details>

<details>
<summary><b>⚠️ "Command Not Found" Errors</b></summary>

- Ensure you're in the correct directory
- Check `ai_arena_temp/` folder exists
- Verify file permissions
- Try with absolute paths
</details>

---

## 🗺️ Roadmap

### 🎯 Upcoming Features

- [ ] 🌐 **Multi-LLM Support**: OpenAI, Anthropic, Ollama, local models
- [ ] 🖥️ **Web Dashboard**: Beautiful UI for managing conversations
- [ ] 🔌 **IDE Plugins**: VS Code, PyCharm, Cursor integration
- [ ] 🌍 **Multi-Language**: Generate code in any programming language
- [ ] 🎨 **Custom Tool Builder**: Create your own tools via GUI
- [ ] 👥 **Team Features**: Shared conversations and knowledge bases
- [ ] 📱 **Mobile App**: iOS/Android companions
- [ ] 🔊 **Voice Customization**: Custom wake words and voice profiles
- [ ] 📦 **Docker One-Click Deploy**: Complete containerized setup
- [ ] 🧪 **Test Generation**: Auto-generate unit tests for any code
- [ ] 📈 **Analytics Dashboard**: Track productivity and usage patterns
- [ ] 🔐 **Enterprise Features**: SSO, audit logs, role-based access

### 🌟 Future Vision

CodeWhisper aims to become the **universal voice interface for software development**, supporting all languages, frameworks, and workflows while maintaining simplicity and accessibility.

---

## 🏆 Showcase

> "CodeWhisper has transformed how I prototype. What used to take hours now takes minutes!" - *Beta Tester*

### Built with CodeWhisper
*Coming soon: Show off what you've built using CodeWhisper!*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Free to use, modify, and distribute. Commercial use allowed!

---

## 🙏 Acknowledgments

Built with amazing open-source tools:

- 🦜 [LangGraph](https://github.com/langchain-ai/langgraph) - Agentic AI workflows
- 🧠 [Google Gemini](https://deepmind.google/technologies/gemini/) - Powerful language model
- 🍃 [MongoDB](https://www.mongodb.com/) - Conversation persistence
- 🎙️ [SpeechRecognition](https://github.com/Uberi/speech_recognition) - Voice input processing
- 💚 Open Source Community - For inspiration and support

---

## 📧 Connect

**Himanshu Dahiya**

- 🐙 GitHub: [@Uhimanshu9](https://github.com/Uhimanshu9)
- 📧 Email: dev.himanshu.ai@gmail.com
- 🔗 Project: [CodeWhisper](https://github.com/Uhimanshu9/CodeWhisper)

---

<div align="center">

### ⭐ Star us on GitHub — it motivates us a lot!

**Built with ❤️ for developers who think faster than they type**

[Report Bug](https://github.com/Uhimanshu9/CodeWhisper/issues) · [Request Feature](https://github.com/Uhimanshu9/CodeWhisper/issues) · [Discussions](https://github.com/Uhimanshu9/CodeWhisper/discussions)

</div>
