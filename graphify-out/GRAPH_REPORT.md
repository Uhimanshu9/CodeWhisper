# Graph Report - CodeWhisper  (2026-08-16)

## Corpus Check
- 15 files · ~5,766 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 170 nodes · 257 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b3c1990`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 🎙️ CodeWhisper
- run_traced_process
- llm_provider.py
- Versioned UI Preview Architecture
- tool_trace.py
- rag.py
- TODO Application
- audio_test.py
- run.sh

## God Nodes (most connected - your core abstractions)
1. `run_traced_process()` - 21 edges
2. `🎙️ CodeWhisper` - 17 edges
3. `trace_tool()` - 15 edges
4. `format_process_result()` - 12 edges
5. `Versioned UI Preview Architecture` - 11 edges
6. `update_project_index()` - 10 edges
7. `push_to_github()` - 8 edges
8. `LiteLLMChatModel` - 7 edges
9. `list_processes()` - 7 edges
10. `run_command_with_confirmation()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `State` --uses--> `LiteLLMChatModel`  [INFERRED]
  voice_coding_agent/code_graph.py → voice_coding_agent/llm_provider.py
- `update_project_index()` --references--> `trace_tool()`  [EXTRACTED]
  voice_coding_agent/rag/rag.py → voice_coding_agent/tools/tool_trace.py
- `voice_input()` --calls--> `create_chat_graph()`  [EXTRACTED]
  voice_coding_agent/audio_test.py → voice_coding_agent/code_graph.py
- `text_input()` --calls--> `create_chat_graph()`  [EXTRACTED]
  voice_coding_agent/audio_test.py → voice_coding_agent/code_graph.py
- `list_processes()` --calls--> `format_process_result()`  [EXTRACTED]
  voice_coding_agent/tools/list_processes.py → voice_coding_agent/tools/tool_trace.py

## Import Cycles
- None detected.

## Communities (9 total, 1 thin omitted)

### Community 0 - "🎙️ CodeWhisper"
Cohesion: 0.05
Nodes (41): 🙏 Acknowledgments, Adjust Voice Recognition, 🔧 Advanced Configuration, 🤖 **AI-Powered by LiteLLM + OpenAI**, 🏗️ Architecture, Built with CodeWhisper, 🎙️ CodeWhisper, Configuration (+33 more)

### Community 1 - "run_traced_process"
Cohesion: 0.11
Nodes (31): Command, CompletedProcess, PathLike, TypedDict, chatbot(), State, list_processes(), tool (+23 more)

### Community 2 - "llm_provider.py"
Cohesion: 0.15
Nodes (19): AIMessage, LiteLLMChatModel, _message_to_openai(), _messages_to_openai(), Any, LiteLLM-backed chat model used by the LangGraph agent. The rest of the…, Convert a LangChain tool into an OpenAI function declaration., Convert LiteLLM/OpenAI tool calls into LangChain AIMessage calls. (+11 more)

### Community 3 - "Versioned UI Preview Architecture"
Cohesion: 0.09
Nodes (21): Agent tools, Branching workflow, Components, Core idea, Docker Preview Runner, Git repository, High-level architecture, Implementation phases (+13 more)

### Community 4 - "tool_trace.py"
Cohesion: 0.22
Nodes (15): Path, _command_timeout(), _max_chars(), _new_record(), Any, Shared tracing for LangChain tools and subprocess-backed operations., Return the maximum runtime for a tool-launched process., Append a trace record without allowing logging failures to break a tool. (+7 more)

### Community 5 - "rag.py"
Cohesion: 0.22
Nodes (13): file_hash(), get_embeddings(), load_metadata(), tool, Compute MD5 hash of a file., Generate stable ID for Qdrant from file path (instead of Python hash)., Create Gemini embeddings only when the legacy RAG tool is requested., Reindex a file into Qdrant using Gemini embeddings. (+5 more)

### Community 6 - "TODO Application"
Cohesion: 0.25
Nodes (7): Contribution, Features, Installation, License, Technologies Used, TODO Application, Usage

### Community 7 - "audio_test.py"
Cohesion: 0.47
Nodes (5): Capture text from the keyboard and interact with the assistant. If the user…, Capture audio from the microphone, convert to text, and interact with the…, text_input(), voice_input(), create_chat_graph()

## Knowledge Gaps
- **54 isolated node(s):** `run.sh script`, `💡 The Problem We Solve`, `🎤 **Dual Input Modes**`, `🧠 **Persistent Memory with MongoDB**`, `🔧 **Smart Tool Ecosystem**` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_traced_process()` connect `run_traced_process` to `tool_trace.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `LiteLLMChatModel` connect `llm_provider.py` to `run_traced_process`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **What connects `run.sh script`, `💡 The Problem We Solve`, `🎤 **Dual Input Modes**` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `🎙️ CodeWhisper` be split into smaller, more focused modules?**
  _Cohesion score 0.047619047619047616 - nodes in this community are weakly interconnected._
- **Should `run_traced_process` be split into smaller, more focused modules?**
  _Cohesion score 0.10810810810810811 - nodes in this community are weakly interconnected._
- **Should `Versioned UI Preview Architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._