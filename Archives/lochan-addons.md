# NitroForge: Zero-Friction Architectural Analytics
## Feature Specification Report

### 1. Strategic Overview
This report details the technical implementation for four high-impact, zero-friction MCP tools. By eliminating the need for GitHub Personal Access Tokens (PATs) and write permissions, NitroForge shifts from a basic search utility to an advanced **Architectural Consultant**. These features leverage standard API reads and local workspace parsing to deliver massive developer value right inside the Antigravity IDE, acting as a preventative shield against technical debt.

---

### 2. Feature 1: Workspace AST Compatibility Analyzer
**The Core Problem:** Recommending a backend framework based purely on semantics is useless if adopting it requires rewriting the user's entire existing local architecture. 

**The Innovation:** A zero-friction local context engine. Instead of a blind search, the MCP server uses a local read-only tool to inspect the user's currently open project. By parsing local files (like `package.json`, `tsconfig.json`) and mapping local TypeScript Abstract Syntax Trees (AST), the AI understands the user's exact current stack without needing complex meta-prompts or manual file management.

*   **Data Source:** Local file system (read-only execution via the MCP tool), traversing local dependency graphs.
*   **Execution:** The AI cross-references the local AST mapping against the target GitHub repository's semantic requirements.
*   **Output Widget:** A **"Compatibility Scorecard"** rendered natively in the chat using `@nitrostack/widgets`. It explicitly tells the user: *"This repo matches your idea perfectly, but I see you are using Express locally, and this repo relies on Fastify. Here is the exact migration adapter snippet you will need."*

---

### 3. Feature 2: Open-Source Health & Tech Debt Risk Index
**The Core Problem:** A repository might have a high semantic match based on a brilliant README, but if it contains unpatched CVEs, malicious preinstall scripts, or abandoned code, it is a massive liability.

**The Innovation:** An automated supply-chain risk auditor. Before recommending any framework, the tool silently queries public, unauthenticated APIs to audit the framework's security posture, dependency vulnerabilities, and maintainer health. 

*   **Data Source:** Public vulnerability databases (like OSV.dev) and the public GitHub API for commit velocity and issue resolution rates.
*   **Execution:** The tool evaluates the dependency tree for known supply chain risks, flagging things like typosquatting attempts, malicious scripts, and stale codebases (e.g., 0 commits in 18 months).
*   **Output Widget:** A **"Risk & Health Index"** badge. If the risk is too high, the agent intercepts the recommendation: *"Repo X is a 99% semantic match, but it has 14 critical open security issues and hasn't been patched in a year. Recommending Repo Y instead."*

---

### 4. Feature 3: The "Ecosystem Lock-In" Profiler
**The Core Problem:** Developers frequently adopt open-source frameworks that secretly force them into specific proprietary ecosystems (e.g., AWS-only SDKs, Vercel-specific edge runtimes), severely limiting future hosting flexibility.

**The Innovation:** A deep-tree dependency scanner that evaluates long-term portability. The MCP tool analyzes the framework's dependency tree and documentation to identify hard integrations with proprietary cloud providers.

*   **Data Source:** Public registry data (e.g., npm) and deep dependency tree analysis via standard APIs.
*   **Execution:** The tool recursively checks for ecosystem-specific imports that would prevent standard Linux or containerized Docker deployments.
*   **Output Widget:** A **"Portability Grade"** (A through F) displayed on the framework's card. The agent warns the user: *"This framework earns a Grade C for portability. It heavily imports proprietary serverless adapters, meaning migrating to a self-hosted environment later will require a major architectural rewrite."*

---

### 5. Feature 4: Chronic Bug Profiler (Issue Landscape Analyzer)
**The Core Problem:** A framework's README highlights its best features but hides its recurring structural flaws. A repository might be highly starred but plagued by memory leaks or breaking state bugs that only appear once a developer is already deeply invested in production.

**The Innovation:** A semantic issue-clustering engine. Instead of a developer manually reading hundreds of GitHub issues to gauge stability, the MCP tool dynamically fetches recent bug reports and runs a rapid clustering analysis to identify chronic, repeating pain points.

*   **Data Source:** Public GitHub Issues API (unauthenticated read fetching the last 100 closed/open bug reports) and LLM-driven semantic clustering.
*   **Execution:** The tool aggregates issue titles and labels, searching for high-frequency complaint patterns (e.g., recurring mentions of "hydration mismatch," "memory leak during SSR," or "router crash on rapid clicks").
*   **Output Widget:** A **"Known Pitfalls"** warning banner. The agent alerts the user before adoption: *"Proceed with caution: 22% of recently opened issues for this framework are related to 'WebSocket connection drops under high load'. Given your distributed chat app idea, this could be a critical blocker."*

---

### 6. Implementation for the NitroStack Hackathon
These four features perfectly align with the hackathon's judging criteria by proving complex, stateful data synthesis. All features will be implemented as `@Tool` decorators with strict Zod validation schemas. By keeping operations strictly read-only (local files and public APIs) and delegating UI rendering to `@nitrostack/widgets`, we completely remove all authentication friction for the end user, ensuring a flawless, zero-setup demo experience for the judging panel.
