# 🏛️ Ideation GOAT System Architecture

This document describes the design principles, file structure, and structural layout of the Ideation GOAT repository. It provides developer teams with a clear roadmap of the codebase and explains how the system operates as a production-grade Model Context Protocol (MCP) server.

---

## 🏗️ Architectural Core Principles

Ideation GOAT is built to operate under the following architectural guardrails:
1.  **ReadOnly Execution Boundaries**: Except for the scaffolding module (`scaffolder.py`), all tools, crawlers, and analyzers are strictly read-only on both the local file system and public networks.
2.  **Zero-Configuration / PAT-Free Discovery**: The suite leverages unauthenticated API endpoints, public search indexes, and local AST parsing. Developers can use the entire system with zero setup or tokens.
3.  **Strict Path Traversal Guard**: Scaffolding outputs are validated against the workspace root configuration to prevent arbitrary write vulnerabilities.
4.  **Multiplexed Transport Isolation**: All debugging and runtime logs are routed to `sys.stderr` to keep `sys.stdout` clean for JSON-RPC MCP multiplexing.

---

## 📁 Repository Directory Map

Below is a breakdown of what every file in this repository does.

```
/home/suzaykid/Projects/ideation-goat
├── ARCHITECTURE.md                  <-- [You are here] System architecture guide
├── LICENSE                          <-- License details (GPL-3.0/MIT alignment)
├── README.md                        <-- Core installation and usage guide
├── app.py                           <-- Streamlit browser UI for local search/analysis
├── arxiv_client.py                  <-- arXiv Atom XML API client (with retry backoff)
├── config.py                        <-- Centralized Settings (Chroma paths, API parameters)
├── data_ingestion.py                <-- Ingestion script to crawl GitHub repos into ChromaDB
├── mcp-config.json                  <-- Configuration settings for Claude Desktop
├── orchestrator.py                  <-- Multi-step diagnostic workflow orchestrator
├── patent_client.py                 <-- USPTO PatentsView DSL query engine
├── pyproject.toml                   <-- Project metadata and dependencies configuration
├── repo_profiler.py                 <-- Edge MCU resource profiler & GitHub health telemetry
├── requirements.txt                 <-- Standard python environment dependencies list
├── scaffolder.py                    <-- Safe project bootstrapper with path traversal guards
├── scholar_client.py                <-- Semantic Scholar academic search client
├── search_engine.py                 <-- Target search and Discovery mode with similarity filter
├── server.py                        <-- Primary MCP Server entrypoint (exposes resources/tools)
├── tests/                           <-- Test suite directory
│   ├── test_addons.py               <-- Terminal helper script to run tools manually
│   └── test_server.py               <-- Offline test suite (23 unit tests covering all modules)
├── uv.lock                          <-- Lock file for fast, reproducible UV environment
├── workspace_analyzer.py            <-- Local compatibility scorecards & structural aligner
└── analyzers/
    ├── bug_profiler.py              <-- TF-IDF issue landscape and chronic pitfalls classifier
    ├── compatibility_scorer.py      <-- Scoring utility comparing language/licensing weights
    ├── github_public_api.py         <-- Internal utility helper for fetching public repo files
    ├── health_analyzer.py           <-- OSV.dev CVE scanner and repo vitality analyzer
    ├── lockin_profiler.py           <-- Deep dependency tree proprietary cloud scan
    └── workspace_analyzer.py        <-- Local configuration and import AST-parser
```

---

## 🔍 Module Responsibilities & Core Code Flows

### 1. The Entrypoint & Server Routing
*   **File:** `server.py`
*   **Role:** Initializes the `FastMCP("IdeationGOAT")` server. Exposes all endpoints as MCP tools or resources. Routes inputs, coordinates tasks, and handles global exception trapping.

### 2. Multi-Domain Search & Matching
*   **Files:** `search_engine.py`, `arxiv_client.py`, `scholar_client.py`, `patent_client.py`
*   **Role:**
    *   `search_engine.py` manages target-specific queries (combining ChromaDB search and academic paper feeds) and discovery-mode queries (which filter out `cs.*` categories using the *Inverse-Similarity Filter* to discover cross-domain analogies).
    *   The clients implement backoff logic and parse XML/JSON responses cleanly.

### 3. Local Workspace Profiling
*   **Files:** `workspace_analyzer.py`, `analyzers/workspace_analyzer.py`
*   **Role:**
    *   Inspects files in the workspace (read-only) using lightweight AST parsing (searching for imports like `react`, `express`, `fastapi`, etc.) and checking package configurations.
    *   Compares the local stack with the target repository language and license rules (`verify_workspace_fit`).
    *   Identifies the workspace layout structure (MVC, Hexagonal, Clean) and prints architectural integration instructions (`align_system_architecture`).

### 4. Telemetry, Vulnerability, and Risk Analyzers
*   **Files:** `repo_profiler.py`, `analyzers/health_analyzer.py`, `analyzers/lockin_profiler.py`, `analyzers/bug_profiler.py`
*   **Role:**
    *   `repo_profiler.py` queries GitHub and OSV.dev and estimates SRAM/Flash weights.
    *   `health_analyzer.py` audits open-source vitality and security (OSV.dev).
    *   `lockin_profiler.py` scans dependencies recursively to check for proprietary lock-in.
    *   `bug_profiler.py` runs clustering analyses on the last 100 bug issues to identify recurring operational hurdles.

### 5. Workspace Integration Scaffolder
*   **File:** `scaffolder.py`
*   **Role:** Generates code files (`README.md`, `math_engine.py`, `state_buffer.py`, `requirements.txt`) containing the integration structures. Validates that paths are subdirectories of `WORKSPACE_ROOT` to prevent arbitrary write vulnerabilities.

### 6. Workflow Orchestration
*   **File:** `orchestrator.py`
*   **Role:** Coordinates and sequences all analytical steps (AST check, repository matching, vitality/OSV health audit, ecosystem lock-in scanning, chronic bug profiling, compatibility check, edge microcontroller sizing, and code scaffolding) into a single unified analysis pipeline.

---

## 🧪 Testing Infrastructure
*   **File:** `tests/test_server.py`
*   **Role:** Validates all MCP endpoints and class functionalities offline. Mocking and intercepting network calls allow the entire test suite to execute in under 4 seconds.

---

## 🧼 Clean Coding Standards & Expected Structure

To maintain the professionalization, reliability, and security of the Ideation GOAT server, all developers must adhere to the following coding standards and architectural guidelines:

### 1. File & Directory Conventions
*   **Logical Separation of Concerns (SoC):** Core tool routing resides in `server.py`. Unified diagnostic sequencing resides in `orchestrator.py`. Domain-specific analytical scanners reside inside the `analyzers/` directory as standalone, decoupled modules. All external network/API communication wrappers are placed in dedicated `_client.py` files.
*   **Zero Duplication:** Shared utility helpers (e.g., fetching files from GitHub or local parser helpers) must be centralized in helper modules like `analyzers/github_public_api.py` or configured inside `config.py`.

### 2. Defensive Coding & File System Access
*   **Strict Security Boundaries:** Write operations (such as in `scaffolder.py`) must be restricted to a configured `WORKSPACE_ROOT` to prevent arbitrary file write vulnerabilities. Always enforce validation checks using `os.path.commonpath`.
*   **Unprivileged Execution:** All tool handlers, analyzers, and resource providers must default to read-only access. Write actions must be isolated strictly to scaffolding tools.
*   **Stdio Sanitization:** Never print debugging, info, or error messages directly to `sys.stdout`. The standard output stream is reserved exclusively for JSON-RPC MCP messages. All logging must route to `sys.stderr` using the unified `logging` module.

### 3. Self-Documenting Requirements
*   **Module Docstrings:** Every Python module must begin with a clear docstring summarizing its purpose, execution role, and structural design.
*   **Function Docstrings:** Every public function and method must implement detailed docstrings documenting the purpose, parameters, return values, and potential exceptions:
    ```python
    def parse_manifest(file_path: str) -> dict:
        """Parses a package manifest file to extract dependency names.

        Args:
            file_path: The absolute path to the package manifest file.

        Returns:
            A dictionary mapping package names to version strings.

        Raises:
            FileNotFoundError: If the manifest does not exist.
        """
    ```
*   **Inline Comments:** Write comments explaining *why* a particular block of code exists or why a specific heuristic was chosen, rather than explaining *what* the syntax is doing.

### 4. Robust Error Handling & API Backoffs
*   **Graceful Degradation:** The server must operate offline-first. If external APIs (GitHub, arXiv, OSV.dev) fail or are rate-limited, the tools must handle the failure gracefully (returning structured error summaries or falling back to local mock data) rather than throwing uncaught exceptions.
*   **Backoff Retries:** Remote network requests must utilize exponential backoff retry patterns (configured in `config.py`) to bypass transient network hiccups safely.

### 5. Test-Driven Verification
*   **Offline-First Testing:** Every public-facing tool, resource, or helper method must be covered by a unit test in `tests/test_server.py`.
*   **Mocking:** Leverage `unittest.mock` to mock all external network calls and filesystems. The test suite must run quickly, offline, and require no API tokens.

