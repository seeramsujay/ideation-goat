# Multi-Domain Semantic Architect Agent: The Universal Knowledge Graph

## Overview
The Semantic Architect Agent is officially evolving from a localized GitHub repository matcher into a universal, multi-domain knowledge graph. By leveraging the Model Context Protocol (MCP) via the Nitrostack framework, we are expanding the agent's reach across three distinct domains. This transforms the agent into an end-to-end autonomous assistant capable of handling academic research, codebase scaffolding, and UI/UX design integration.

This document details the three core domains the MCP server operates within, how they solve developer pain points, and how they correlate directly to the concrete tools and roadmap features documented in [addons.md](file:///home/suzaykid/Projects/ideation-goat/docs/addons.md).

---

## Domain 1: Open Source Frameworks & Architecture (The Codebase Matcher)

### What it solves
Developers suffer from decision fatigue and the fear of making bad technical commitments. With thousands of frameworks on GitHub, it is incredibly difficult to know which one is actively maintained, financially viable, and compatible with existing code. This domain solves the "discoverability and dependency" crisis.

### Core Addons & Tools Mapping
*   **Semantic Search Tool (`search_knowledge_grid` - target mode & `compose_solution_stack`):**
    *   *Implementation:* Uses vector databases (like ChromaDB) to map the user's natural language intent to the best-matching GitHub repositories and suggests layered system packages.
    *   *Codebase Reference:* `search_engine.py` (tested via `test_compose_solution_stack` and `test_search_knowledge_grid_target`).
*   **Local Resource Integration & Diagnostic Scans (`analyze_workspace_ast`, `verify_workspace_fit`, `check_ecosystem_lockin`, `analyze_repo_bugs`, `profile_repo_hardware_footprint`):**
    *   *Implementation:* Functions as an offline AST scanner of package manifests, audits copyleft legal compliance, identifies vendor cloud lock-in (AWS/Vercel), clusters recurring bugs/memory leaks, and profiles hardware footprint estimations (SRAM/Flash) for edge controllers.
    *   *Codebase Reference:* `workspace_analyzer.py`, `analyzers/`, and `repo_profiler.py` (tested via AST, fit, lock-in, bug, and hardware unit tests).
*   **Autonomous Scaffolding (`write_scaffolding_files`):**
    *   *Implementation:* Once a framework is selected, the agent utilizes validated write tools to install the boilerplate, configure `.env` files, and generate Docker virtualization containers directly in the local workspace.
    *   *Codebase Reference:* `scaffolder.py` (tested via `test_write_scaffolding_files`).
*   **Unified Workflow Orchestration (`orchestrate_architectural_workflow`):**
    *   *Implementation:* Aggregates AST parsing, search, health telemetry, lock-in scoring, bug clustering, compatibility scoring, sizing, and project scaffolding into a single diagnostic pipeline execution.
    *   *Codebase Reference:* `orchestrator.py` (tested via `test_orchestrate_architectural_workflow_tool`).

---

## Domain 2: Research & Academic Papers (The Literature Matcher)

### What it solves
There is a massive gap between cutting-edge academic research and practical software engineering. Developers building advanced AI, machine learning, or complex algorithmic systems often reinvent the wheel because they cannot easily find, interpret, or implement the latest whitepapers, SOTA (State of the Art) benchmarks, or preprint algorithms.

### Core Addons & Tools Mapping
*   **Academic Search (`search_academic_papers` & `search_knowledge_grid` - discovery mode):**
    *   *Implementation:* Parallel queries across arXiv and Semantic Scholar. In `discovery` mode, it filters out direct computer science (`cs.*`) papers using an **Inverse-Similarity Filter** to discover parallel scientific concepts (e.g. biology, physics) that map back as structural analogies.
    *   *Codebase Reference:* `arxiv_client.py` and `scholar_client.py` (tested via `test_search_academic_papers` and `test_search_knowledge_grid_discovery`).
*   **Research Roadmap Orchestration (Domain 2 Workflow):**
    *   *Implementation:* Executes a three-phase pipeline: (1) Finds academic papers via arXiv and Semantic Scholar; (2) Programmatically extracts required engineering/software frameworks from the literature; (3) Queries Google Patents (via SerpApi) for patents matching those frameworks for deep IP analysis, and then queries GitHub specifically for those framework codebases instead of searching for the broad original query term.
    *   *Codebase Reference:* `orchestrator.py` (`_orchestrate_domain_2` / `_extract_frameworks`).
*   **Concept Hybridization (`breed_concepts`):**
    *   *Implementation:* Cross-pollinates two distinct architectural paradigms into a single hybrid specification, producing a custom conceptual bridge, mathematical LaTeX formulas, and a catalyst prompt for client LLMs.
    *   *Codebase Reference:* `server.py` (tested via `test_breed_concepts`).
*   **Abstract Synthesis & Code Bridging (`bridge_code_and_theory`):**
    *   *Implementation:* Performs bidirectional translation by mapping source code to LaTeX formula representations (and matching literature) or converting mathematical formulas back to matching software template code structures.
    *   *Codebase Reference:* `server.py` (tested via `test_bridge_code_and_theory_code_to_math` and `test_bridge_code_and_theory_math_to_code`).

---

## Domain 3: Design & Frontend Portfolios (The UI/UX Synthesizer)

### What it solves
Backend and full-stack developers frequently struggle with frontend aesthetics. Finding the right inspiration that actually matches a specific modern tech stack (like Tailwind + Framer Motion) is tedious. Developers need a way to bridge the gap between high-end design platforms and functional code generation without hiring a dedicated designer.

### Core Addons & Tools Mapping
*   **Visual-to-Code Map Resource (`ideation-goat://canvas`):**
    *   *Implementation:* Exposes node-and-edge graphs representing the last active search query's conceptual layout, cognitive distances, and domain weights, enabling UI components to render interactive constellation visualizers.
    *   *Codebase Reference:* `server.py`.
*   **Interactive Design Widget (Planned Roadmap):**
    *   *Implementation:* Leveraging `@nitrostack/widgets` to render a visual repository status widget (Match Percentage ring chart, stars, velocity sparklines) directly in the chat interface.
    *   *Codebase Reference:* Mock/structure represented in `app.py`.
