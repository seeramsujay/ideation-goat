![Ideation GOAT Banner](assets/banner.png)

<div align="center">
  <h1>Ideation GOAT</h1>
  <p><strong>Cross-Domain Cross-Pollination & Ideation Engine for AI Agents</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/MCP-FastMCP-purple.svg" alt="MCP">
    <img src="https://img.shields.io/badge/License-GPL--3.0-green.svg" alt="License">
  </p>
</div>


---

The Multi-Domain Semantic Architect Agent is an enterprise-grade Model Context Protocol server that operates as the analytical and creative subconscious of advanced AI coding agents. It exposes **24 autonomous diagnostic tools** spanning three distinct knowledge domains — codebases, academic research, and visual design — enabling AI agents to validate technical compatibility, audit supply-chain security, hybridize cross-domain concepts, and scaffold production-ready project architectures in a single unified pipeline.

Powered by **Gemini 3.1 Flash Lite** for high-speed structural reasoning, enforced by **Zod-based auto-healing middleware** that self-corrects malformed LLM parameters at runtime, and deployed via the **NitroStack** framework for serverless MCP hosting on NitroCloud.

---

## 🏗️ System Architecture

```mermaid
graph TD
    %% ═══════════════════════════════════════════════════
    %% COLOUR CLASSES
    %% ═══════════════════════════════════════════════════
    classDef client   fill:#1e293b,stroke:#94a3b8,color:#f1f5f9,stroke-width:2px
    classDef gateway  fill:#312e81,stroke:#818cf8,color:#e0e7ff,stroke-width:2px
    classDef mw       fill:#4c1d95,stroke:#a78bfa,color:#ede9fe,stroke-width:2px
    classDef brain    fill:#7c3aed,stroke:#c4b5fd,color:#fff,stroke-width:3px
    classDef d1node   fill:#0c4a6e,stroke:#38bdf8,color:#e0f2fe,stroke-width:1.5px
    classDef d2node   fill:#064e3b,stroke:#34d399,color:#d1fae5,stroke-width:1.5px
    classDef d3node   fill:#431407,stroke:#fb923c,color:#ffedd5,stroke-width:1.5px
    classDef db       fill:#78350f,stroke:#fbbf24,color:#fef3c7,stroke-width:2px

    %% ═══════════════════════════════════════════════════
    %% TIER 1 — HOST INGESTION LAYER
    %% ═══════════════════════════════════════════════════
    Client["🖥️  IDE Host · Claude Desktop · Custom AI Swarm"]:::client
    Client -->|"stdio  ·  JSON-RPC 2.0"| Gateway["⚡ FastMCP Server  ·  JSON-RPC Stdio Gateway"]:::gateway

    %% ═══════════════════════════════════════════════════
    %% TIER 2 — ENTERPRISE MIDDLEWARE
    %% ═══════════════════════════════════════════════════
    Gateway --> Sandbox{"🔐  Identity Sandbox\nJWT Verification · Scope Guard"}:::mw
    Sandbox -->|"valid token"| Healer["🛡️  Parameter Auto-Healer\nZod Coercion · Typo Fuzzy-Match · Default Injection"]:::mw
    Healer --> Brain

    %% ═══════════════════════════════════════════════════
    %% TIER 3 — MASTER BRAIN
    %% ═══════════════════════════════════════════════════
    Brain(["🧠  Master Workflow Orchestrator\norchestrator.py"]):::brain

    %% ═══════════════════════════════════════════════════
    %% TIER 4a — DOMAIN 1: CODEBASE & FRAMEWORKS
    %% ═══════════════════════════════════════════════════
    Brain -->|"Codebase & Infra query"| D1

    subgraph D1 ["📁  DOMAIN 1 — Codebase & Open Source Frameworks"]
        direction TB
        D1_AST["📂  Local AST Scanner\npackage.json · requirements.txt · Cargo.toml"]:::d1node
        D1_GH["🐙  GitHub Registry Search\nRepo match · Star velocity · PR activity"]:::d1node
        D1_GL["🦊  GitLab Projects Integration\nGitLab API · cross-registry sourcing"]:::d1node
        D1_HN["📰  Hacker News Sentiment Auditor\nReal-time developer mention trends"]:::d1node
        D1_CVE["🛡️  OSV.dev CVE Security Shield\nVulnerability scan · severity gates"]:::d1node
        D1_LOCK["🔒  Ecosystem Lock-In Profiler\nAWS · GCP · Vercel · Portability Grade A–F"]:::d1node
        D1_BUG["🩺  Chronic Bug Profiler\nTF-IDF issue clustering · recurring pitfalls"]:::d1node
        D1_HW["🎛️  Edge Hardware Footprint Sizer\nSRAM · Flash · ESP32 · STM32 · Arduino"]:::d1node
        D1_DI["💉  Dependency Injection Profiler\nDI pattern quality · coupling scorer"]:::d1node
        D1_COST["💰  Cloud Cost Forecaster\nAWS · Vercel · Supabase · Neon estimates"]:::d1node
        D1_DOCK["🐳  Docker & Scaffold Synthesizer\nDockerfile · docker-compose · .env.example"]:::d1node
        D1_AST --> D1_GH --> D1_GL --> D1_HN --> D1_CVE
        D1_CVE --> D1_LOCK --> D1_BUG --> D1_HW --> D1_DI --> D1_COST --> D1_DOCK
    end

    D1_AST -.->|"vector index"| ChromaDB[("🗄️  ChromaDB\nVector Store")]:::db
    D1_GH  -.->|"embed repos"| ChromaDB

    %% ═══════════════════════════════════════════════════
    %% TIER 4b — DOMAIN 2: ACADEMIC & DEEP RESEARCH
    %% ═══════════════════════════════════════════════════
    Brain -->|"Research & theory query"| D2

    subgraph D2 ["🔬  DOMAIN 2 — Academic & Deep Research Literature"]
        direction TB
        D2_ARX["📄  arXiv Preprint Engine\nAtom XML · retry backoff · category filter"]:::d2node
        D2_SCH["🎓  Semantic Scholar Literature Client\nCitation counts · abstract summaries"]:::d2node
        D2_PAT["⚖️  Google Patents IP Evasion Tool\nCollision detection · defensive strategy"]:::d2node
        D2_BRG["🔄  Code ↔ Theory Bidirectional Translator\nCode → LaTeX · LaTeX → software template"]:::d2node
        D2_ARX --> D2_SCH --> D2_PAT --> D2_BRG
    end

    %% ═══════════════════════════════════════════════════
    %% TIER 4c — DOMAIN 3: VISUAL DESIGN & UI CANVAS
    %% ═══════════════════════════════════════════════════
    Brain -->|"Design & UI query"| D3

    subgraph D3 ["🎨  DOMAIN 3 — Visual Design & Frontend Canvas"]
        direction TB
        D3_CAN["🌌  Metaphor Canvas Node Graph\nideation-goat://canvas  ·  cognitive-distance edges"]:::d3node
        D3_HYB["🧬  Concept Hybridization Engine\nCross-domain analogy · LaTeX formula · catalyst prompt"]:::d3node
        D3_AWW["🏆  Awwwards Design Scraper\nPremium UI pattern references"]:::d3node
        D3_DRI["🎯  Dribbble Palette Harvester\nColour system · layout moodboards"]:::d3node
        D3_WID["⚛️  @nitrostack/widgets Renderer Panel\nHealth Dashboard · Design Moodboard widgets"]:::d3node
        D3_CAN --> D3_HYB --> D3_AWW --> D3_DRI --> D3_WID
    end

    D3_CAN -.->|"cache graph"| SessionCache[("💾  In-Memory\nSession Cache")]:::db
    Brain  -.->|"pipeline state"| SessionCache
```

---

## ⚡ Capability Matrix

### 🛠️ 24 Autonomous Tools

| # | Tool | Domain | Purpose |
|:--|:-----|:-------|:--------|
| 1 | `search_knowledge_grid` | D1 & D2 | Multi-domain semantic search with Target and Discovery modes |
| 2 | `breed_concepts` | D3 | Cross-pollinate two paradigms into a hybrid architectural blueprint |
| 3 | `bridge_code_and_theory` | D2 | Bidirectional code ↔ LaTeX mathematical translation |
| 4 | `assess_viability` | D2 | Patent collision detection and defensive evasion strategy |
| 5 | `search_academic_papers` | D2 | Parallel arXiv + Semantic Scholar literature sweep |
| 6 | `write_scaffolding_files` | D1 | Automated project skeleton and boilerplate generator |
| 7 | `verify_workspace_fit` | D1 | License and ecosystem compatibility auditor |
| 8 | `compose_solution_stack` | D1 | Multi-layer architectural decomposition and framework matching |
| 9 | `get_repo_health` | D1 | Real-time GitHub health, stars, and CVE telemetry |
| 10 | `profile_repo_hardware_footprint` | D1 | Edge device SRAM/Flash memory footprint estimation |
| 11 | `align_system_architecture` | D1 | Directory structure pattern detection and alignment scoring |
| 12 | `analyze_workspace_ast` | D1 | Zero-friction offline AST and dependency tree parser |
| 13 | `check_repo_health` | D1 | Supply-chain risk and maintenance health auditor |
| 14 | `check_ecosystem_lockin` | D1 | Vendor lock-in dependency scanner and portability grader |
| 15 | `analyze_repo_bugs` | D1 | TF-IDF semantic clustering of chronic bug patterns |
| 16 | `orchestrate_architectural_workflow` | D1 & D2 | Unified multi-step diagnostic pipeline orchestrator |
| 17 | `forecast_live_costs` | D1 | Cloud hosting cost estimator (AWS, Vercel, Supabase, Neon) |
| 18 | `auto_heal_parameters` | Core | Zod-based autonomous parameter type coercion and typo correction |
| 19 | `verify_identity_token` | Core | JWT authentication sandbox with scope verification |
| 20 | `profile_dependency_injection` | D1 | DI pattern quality scanner and modularity scorer |
| 21 | `generate_docker_scaffolding` | D1 | Multi-stage Dockerfile and docker-compose generator |
| 22 | `scan_local_cves` | D1 | OSV.dev vulnerability scanner with severity-based execution gates |
| 23 | `search_gitlab_repos` | D1 | GitLab project registry search integration |
| 24 | `audit_hacker_news_trends` | D1 | Real-time developer sentiment and mention trend auditor |

### 🧠 Core Intelligence Features

| Feature | Technology | Description |
|:--------|:-----------|:------------|
| 🤖 **LLM Synthesis Engine** | Gemini 3.1 Flash Lite | Powers concept hybridization, semantic analysis, and cross-domain analogy generation |
| 🛡️ **Zod Auto-Healing** | `@nitrostack/core` | Intercepts malformed LLM parameters at runtime, coerces types, corrects typos, applies defaults |
| 🔐 **Identity Sandbox** | PyJWT + OAuth 2.1 | Validates JWT tokens, enforces permission scopes, and gates privileged file operations |
| 🌌 **Metaphor Canvas** | MCP Resource | Exposes interactive node-and-edge cognitive graphs for frontend visualization |
| 📊 **Offline-First Testing** | Python unittest | 32/32 tests pass completely offline in under 2 seconds via mocked API interfaces |

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/suzaykid/ideation-goat.git
cd ideation-goat
```

### 2. Install Python Core Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install TypeScript Wrapper Dependencies

```bash
pnpm install
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and populate the required keys:

| Variable | Purpose |
|:---------|:--------|
| `GEMINI_API_KEY` | Gemini 3.1 Flash Lite API key for LLM synthesis |
| `GITHUB_TOKEN` | GitHub Personal Access Token (optional, bypasses rate limits) |
| `GITLAB_API_TOKEN` | GitLab API token for project registry searches |
| `CHROMA_DB_PATH` | Local path to ChromaDB vector store collection |

---

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Server

### Standalone stdio Mode
You can run the server directly in your terminal to verify that it starts correctly:
```bash
python server.py
```

### Integration with Claude Desktop
To integrate Ideation GOAT, edit your `claude_desktop_config.json` configuration file:

*   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Replace `/ABSOLUTE/PATH/TO/ideation-goat` with the actual absolute path to your repository.

#### Configuration (macOS / Linux)
```json
{
  "mcpServers": {
    "ideation-goat": {
      "command": "/ABSOLUTE/PATH/TO/ideation-goat/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/ideation-goat/server.py"
      ]
    }
  }
}
```

#### Configuration (Windows)
```json
{
  "mcpServers": {
    "ideation-goat": {
      "command": "C:\\ABSOLUTE\\PATH\\TO\\ideation-goat\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\ABSOLUTE\\PATH\\TO\\ideation-goat\\server.py"
      ]
    }
  }
}
```
---

## 🧪 Running the Offline Test Suite

Ideation GOAT features a comprehensive, enterprise-grade automated test suite containing **32 unit and integration tests** designed to validate every autonomous tool, routing rule, and middleware layer. The test suite is optimized for maximum execution speed, running fully offline in under 2 seconds.

### 🛡️ Mock-Driven Offline Architecture
To ensure the test suite is 100% reliable, fast, and does not hit rate-limiting thresholds or require active API credentials, all external network requests are aggressively mocked:
*   **arXiv & Semantic Scholar APIs:** Mocked using Python's `unittest.mock.patch` to intercept HTTP requests (`urllib.request.urlopen`) and serve local Atom XML documents and JSON responses.
*   **GitHub & GitLab REST APIs:** Uses mocked class structures for repository metadata, stargazers count, fork activity, commits, and pull requests to profile repository health offline.
*   **OSV.dev & Google Patents (SerpApi):** Stubbed to return clean vulnerability grids and deterministic patent organic search results, enabling testing of vulnerability scanners and IP evasion logic.

### 📂 Filesystem Isolation & Safety
Tests that perform filesystem operations—specifically `write_scaffolding_files` and `generate_docker_scaffolding`—run within completely isolated environments:
*   **Zero Side-Effects:** Utilizes Python's `tempfile.TemporaryDirectory` context manager, which builds, accesses, and tears down directories on the fly.
*   **Pollution Prevention:** No temporary files or configuration skeletons ever leak or pollute your active workspace.

### 🔒 Security-Gate Verification
The test suite explicitly asserts security constraints:
*   **Path Traversal Prevention:** Contains tests that deliberately supply path payloads outside the allowed workspace (e.g., system-level `/tmp` or parent dirs) to verify that the scaffolding utility detects and halts the process with a `Security Violation` error.
*   **Identity Sandbox & Token Gates:** Validates JWT signature parsing, expiration dates, and permission scope matching to ensure unauthorized requests are gated correctly.

### 🚀 Running the Tests

You can run the test suite using either the default Python `unittest` framework or `pytest` within your active virtual environment:

#### Option A: Using pytest (Recommended)
If you are using the local `.ig` virtual environment:
```bash
./.ig/bin/pytest
```

#### Option B: Using standard Python unittest
```bash
./.ig/bin/python -m unittest discover -s tests
```

---

## 🎨 Interactive Resources

### Constellation Map Graph (`ideation-goat://canvas`)
The server exposes a custom MCP resource mapping cognitive paths. It returns a node-and-edge JSON graph containing:
*   **Nodes:** Matched codebase topics, patents, and academic papers.
*   **Edges:** Cognitive distances and relational overlaps.
*   **Use Case:** Frontends can fetch this URI to render interactive, node-based visual graphics showing where ideas intersect.

---

## 📄 License & Restrictions

This project is licensed under the GPL-3.0 License.

### Automated Training & Ingestion Restriction
*   **NO AI Training Ingestion:** Ingestion of code, text, layouts, designs, or assets for training, validation, testing, or tuning of machine learning models or neural networks is strictly prohibited.
*   **NO Automated Scraping:** Scraping, harvesting, or automated crawling of this repository by spiders or scraper bots is prohibited.
*   **Personal/Human Use Only:** Access is provided strictly for human code inspection and educational review.

