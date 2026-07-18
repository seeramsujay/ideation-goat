# 🛠️ Multi-Domain Semantic Architect Agent Tool Catalog

This document provides the definitive tool and resource registry for the **Multi-Domain Semantic Architect Agent** (Ideation GOAT) MCP server, mapping all 24 active tools and resources to their respective functional domains, implementation modules, and testing suites.

---

## 🗺️ Multi-Domain Mapping Matrix

The agent bridges three distinct conceptual domains to help developer teams discover, validate, and scaffold software systems.

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
| **Domain 1: Open Source Frameworks & Architecture** | Local stack compatibility, license checks, project health, tech debt, ecosystem lock-in, chronic bugs, CVE vulnerability gates, and codebase scaffolding. | `search_knowledge_grid` (target mode), `verify_workspace_fit`, `analyze_workspace_ast`, `align_system_architecture`, `check_repo_health`, `get_repo_health`, `check_ecosystem_lockin`, `analyze_repo_bugs`, `write_scaffolding_files`, `orchestrate_architectural_workflow`, `forecast_live_costs`, `profile_dependency_injection`, `generate_docker_scaffolding`, `scan_local_cves`, `search_gitlab_repos`, `audit_hacker_news_trends` |
| **Domain 2: Research & Academic Papers** | Bridging software implementations with cutting-edge academic preprints and theoretical/mathematical models. | `search_academic_papers`, `search_knowledge_grid` (discovery mode), `bridge_code_and_theory`, `assess_viability` |
| **Domain 3: Design & Frontend Portfolios** | Concept cross-pollination and interactive React UI components rendering. | `breed_concepts`, and canvas graph mapping resource (`ideation-goat://canvas`). |

---

## 📋 Complete Tool & Resource Registry

The following list contains all 24 fully implemented and active MCP tools exposed by the server.

### 1. Multi-Domain Semantic Queries (`search_knowledge_grid`)
* **Domain:** Domain 1 (Target Mode) / Domain 2 (Discovery Mode)
* **Description:** Interrogates local vector databases (ChromaDB), academic paper search (arXiv), and Google Patents records.
  * `target` Mode: High-precision, direct functional searches for relevant repositories and papers.
  * `discovery` Mode: Uses an **Inverse-Similarity Filter** to exclude direct computer science (`cs.*`) papers. Retrieves parallel concepts in disciplines like quantitative biology or physics, mapping them back as structural analogies.
* **Python Module**: `search_engine.py`, `server.py`

### 2. Concept Hybridization (`breed_concepts`)
* **Domain:** Domain 3 (Design & UI)
* **Description:** Cross-pollinates two distinct architectural paradigms into a single hybrid specification. Generates a custom conceptual bridge, mathematical LaTeX formulas, and a catalyst prompt for client LLMs.
* **Python Module**: `server.py`

### 3. Bidirectional Algorithmic Translation (`bridge_code_and_theory`)
* **Domain:** Domain 2 (Research & Academia)
* **Description:** Translates code snippets into mathematical LaTeX representations (mapping to academic literature) or parses LaTeX formulas to recommend matching software codebase architectures/templates.
* **Python Module**: `server.py`

### 4. Assess Patent Viability (`assess_viability`)
* **Domain:** Domain 2 (Research & Academia)
* **Description:** Evaluates custom software design concepts against active patent filings in Google Patents, outputting potential infringement risks and proposing defensive evasion strategies.
* **Python Module**: `server.py`

### 5. Search Academic Papers (`search_academic_papers`)
* **Domain:** Domain 2 (Research & Academia)
* **Description:** Executes parallel queries across arXiv and Google Scholar databases to return academic literature summaries, authors, URLs, and citation statistics.
* **Python Module**: `search_engine.py`, `server.py`

### 6. Project Scaffolder (`write_scaffolding_files`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Creates skeleton folders and code configurations securely in the workspace. Enforces strict boundary checks to prevent path traversal attacks.
* **Python Module**: `scaffolder.py`, `server.py`

### 7. Workspace Compatibility & License Guard (`verify_workspace_fit`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Audits package managers and license structures of local projects against proposed GitHub repositories. Prevents copyleft licensing conflicts (e.g., commercial MIT code importing AGPL/GPL packages).
* **Python Module**: `workspace_analyzer.py`, `server.py`

### 8. Agentic Stack Composer (`compose_solution_stack`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Decomposes complex multi-layered system descriptions into separate layers (e.g., storage, transport, cryptography) and suggests compatible packages for each.
* **Python Module**: `search_engine.py`, `server.py`

### 9. Get Repository Health (`get_repo_health`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Retrieves an aggregated repository vitality and momentum report over the past 3 years, including star counts, open issues, and telemetry.
* **Python Module**: `repo_profiler.py`, `server.py`

### 10. Edge-Deploy Footprint Profiler (`profile_repo_hardware_footprint`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Profiles structural resource weights of packages and estimates SRAM/Flash footprints against edge microcontrollers (ESP32, STM32, Arduino).
* **Python Module**: `repo_profiler.py`, `server.py`

### 11. Architectural Pattern Aligner (`align_system_architecture`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Profiles local workspace folder layouts to detect design patterns (Hexagonal, MVC, Clean, Monolith) and outputs integration adaptors/guidance.
* **Python Module**: `workspace_analyzer.py`, `server.py`

### 12. Local Stack AST Scanning (`analyze_workspace_ast`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Zero-friction local AST scan of package manifests (e.g., `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) to discover active frameworks, build systems, and dependencies.
* **Python Module**: `analyzers/workspace_analyzer.py`, `server.py`

### 13. Supply-Chain Security & Vitality Audit (`check_repo_health`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Fetches real-time commit velocity, pull request activity, and open issue ratios to compute an open-source vitality score. Also queries OSV.dev to check for known vulnerability CVEs.
* **Python Module**: `analyzers/health_analyzer.py`, `server.py`

### 14. Ecosystem Lock-In & Portability Profiler (`check_ecosystem_lockin`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Evaluates dependencies to identify hard vendor lock-in with proprietary cloud suites (AWS, Vercel, GCP, Azure, Cloudflare) and assigns a Portability Grade (A to F).
* **Python Module**: `analyzers/lockin_profiler.py`, `server.py`

### 15. Chronic Bug Profiler (`analyze_repo_bugs`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Gathers open/closed bug reports from GitHub, running n-gram keyword grouping and clustering to identify recurring structural pitfalls before developer adoption.
* **Python Module**: `analyzers/bug_profiler.py`, `server.py`

### 16. Unified Workflow Orchestration (`orchestrate_architectural_workflow`)
* **Domain:** Domain 1 (Open Source Frameworks) & Domain 2 (Research)
* **Description:** Runs an end-to-end multi-step diagnostic sequence. It aggregates workspace AST parsing, target repo search, dynamic stack layering, vulnerability telemetry scans, cloud lock-in audits, chronic bug profiling, hardware footprint checks, and directory scaffolding.
* **Python Module**: `orchestrator.py`, `server.py`

### 17. Live Cost Forecaster (`forecast_live_costs`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Estimates monthly cloud service fees (AWS, Vercel, Supabase, Neon) based on request traffic.
* **Python Module**: `analyzers/cost_forecaster.py`, `server.py`

### 18. Autonomous Schema Auto-Healer (`auto_heal_parameters`)
* **Domain:** Core Utility
* **Description:** Intercepts and self-corrects parameter type mismatches, missing defaults, and option choices/typos generated by LLMs.
* **Python Module**: `analyzers/schema_healer.py`, `server.py`

### 19. Enterprise Identity Sandbox (`verify_identity_token`)
* **Domain:** Core Utility
* **Description:** Controls execution permissions by validating signed JWT authentication credentials and authorized permission scopes.
* **Python Module**: `analyzers/identity_sandbox.py`, `server.py`

### 20. Dependency Injection Profiler (`profile_dependency_injection`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Scores codebase modularity and coupling patterns, highlighting tight constructor dependencies.
* **Python Module**: `analyzers/di_profiler.py`, `server.py`

### 21. "Works Anywhere" Synthesizer (`generate_docker_scaffolding`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Automates environment setup by generating container and config file templates (Dockerfile, docker-compose.yml, .env.example) tailored to the project framework.
* **Python Module**: `scaffolder.py`, `server.py`

### 22. CVE Security Shield (`scan_local_cves`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Performs dependency vulnerability scanning using OSV.dev APIs with severity-based execution gates.
* **Python Module**: `analyzers/cve_shield.py`, `server.py`

### 23. Search GitLab Repos (`search_gitlab_repos`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Queries the GitLab projects registry for repositories matching search intent.
* **Python Module**: `orchestrator.py`, `server.py`

### 24. Audit Hacker News Trends (`audit_hacker_news_trends`)
* **Domain:** Domain 1 (Open Source Frameworks)
* **Description:** Scans Hacker News titles and comments for developer sentiment and mention trends.
* **Python Module**: `orchestrator.py`, `server.py`

---

## 🎨 Interactive Resources

### Constellation Map Graph Resource (`ideation-goat://canvas`)
* **Domain:** Domain 3 (Design & UI)
* **Description:** Exposes visual node-and-edge graphs summarizing the last active search query's conceptual layout, cognitive distances, and domain weights, enabling frontend renderers to draw interactive constellation visualizers.
* **Python Module**: `server.py`
