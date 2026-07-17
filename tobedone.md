# 📋 Ideation GOAT Project Backlog & Future Roadmap

This document outlines all outstanding tasks, planned extensions, and engineering targets required to evolve the Ideation GOAT MCP server into a fully productionized, multi-tenant enterprise system.

---

## 🛠️ 1. Infrastructure & Transport Evolution

- [ ] **Transition stdio to HTTP SSE Transport:**
  * Implement a FastAPI wrapper around the existing `FastMCP` server.
  * Configure Server-Sent Events (SSE) for remote, multi-tenant AI client access.
  * Secure the server with CORS policies and API key headers.
- [ ] **State Storage & Session Persistence:**
  * Transition the in-memory Metaphor Canvas data structures into a persistent graph store (e.g., SQLite or Neo4j) to preserve search histories across client sessions.
- [ ] **Telemetry Dashboard Integration:**
  * Connect the Streamlit UI (`app.py`) to the new database/state backend to display real-time usage graphs and system analysis telemetry.

---

## 🚀 2. Implementing the Core Autonomous Capabilities (Roadmap Addons)

This section documents the specifications for implementing the 11 core autonomous capabilities of the Semantic Architect Agent, designed to solve universal developer pain points using the Model Context Protocol (MCP) and the Nitrostack framework.

### 2.1. Dependency Forecaster
*   **Overview:** Recommending a great framework is useless if it breaks the developer's existing codebase. This feature prevents library conflicts before installation.
*   **How it works:** The agent reads the user's active `package.json` or `requirements.txt` file from their local environment.
*   **MCP Primitive Leveraged:** Resource.
*   **Tasks to Complete:**
    - [ ] Expand package manifest AST scan to analyze transitive dependencies.
    - [ ] Parse deep lockfiles (e.g., `pnpm-lock.yaml`, `poetry.lock`, `package-lock.json`).
    - [ ] Cross-reference the new framework's dependencies against the user's local environment, warning them of potential version conflicts or peer dependency issues.

### 2.2. Live Sentiment Auditor
*   **Overview:** READMEs are marketing documents; the "Issues" tab is where the truth lives. This audits recent GitHub issues for hidden red flags.
*   **How it works:** Fetches the 50 most recent open issues of the semantically matched repository via the GitHub API.
*   **MCP Primitive Leveraged:** Tool.
*   **Tasks to Complete:**
    - [ ] Query GitHub API for the top 50 active open issues.
    - [ ] Integrate a lightweight NLP classifier or simple rule-based sentiment lexicon to detect critical unresolved problems.
    - [ ] Perform rapid sentiment analysis and flag risk in real-time if a repository is currently flooded with critical bugs, proposing runner-up alternatives instead.

### 2.3. License Compliance Checker
*   **Overview:** Accidentally integrating restrictive open-source code into commercial products is a massive real-world legal problem. This acts as a legal guardrail.
*   **How it works:** When pulling repository metadata, the agent specifically extracts the license type.
*   **MCP Primitive Leveraged:** Prompt / Tool.
*   **Tasks to Complete:**
    - [ ] Read legal compliance profile configurations from `config.py` (e.g., commercial vs open source).
    - [ ] Auto-filter or strongly warn against GPL-licensed frameworks if closed-source targets are detected, prioritizing MIT or Apache 2.0 alternatives.

### 2.4. Interactive Health Widget
*   **Overview:** Judges/users suffer from fatigue; a wall of text will not impress them. This displays a visual dashboard of the repository's status for immediate visual impact.
*   **How it works:** Utilizes the `@nitrostack/widgets` package to attach React components directly to the tool's output.
*   **MCP Primitive Leveraged:** Widget.
*   **Tasks to Complete:**
    - [ ] Build React UI component templates using the `@nitrostack/widgets` standard.
    - [ ] Embed SVG/JSON visualizations in standard text messages or custom client-side rendering handlers (e.g., Match Percentage ring chart, live GitHub stars, date of last commit, and a one-click "Install Now" button).

### 2.5. The Longevity Predictor
*   **Overview:** Solves the fear of commitment by answering: "Will this framework die and waste my time?" Developers are terrified of adopting frameworks that maintainers will abandon.
*   **How it works:** Reads a repository's commit velocity, maintainer response time to pull requests, and ecosystem momentum over the last 3 years.
*   **MCP Primitive Leveraged:** Resource.
*   **Tasks to Complete:**
    - [ ] Incorporate star velocity, PyPI/npm download velocity, and monthly active user trends.
    - [ ] Calculate project health/decay indexes and intervene if a community is dying to recommend stable alternatives.

### 2.6. Live Cost Forecaster
*   **Overview:** Solves financial anxiety regarding whether a developer can actually afford to run the suggested architecture. People need financial predictability.
*   **How it works:** Pings live pricing APIs across platforms like AWS, Supabase, Vercel, or NitroCloud.
*   **MCP Primitive Leveraged:** Tool.
*   **Tasks to Complete:**
    - [ ] Integrate public API price scrapers or static SDK tables for major cloud service providers (AWS, Vercel, Supabase, Neon).
    - [ ] Automatically calculate estimated monthly costs based on expected traffic.
    - [ ] Render a Budget Widget showing free tier limits and scaling costs.

### 2.7. The "Works Anywhere" Synthesizer
*   **Overview:** Solves the dreaded "It works on my machine" curse. Environment setup breaks the spirit of engineers; we need universal parity.
*   **How it works:** The agent writes directly to the user's file system to generate virtualization files.
*   **MCP Primitive Leveraged:** Tool.
*   **Tasks to Complete:**
    - [ ] Integrate templates in `scaffolder.py` to write custom `Dockerfile` and `docker-compose.yml` configurations tailored to the selected framework and local environment.
    - [ ] Generate associated environment configurations (e.g. `.env.example`).

### 2.8. CVE Security Shield
*   **Overview:** Solves the fear of sabotage and injecting vulnerabilities during supply chain attacks.
*   **How it works:** Cross-references the matched framework's `package.json` against the National Vulnerability Database (NVD) or GitHub Advisory Database.
*   **MCP Primitive Leveraged:** Tool.
*   **Tasks to Complete:**
    - [ ] Implement a full dependency tree scanner calling OSV.dev for local configurations.
    - [ ] Implement severity-based execution gates: halt scaffolding and pivot if a critical vulnerability is detected.

### 2.9. Autonomous Schema Auto-Healer
*   **Overview:** Solves system reliability issues where AI hallucinations break the application with incorrect parameters.
*   **How it works:** Defines a strict input schema utilizing Nitrostack's end-to-end type safety via Zod validation. Bad parameters are intercepted by Nitrostack's middleware pipeline (Guards, interceptors, pipes, exception filters).
*   **MCP Primitive Leveraged:** Zod Validation & Middleware.
*   **Tasks to Complete:**
    - [ ] Define strict validation schemas utilizing Zod.
    - [ ] Set up server middleware layers to catch validation failures, analyze payload issues, and autonomously self-correct the parameters in the background.

### 2.10. Enterprise Identity Sandbox
*   **Overview:** Solves corporate security fears of a rogue AI executing unauthorized commands.
*   **How it works:** Locks down powerful MCP Tools by leveraging Nitrostack's JWT, OAuth 2.1, and API key authentication out of the box.
*   **MCP Primitive Leveraged:** Built-in Auth Modules & Guards.
*   **Tasks to Complete:**
    - [ ] Configure JWT authentication guards for the server.
    - [ ] Verify user identity and active session permissions prior to triggering file system write or setup tools.

### 2.11. Dependency Injection Profiler
*   **Overview:** Prevents technical debt caused by AI generating unscalable, flat spaghetti code.
*   **How it works:** Leverages Nitrostack's first-class Dependency Injection container with singleton, transient, and scoped lifecycles.
*   **MCP Primitive Leveraged:** DI Container & Decorators.
*   **Tasks to Complete:**
    - [ ] Structure newly generated framework code using clean, declarative TypeScript decorators.
    - [ ] Configure the scaffolder output to follow dependency injection best practices to ensure hyper-scalable system structure.

---

## 🧪 3. Quality Assurance & Tests

- [ ] **Expand Integration Testing:**
  * Write end-to-end integration tests for HTTP SSE transport channels.
  * Add regression tests checking file-writing permissions and path isolation constraints on various operating systems.
