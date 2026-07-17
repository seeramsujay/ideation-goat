# Nitrostack MCP Semantic Discovery Suite: Feature Specification Report

This specification details the technical implementation of five high-impact, context-aware Model Context Protocol (MCP) tools for the **Semantic GitHub Idea Matcher**. Built as native plugins for the **Nitrostack Agentic AI Framework**, these tools transition the server from a static framework search engine into an active, defensive, and edge-ready architectural copilot.

By combining read-only local workspace parsing with public, real-time metadata queries, this suite protects developers from technical debt, compliance issues, hardware overruns, and structural rot during active agent sessions.

---

## 1. Workspace Compatibility & License Guard (`verify_workspace_fit`)

### A. Core Problem
AI agents can match semantic intent against open-source repositories but remain blind to the local developer environment. If an agent blindly pulls in a library under a highly restrictive copyleft license (such as GPL-3.0 or AGPL-3.0) into a proprietary commercial project, it exposes the business to severe legal risk. Furthermore, attempting to install Python dependencies into a Node.js-specific workspace breaks build pipelines and wastes compute resources.

### B. Technical Mechanics
This tool executes a localized directory scan to determine the active project type, language ecosystem, and licensing framework before recommending any third-party software.
*   **Data Sourcing:** Local file system (read-only execution via the local MCP context), parsing core project manifests such as package.json, requirements.txt, Cargo.toml, go.mod, or local LICENSE files.
*   **Execution:** The tool extracts local environment constraints, detects active project licenses, and cross-references them against the target GitHub repository's semantic metadata.
*   **MCP Primitive Leveraged:** Tool / Resource.

### C. Final Outcome
The agent receives a clear, deterministic compatibility scorecard. If a license conflict or language mismatch is detected, the agent proactively alerts the user with warnings (e.g., "GPL-3.0 conflict detected within proprietary MIT workspace") and pivots the search to alternative, permissive frameworks like Apache-2.0 or MIT.

---

## 2. Agentic Stack Composer (`compose_solution_stack`)

### A. Core Problem
Complex user requirements rarely map to a single repository. If a developer asks to build a "secure, local-first offline mobile application with real-time syncing," a simple semantic search engine will only suggest one component (like an offline database). The developer is left to manually discover, evaluate, and integrate the networking, security, and state-management layers themselves.

### B. Technical Mechanics
This orchestrator intercepts broad, multi-layered product ideas, breaks them down into atomic architectural requirements, and queries the vector database in parallel to assemble a unified technology stack.
*   **Data Sourcing:** High-dimensional semantic vectors queried from the cloud-hosted vector index (Pinecone/Supabase) containing clean, pre-chunked repository README data.
*   **Execution:** The tool runs a lightweight local semantic parsing pipeline to isolate technical layers (e.g., Storage, Cryptography, Transport). It triggers parallel vector searches for each isolated layer and verifies mutual compatibility using dependency rules.
*   **MCP Primitive Leveraged:** Tool.

### C. Final Outcome
Instead of suggesting a single isolated framework, the agent delivers a complete "Architectural Solution Stack Blueprint." It guides the developer through a unified setup: "Use SQLCipher for local database encryption, Libsodium for cryptographic transport, and WatermelonDB for offline-syncing."

---

## 3. Real-Time "Pulse & Health" Telemetry (`get_repo_health`)

### A. Core Problem
Vector embeddings look at the textual semantic meaning of a repository's description or README, which is highly static. A repository might have a brilliantly written landing page describing a revolutionary utility, but the codebase itself could be abandoned, full of unpatched CVE vulnerabilities, or plagued with hundreds of unaddressed issues. 

### B. Technical Mechanics
This telemetry engine layers real-time community and maintenance vitality metrics over the static vector search scores, ensuring the developer does not build critical infrastructure on top of dead software.
*   **Data Sourcing:** Live, unauthenticated public GitHub API endpoints and open vulnerability databases (such as OSV.dev).
*   **Execution:** The tool fetches live project health metadata (e.g., time since last commit, average issue resolution velocity, PR closure rates, star velocity, and open vulnerability notices). It calculates a dynamic Vitality Score that modifies the final semantic ranking.
*   **MCP Primitive Leveraged:** Tool / Resource.

### C. Final Outcome
If a semantic match is identified as high-risk, the agent intervenes with a visual warning: "Although Repo X is a 95% semantic match, it has had 0 commits in the past 18 months and contains 3 critical open CVEs. Recommending Repo Y instead, which maintains a 92% semantic match and a high-vitality active maintenance score."

---

## 4. Edge-Deploy Resource & Footprint Profiler (`profile_repo_hardware_footprint`)

### A. Core Problem
AI coding assistants excel at writing web-scale code, but they are notoriously bad at understanding physical, low-level hardware constraints. If a developer is building firmware or edge applications for resource-constrained IoT nodes (such as an ESP32, STM32 microcontroller, or bare-metal Cortex-M board), they cannot afford heavy, bloated, or library-dense frameworks that expect a full Unix-like environment.

### B. Technical Mechanics
This tool analyzes physical and structural resource requirements of matched open-source codebases, cross-referencing them against target edge hardware constraints provided by the user.
*   **Data Sourcing:** Matched repository dependency trees, language-specific compiled package weight estimates, and target MCU/RTOS physical specifications.
*   **Execution:** The tool checks the package structure for heavy external dependencies, platform-specific OS imports (like POSIX thread requirements), and approximates the physical SRAM/DRAM and Flash footprint.
*   **MCP Primitive Leveraged:** Tool / Resource.

### C. Final Outcome
The agent proactively prevents compile-time and runtime hardware crashes. If a developer attempts to use a memory-heavy library on an ESP32, the profiler flags the issue: "Target SRAM limit of 520KB will be exceeded by this library (est. heap requirements: 600KB). Recommending a bare-metal optimized, ultra-thin C/C++ alternative instead."

---

## 5. Architectural Vector "Drift" Alert Engine (`align_system_architecture`)

### A. Core Problem
As a software project grows, it must adhere to strict, unified architectural patterns (such as Clean Architecture, MVC, Domain-Driven Design, or Hexagonal Architecture). AI agents routinely introduce technical debt by importing third-party libraries that rely on conflicting structural paradigms (for instance, trying to run active-record monolithic mapping libraries inside a decoupled, port-and-adapters clean architecture structure).

### B. Technical Mechanics
This static-analysis analyzer maps the design patterns of both the active local workspace and the proposed open-source library, alerting the agent to potential architectural clashes.
*   **Data Sourcing:** Local directory tree structures and structural project layouts analyzed via read-only local workspace parsing.
*   **Execution:** The tool converts the local directory and dependency topology into an architectural vector model. It compares this model against standard architectural pattern templates and evaluates how the target matched repository expects to be integrated.
*   **MCP Primitive Leveraged:** Tool.

### C. Final Outcome
The agent is guided to act as an elite systems architect. Instead of blindly writing coupled code, it issues a design alert: "This workspace uses Hexagonal Architecture. Directly importing this database library will violate your domain-layer isolation. I will structure the integration by placing the framework inside a custom repository adapter under your infrastructure layer."
