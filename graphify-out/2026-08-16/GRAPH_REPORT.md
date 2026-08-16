# Graph Report - .  (2026-08-14)

## Corpus Check
- Corpus is ~2,963 words - fits in a single context window. You may not need a graph.

## Summary
- 45 nodes · 58 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Agent Orchestration
- Input & Graph Assembly
- Index Lifecycle
- Embeddings & Vectors
- Process Monitoring
- GitHub Automation
- Project Search
- Python Documentation
- File Change Detection
- Infrastructure Startup

## God Nodes (most connected - your core abstractions)
1. `update_project_index()` - 9 edges
2. `create_chat_graph()` - 4 edges
3. `stable_id()` - 4 edges
4. `reindex_file()` - 4 edges
5. `list_processes()` - 4 edges
6. `push_to_github()` - 4 edges
7. `run_command_with_confirmation()` - 4 edges
8. `search_in_files()` - 4 edges
9. `show_python_docs()` - 4 edges
10. `voice_input()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `voice_input()` --calls--> `create_chat_graph()`  [EXTRACTED]
  voice_coding_agent/audio_test.py → voice_coding_agent/code_graph.py
- `text_input()` --calls--> `create_chat_graph()`  [EXTRACTED]
  voice_coding_agent/audio_test.py → voice_coding_agent/code_graph.py

## Import Cycles
- None detected.

## Communities (11 total, 2 thin omitted)

### Community 0 - "Agent Orchestration"
Cohesion: 0.32
Nodes (6): TypedDict, chatbot(), State, tool, Takes a command line prompt and executes it on the user's machine and returns…, run_command_with_confirmation()

### Community 1 - "Input & Graph Assembly"
Cohesion: 0.47
Nodes (5): Capture text from the keyboard and interact with the assistant. If the user…, Capture audio from the microphone, convert to text, and interact with the…, text_input(), voice_input(), create_chat_graph()

### Community 2 - "Index Lifecycle"
Cohesion: 0.47
Nodes (5): load_metadata(), tool, Incrementally update project index by hashing files. Only changed files are re-…, save_metadata(), update_project_index()

### Community 3 - "Embeddings & Vectors"
Cohesion: 0.50
Nodes (4): Generate stable ID for Qdrant from file path (instead of Python hash)., Reindex a file into Qdrant using Gemini embeddings., reindex_file(), stable_id()

### Community 4 - "Process Monitoring"
Cohesion: 0.50
Nodes (3): list_processes(), tool, Lists processes currently running for the user.

### Community 5 - "GitHub Automation"
Cohesion: 0.50
Nodes (3): push_to_github(), tool, Stages all changes, commits with a message, and pushes to the current Git…

### Community 6 - "Project Search"
Cohesion: 0.50
Nodes (3): tool, Searches for a given term in all files in the current directory recursively., search_in_files()

### Community 7 - "Python Documentation"
Cohesion: 0.50
Nodes (3): tool, Opens the pydoc documentation for a given Python module or function., show_python_docs()

## Knowledge Gaps
- **1 isolated node(s):** `run.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `update_project_index()` connect `Index Lifecycle` to `Agent Orchestration`, `File Change Detection`, `Embeddings & Vectors`?**
  _High betweenness centrality (0.221) - this node is a cross-community bridge._
- **Why does `list_processes()` connect `Process Monitoring` to `Agent Orchestration`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `push_to_github()` connect `GitHub Automation` to `Agent Orchestration`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **What connects `run.sh script` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._