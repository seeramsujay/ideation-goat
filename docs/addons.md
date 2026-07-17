# 🛠️ Ideation GOAT Addons & Feature Reference

This consolidated guide details all MCP tools, resources, and future roadmap capabilities across the Ideation GOAT repository. It maps each feature back to the three core domains of the **Multi-Domain Semantic Architect Agent**, showing its working status, associated source files, and corresponding test cases.

---

## 🗺️ Multi-Domain Mapping Matrix

The Ideation GOAT MCP server bridges three distinct conceptual domains to help developer teams discover, validate, and scaffold software systems.

```
                  +----------------------------------------------+
                  |    Multi-Domain Semantic Architect Agent     |
                  +----------------------+-----------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
+--------v--------+             +--------v--------+             +--------v--------+
|    Domain 1:    |             |    Domain 2:    |             |    Domain 3:    |
| Open Source     |             | Research &      |             | Design &        |
| Frameworks      |             | Academic Papers |             | Frontend        |
+-----------------+             +-----------------+             +-----------------+
```

| Domain | Focus | Key Associated MCP Tools / Resources |
| :--- | :--- | :--- |
| **Domain 1: Open Source Frameworks & Architecture** | Local stack compatibility, license checks, project health, tech debt, ecosystem lock-in, chronic bugs, and automatic codebase scaffolding. | `search_knowledge_grid` (target mode), `verify_workspace_fit`, `analyze_workspace_ast`, `align_system_architecture`, `check_repo_health`, `get_repo_health`, `check_ecosystem_lockin`, `analyze_repo_bugs`, `write_scaffolding_files`, `orchestrate_architectural_workflow` |
| **Domain 2: Research & Academic Papers** | Bridging software implementations with cutting-edge academic preprints and theoretical/mathematical models. | `search_academic_papers`, `search_knowledge_grid` (discovery mode), `bridge_code_and_theory`, `breed_concepts` |
| **Domain 3: Design & Frontend Portfolios** | Synthesis of visual templates, hex colors, and UI layouts into responsive frontends. | Supported via Streamlit canvas representation and canvas graph mapping resource (`ideation-goat://canvas`). Future CLI/Next.js theme scaffolding. |

---

## 📋 Active MCP Tools & Implementation Reference

The following list contains all fully implemented and active MCP tools exposed by `server.py`, with related roadmap capabilities merged in to check for duplicates and preserve all project specification context.

### 1. Multi-Domain Semantic Queries (`search_knowledge_grid`)
*   **Domain:** Domain 1 (Target Mode) / Domain 2 (Discovery Mode)
*   **Description:** Interrogates local vector databases (ChromaDB), academic paper search (arXiv), and USPTO patent records.
    *   `target` Mode: Performs high-precision, direct functional searches for relevant repositories and papers.
    *   `discovery` Mode: Utilizes an **Inverse-Similarity Filter** to exclude direct computer science (`cs.*`) papers. It retrieves parallel concepts in disciplines like quantitative biology, physics, and finance, mapping them to structural/biological analogies (e.g., neural decay models).
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `search_engine.py`, `arxiv_client.py`, `patent_client.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_search_knowledge_grid_discovery`, `TestIdeationGoatServer.test_search_knowledge_grid_target`)

### 2. Concept Hybridization (`breed_concepts`)
*   **Domain:** Domain 2 (Research & Academia)
*   **Description:** Cross-pollinates two distinct architectural paradigms (e.g., Marine Biology neural models and Computer Science caches) into a single hybrid specification. Generates a custom conceptual bridge, mathematical LaTeX formulas, and a catalyst prompt for client LLMs.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_breed_concepts`)

### 3. Bidirectional Algorithmic Translation (`bridge_code_and_theory`)
*   **Domain:** Domain 2 (Research & Academia)
*   **Description:** Translates code snippets into mathematical LaTeX representations (and maps them to academic literature) or parses LaTeX formulas to recommend matching software codebase architectures/templates.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_bridge_code_and_theory_code_to_math`, `TestIdeationGoatServer.test_bridge_code_and_theory_math_to_code`)

### 4. Supply-Chain Security & Vitality Audit (`check_repo_health` / `get_repo_health`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Fetches real-time commit velocity, pull request activity, and open issue ratios to compute an open-source vitality score. Also queries OSV.dev to scan the latest commit SHA for known vulnerability CVEs.
*   **Merged Roadmap Capabilities:**
    *   **The Longevity Predictor:** Solves the fear of commitment by answering: *"Will this framework die and waste my time?"* Developers are terrified of adopting frameworks that maintainers will abandon.
        *   *How it works:* Reads a repository's commit velocity, maintainer response time to pull requests, and ecosystem momentum over the last 3 years.
        *   *MCP Primitive Leveraged:* Resource.
        *   *Roadmap Tasks:* Incorporate star velocity, PyPI/npm download velocity, and monthly active user trends; calculate project health/decay indexes and intervene if a community is dying.
    *   **The CVE Security Shield:** Solves the fear of sabotage and injecting vulnerabilities during supply chain attacks.
        *   *How it works:* Cross-references the matched framework's metadata against the National Vulnerability Database (NVD) or GitHub Advisory Database.
        *   *MCP Primitive Leveraged:* Tool.
        *   *Roadmap Tasks:* Implement a full dependency tree scanner calling OSV.dev for local configurations; implement severity-based execution gates to halt scaffolding and pivot if a critical vulnerability is detected.
*   **Working Status:** **Fully Implemented** (Commit velocity scoring, PR activity, and OSV.dev SHA checker active; local tree scanning and live download trend integration on roadmap)
*   **Python File:** `server.py`, `repo_profiler.py`, `analyzers/health_analyzer.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_check_repo_health`, `TestIdeationGoatServer.test_get_repo_health`)

### 5. Local Stack AST Scanning (`analyze_workspace_ast`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Zero-friction local AST scan of package manifests (e.g., `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and source import statements to discover active frameworks, build systems, and dependencies. Runs fully offline and requires no external API keys.
*   **Merged Roadmap Capabilities:**
    *   **Dependency Forecaster:** Recommending a great framework is useless if it breaks the developer's existing codebase. This feature prevents library conflicts before installation.
        *   *How it works:* The agent reads the user's active package manager files from their local environment.
        *   *MCP Primitive Leveraged:* Resource.
        *   *Roadmap Tasks:* Expand package manifest AST scan to analyze transitive dependencies; parse deep lockfiles (e.g., `pnpm-lock.yaml`, `poetry.lock`, `package-lock.json`); cross-reference new framework dependencies against the local environment to warn of potential version conflicts.
*   **Working Status:** **Fully Implemented** (Offline local AST package/manifest parser is active; transitive dependency tree and lockfile resolution on roadmap)
*   **Python File:** `server.py`, `workspace_analyzer.py`, `analyzers/workspace_analyzer.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_analyze_workspace_ast`)

### 6. Workspace Compatibility & License Guard (`verify_workspace_fit`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Audits package managers and license structures of local projects against proposed GitHub repositories. Prevents copyleft licensing conflicts (e.g., commercial MIT code importing AGPL/GPL packages) and flags language mismatches.
*   **Merged Roadmap Capabilities:**
    *   **License Compliance Checker:** Accidentally integrating restrictive open-source code into commercial products is a massive real-world legal problem. This acts as a legal guardrail.
        *   *How it works:* When pulling repository metadata, the agent specifically extracts the license type.
        *   *MCP Primitive Leveraged:* Prompt / Tool.
        *   *Roadmap Tasks:* Read legal compliance profile configurations from `config.py` (e.g., commercial vs open source); auto-filter or strongly warn against GPL-licensed frameworks if closed-source targets are detected, prioritizing MIT or Apache 2.0 alternatives.
*   **Working Status:** **Fully Implemented** (Copyleft check logic active; configurable profiles on roadmap)
*   **Python File:** `server.py`, `workspace_analyzer.py`, `analyzers/compatibility_scorer.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_verify_workspace_fit`)

### 7. Ecosystem Lock-In & Portability Profiler (`check_ecosystem_lockin`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Evaluates dependencies to identify hard vendor lock-in with proprietary cloud suites (AWS, Vercel, GCP, Azure, Cloudflare) and assigns a Portability Grade (A to F).
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `analyzers/lockin_profiler.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_check_ecosystem_lockin`)

### 8. Chronic Bug Profiler (`analyze_repo_bugs`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Gathers open/closed bug reports from GitHub, running n-gram keyword grouping and clustering to identify recurring structural pitfalls (e.g., "memory leak during SSR", "WebSocket connection drops") before the developer adopts the framework.
*   **Merged Roadmap Capabilities:**
    *   **Live Sentiment Auditor:** READMEs are marketing documents; the "Issues" tab is where the truth lives. This audits recent GitHub issues for hidden red flags.
        *   *How it works:* Fetches the 50 most recent open issues of the semantically matched repository via the GitHub API.
        *   *MCP Primitive Leveraged:* Tool.
        *   *Roadmap Tasks:* Query GitHub API for top 50 active open issues; integrate a lightweight NLP classifier or simple rule-based sentiment lexicon to detect critical unresolved problems; perform rapid sentiment analysis and flag risk in real-time.
*   **Working Status:** **Fully Implemented** (Bug clustering and n-gram keyword grouping active; dynamic sentiment classification on roadmap)
*   **Python File:** `server.py`, `analyzers/bug_profiler.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_analyze_repo_bugs`)

### 9. Edge-Deploy Footprint Profiler (`profile_repo_hardware_footprint`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Profiles structural resource weights of packages (assesses heap allocation, C++ STL usage, Python interpretation overhead) and estimates SRAM/Flash footprints against edge microcontrollers (ESP32, STM32, Arduino).
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `repo_profiler.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_profile_repo_hardware_footprint`)

### 10. Architectural Alignment Aligner (`align_system_architecture`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Profiles local workspace folder layouts to detect design patterns (Hexagonal, MVC, Clean, Monolith) and outputs integration adaptors/guidance matching that structure.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `workspace_analyzer.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_align_system_architecture`)

### 11. Agentic Stack Composer (`compose_solution_stack`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Decomposes complex multi-layered system descriptions into separate layers (e.g., storage, transport, cryptography) and suggests compatible packages for each.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `search_engine.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_compose_solution_stack`)

### 12. Parallel Academic Search (`search_academic_papers`)
*   **Domain:** Domain 2 (Research & Academia)
*   **Description:** Executes parallel queries across arXiv and Semantic Scholar databases to return academic literature summaries and citation counts.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `arxiv_client.py`, `scholar_client.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_search_academic_papers`)

### 13. Project Scaffolder (`write_scaffolding_files`)
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Creates skeleton folders and code configurations (`README.md`, `math_engine.py`, `state_buffer.py`, `requirements.txt`) securely in the workspace. Enforces strict boundary checks to prevent path traversal attacks.
*   **Merged Roadmap Capabilities:**
    *   **The "Works Anywhere" Synthesizer:** Solves the dreaded "It works on my machine" curse. Environment setup breaks the spirit of engineers; we need universal parity.
        *   *How it works:* The agent writes directly to the user's file system to generate virtualization files.
        *   *MCP Primitive Leveraged:* Tool.
        *   *Roadmap Tasks:* Integrate templates in `scaffolder.py` to write custom `Dockerfile` and `docker-compose.yml` configurations tailored to the selected framework and local environment; generate associated environment configurations (e.g. `.env.example`).
*   **Working Status:** **Fully Implemented** (Secure folder/boilerplate scaffolding active; automated Docker layout generation on roadmap)
*   **Python File:** `server.py`, `scaffolder.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_write_scaffolding_files`)

### 14. Unified Workflow Orchestration (`orchestrate_architectural_workflow`)
*   **Domain:** Domain 1 (Open Source Frameworks) & Domain 2 (Research)
*   **Description:** Runs an end-to-end multi-step diagnostic sequence. It aggregates workspace AST parsing, target repo search, dynamic stack layering, vulnerability telemetry scans, cloud lock-in audits, chronic bug profiling, hardware footprint checks, and directory scaffolding into a single unified analytical report.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`, `orchestrator.py`
*   **Test File / Cases:** `tests/test_server.py` (`TestIdeationGoatServer.test_orchestrate_architectural_workflow_tool`, `TestIdeationGoatServer.test_workflow_orchestrator_module_success`)

---

## 🚀 Future Roadmap Capabilities (Planned Addons)

These planned additions are designed to expand the Semantic Architect Agent's capabilities utilizing the Model Context Protocol (MCP) and the Nitrostack framework, without duplicating any of the active codebase tools.

### 15. Interactive Health Widget
*   **Domain:** Domain 3 (Design & UI/UX Synthesis)
*   **Description:** Solves user detail fatigue by displaying a visual dashboard of a repository's status for immediate visual impact.
    *   *How it works:* Utilizes the `@nitrostack/widgets` package to attach React components directly to the tool's output.
    *   *MCP Primitive Leveraged:* Widget.
    *   *Roadmap Tasks:* Build React UI component templates using the `@nitrostack/widgets` standard; embed SVG/JSON visualizations (Match Percentage ring chart, live GitHub stars, date of last commit, and a one-click "Install Now" button).
*   **Working Status:** **Planned (Roadmap)** (Frontend representation layout modeled in Streamlit dashboard)
*   **Python File:** `app.py`
*   **Test File / Cases:** N/A

### 16. Live Cost Forecaster
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Solves financial anxiety regarding whether a developer can actually afford to run the suggested architecture.
    *   *How it works:* Pings live pricing APIs across platforms like AWS, Supabase, Vercel, or NitroCloud.
    *   *MCP Primitive Leveraged:* Tool.
    *   *Roadmap Tasks:* Integrate public API price scrapers or static SDK tables for major cloud service providers (AWS, Vercel, Supabase, Neon); automatically calculate estimated monthly costs based on expected traffic; render a Budget Widget showing free tier limits and scaling costs.
*   **Working Status:** **Planned (Roadmap)**
*   **Python File:** N/A
*   **Test File / Cases:** N/A

### 17. Autonomous Schema Auto-Healer
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Solves system reliability issues where AI hallucinations break the application with incorrect parameters.
    *   *How it works:* Defines a strict input schema utilizing Nitrostack's end-to-end type safety via Zod validation. Bad parameters are intercepted by Nitrostack's middleware pipeline (Guards, interceptors, pipes, exception filters).
    *   *MCP Primitive Leveraged:* Zod Validation & Middleware.
    *   *Roadmap Tasks:* Define strict validation schemas utilizing Zod; set up server middleware layers to catch validation failures, analyze payload issues, and autonomously self-correct the parameters in the background.
*   **Working Status:** **Planned (Roadmap)**
*   **Python File:** N/A
*   **Test File / Cases:** N/A

### 18. Enterprise Identity Sandbox
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Solves corporate security fears of a rogue AI executing unauthorized commands.
    *   *How it works:* Locks down powerful MCP Tools by leveraging Nitrostack's JWT, OAuth 2.1, and API key authentication out of the box.
    *   *MCP Primitive Leveraged:* Built-in Auth Modules & Guards.
    *   *Roadmap Tasks:* Configure JWT authentication guards for the server; verify user identity and active session permissions prior to triggering file system write or setup tools.
*   **Working Status:** **Planned (Roadmap)**
*   **Python File:** N/A
*   **Test File / Cases:** N/A

### 19. Dependency Injection Profiler
*   **Domain:** Domain 1 (Open Source Frameworks)
*   **Description:** Prevents technical debt caused by AI generating unscalable, flat spaghetti code.
    *   *How it works:* Leverages Nitrostack's first-class Dependency Injection container with singleton, transient, and scoped lifecycles.
    *   *MCP Primitive Leveraged:* DI Container & Decorators.
    *   *Roadmap Tasks:* Structure newly generated framework code using clean, declarative TypeScript decorators; configure the scaffolder output to follow dependency injection best practices to ensure hyper-scalable system structure.
*   **Working Status:** **Planned (Roadmap)**
*   **Python File:** N/A
*   **Test File / Cases:** N/A

---

## 🎨 Interactive Resources

### 20. Constellation Map Graph (`ideation-goat://canvas`)
*   **Domain:** Domain 3 (Design & UI/UX Synthesis)
*   **Description:** Exposes visual node-and-edge graphs summarizing the last active search query's conceptual layout, cognitive distances, and domain weights. Allows GUI/chat extensions to render interactive constellation visualizers.
*   **Working Status:** **Fully Implemented**
*   **Python File:** `server.py`
*   **Test File / Cases:** N/A (Dynamic JSON-RPC Resource payload verified in manual test runner)
