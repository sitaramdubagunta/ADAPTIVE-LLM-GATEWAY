# Graph Report - llm-gateway  (2026-10-13)

## Corpus Check
- 36 files · ~17,591 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 5, .css 1)

## Summary
- 223 nodes · 384 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d7cd4051`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- auth.py
- api.js
- package.json
- Adaptive LLM Gateway
- router.py
- main.py
- chat_service.py
- groq_provider.py
- ChatWindow.jsx
- dependencies
- React + Vite
- screenshots/README.md

## God Nodes (most connected - your core abstractions)
1. `User` - 11 edges
2. `Adaptive LLM Gateway` - 11 edges
3. `login()` - 8 edges
4. `register()` - 7 edges
5. `ChatWindow()` - 7 edges
6. `Dashboard()` - 7 edges
7. `chat_v1()` - 6 edges
8. `token_stream()` - 6 edges
9. `react` - 6 edges
10. `react-router-dom` - 6 edges

## Surprising Connections (you probably didn't know these)
- `login()` --uses--> `User`  [INFERRED]
  backend/routes/auth.py → backend/database/models.py
- `register()` --uses--> `User`  [INFERRED]
  backend/routes/auth.py → backend/database/models.py
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/services/auth_service.py → backend/database/models.py
- `chat_v1()` --uses--> `User`  [INFERRED]
  backend/main.py → backend/database/models.py
- `list_chats()` --uses--> `User`  [INFERRED]
  backend/main.py → backend/database/models.py

## Import Cycles
- None detected.

## Communities (12 total, 1 thin omitted)

### Community 0 - "auth.py"
Cohesion: 0.10
Nodes (11): get_db(), login(), normalize_email(), register(), UserCreate, UserOut, get_current_user(), create_access_token() (+3 more)

### Community 1 - "api.js"
Cohesion: 0.11
Nodes (24): getChatMessages(), getChats(), getHeaders(), getToken(), login(), register(), sendMessage(), uploadAudio() (+16 more)

### Community 2 - "package.json"
Cohesion: 0.07
Nodes (32): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, @types/react, @types/react-dom (+24 more)

### Community 3 - "Adaptive LLM Gateway"
Cohesion: 0.11
Nodes (18): Adaptive LLM Gateway, API Overview, Auth Screen, Backend, Chat Dashboard, Chat History, Database Setup, Docker Backend (+10 more)

### Community 4 - "router.py"
Cohesion: 0.21
Nodes (6): build_route_payload(), get_embedding(), choose_provider(), _general_route(), _load_route_config(), _resolve_route_config()

### Community 5 - "main.py"
Cohesion: 0.19
Nodes (9): User, chat_v1(), ChatRequest, list_chats(), list_messages(), root(), get_chat_messages(), get_user_chats() (+1 more)

### Community 6 - "chat_service.py"
Cohesion: 0.25
Nodes (8): ChatService, get_db_ids(), token_stream(), create_chat(), create_request(), create_response(), _insert_returning_id(), update_chat_timestamp()

### Community 7 - "groq_provider.py"
Cohesion: 0.20
Nodes (4): GeminiProvider, GroqProvider, _messages(), _token_from_chunk()

### Community 8 - "ChatWindow.jsx"
Cohesion: 0.23
Nodes (9): ChatWindow(), sendMessage(), messageCache, markdownComponents, updateAssistantMessage(), PromptBox(), react-markdown, react-syntax-highlighter (+1 more)

### Community 9 - "dependencies"
Cohesion: 0.18
Nodes (11): dependencies, axios, lucide-react, react, react-dom, react-markdown, react-router-dom, react-syntax-highlighter (+3 more)

### Community 10 - "React + Vite"
Cohesion: 0.50
Nodes (3): Expanding the ESLint configuration, React Compiler, React + Vite

## Knowledge Gaps
- **5 isolated node(s):** `axios`, `lucide-react`, `tailwindcss`, `@types/react`, `@types/react-dom`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 85 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react-router-dom` connect `api.js` to `package.json`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `chat_v1()` and `list_chats()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `axios`, `lucide-react`, `tailwindcss` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10158730158730159 - nodes in this community are weakly interconnected._
- **Why does `dependencies` connect `dependencies` to `package.json`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Should `api.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1126984126984127 - nodes in this community are weakly interconnected._
- **Why does `react` connect `api.js` to `ChatWindow.jsx`, `package.json`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._