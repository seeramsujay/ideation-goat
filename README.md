<div align="center">
  <img src="logo.png" alt="Ideation Goat Logo" width="200" height="200">
  <h1>Ideation GOAT</h1>
  <p><strong>Cross-Domain Cross-Pollination & Ideation Engine for AI Agents</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/MCP-FastMCP-purple.svg" alt="MCP">
    <img src="https://img.shields.io/badge/License-GPL--3.0-green.svg" alt="License">
  </p>
</div>

---

## What It Is

Ideation GOAT is a production-grade Model Context Protocol (MCP) server that acts as the creative subconscious of advanced AI agents. It performs cross-domain knowledge hybridization, academic paper mapping, local compatibility scorecards, vendor cloud lock-in audits, and secure codebase scaffolding. 

The server outputs structured JSON payloads and architectural specification reports that coding agents can immediately ingest and execute.

---

## 🛠️ MCP Tools Exposed

Ideation GOAT exposes **14 core developer diagnostics and cross-pollination tools** under `server.py`:

| Tool / Name | Inputs | Description |
| :--- | :--- | :--- |
| **`search_knowledge_grid`** | `query`, `mode`, `cognitive_distance` | Searches local vector DB (ChromaDB), arXiv, and USPTO patents. Supports **Target Mode** (direct precision matches) and **Discovery Mode** (using an *Inverse-Similarity Filter* to discover scientific analogies outside of computer science). |
| **`breed_concepts`** | `concept_a`, `concept_b` | Cross-pollinates two distinct architectural paradigms (e.g., biological processes and server caches) into a single hybrid specification. |
| **`bridge_code_and_theory`** | `target_type`, `payload` | Bidirectionally translates between code implementations and mathematical LaTeX representations. |
| **`check_repo_health`** | `owner`, `repo` | Fetches PR response times, commit velocity, and queries OSV.dev to scan the latest commit SHA for known vulnerabilities (CVEs). |
| **`get_repo_health`** | `owner`, `repo` | Retrieves an aggregated repository vitality and momentum report over the past 3 years. |
| **`analyze_workspace_ast`** | `workspace_path` | Offline AST scan of project manifest configurations (`package.json`, `requirements.txt`, etc.) and import statements to detect active languages and dependencies. |
| **`verify_workspace_fit`** | `workspace_path`, `target_repo` | Audits licenses, package compatibility, and programming languages between the local workspace and a proposed GitHub repository. |
| **`check_ecosystem_lockin`** | `owner`, `repo` | Scans a repository's imports to identify hard cloud vendor lock-in (AWS, GCP, Vercel) and computes a Portability Grade (A to F). |
| **`analyze_repo_bugs`** | `owner`, `repo` | Gathers GitHub issue logs and clusters them using keyword analysis to report recurring chronic operational bugs before adoption. |
| **`profile_repo_hardware_footprint`**| `owner`, `repo` | Estimates SRAM/Flash memory footprints and heap allocation weights for edge microcontroller deployments (ESP32, STM32, Arduino). |
| **`align_system_architecture`** | `workspace_path` | Analyzes local folder structure layouts (e.g., Hexagonal, MVC, Clean) and provides matching structural integration advice. |
| **`compose_solution_stack`** | `system_description` | Decomposes a multi-tier system requirement into layers and suggests compatible frameworks. |
| **`search_academic_papers`** | `query` | Executes parallel queries across arXiv and Semantic Scholar to return relevant preprints, citation counts, and abstracts. |
| **`write_scaffolding_files`** | `workspace_path`, `files` | Generates boilerplate files and skeleton structures securely inside the workspace. |
| **`orchestrate_architectural_workflow`**| `query`, `workspace_path` | Coordinates all analytical scans (AST, compatibility, lock-in, bugs, hardware sizing, vulnerability checks, and project scaffolding) in a single-pass execution pipeline. |

---

## 🏛️ System Architecture

```
         AI Agent (Claude Desktop, Cursor, or custom swarm)
                                |
                     JSON-RPC over stdio / stdout
                                |
                                v
                       server.py (FastMCP)
                                |
           +--------------------+--------------------+
           |                                         |
     Tools Layer                               Resources Layer
 (14 Analytical Tools)                    (ideation-goat://canvas)
           |                                         |
           v                                         v
   orchestrator.py                             search_engine.py
 (Unified Diagnostics)                      (ChromaDB / Vector Map)
           |
           +---> analyzers/ (AST, lock-in, bugs, health, compatibility)
           +---> scaffolder.py (Protected file writing)
           +---> _client.py (arXiv, Scholar, Patent APIs)
```

---

## ⚖️ Ethical Coding Principles & Privacy Safeguards

Ideation GOAT is built to respect developer environment integrity and enforce ethical coding practices:

1.  **Local-First Privacy Guard:** Codebase analysis (such as AST scanning and import parsing) runs entirely locally and offline. Your source code is never transmitted to external APIs or training pipelines.
2.  **Strict File System Boundaries:** The scaffolding tool implements strict directory traversal checks. Write operations are restricted strictly within the user-authorized workspace directory, protecting systemic operating files.
3.  **No Unverified Third-Party Imports:** The engine does not download executable packages autonomously. It identifies and scores dependency trees so developers can make informed installation decisions.
4.  **Copyleft License Guardrail:** The system proactively flags copyleft licenses (such as GPL/AGPL) if it detects integration with closed-source commercial workspaces, protecting projects from legal contagion.
5.  **API Rate-Limit Etiquette:** Connections to public APIs (arXiv, Semantic Scholar, GitHub, OSV.dev) use caching, exponential backoff, and unauthenticated endpoints to avoid resource abuse and rate limits.
6.  **Ecosystem Portability Advocacy:** The server actively identifies proprietary cloud vendor lock-in to help developers maintain technical sovereignty and build platform-agnostic software.

---

## 📦 Installation & Setup

To ensure isolation from your global Python environment, Ideation GOAT standardizes on the Python virtual environment (`venv`) and package manager (`pip`).

### 1. Clone the Repository
```bash
git clone https://github.com/suzaykid/ideation-goat.git
cd ideation-goat
```

### 2. Create a Virtual Environment
Create an isolated virtual environment named `.venv` in the project root:
```bash
python -m venv .venv
```

### 3. Activate the Environment
Activate the environment depending on your operating system:

*   **macOS / Linux:**
    ```bash
    source .venv/bin/activate
    ```
*   **Windows (Command Prompt):**
    ```cmd
    .venv\Scripts\activate.bat
    ```
*   **Windows (PowerShell):**
    ```powershell
    .venv\Scripts\Activate.ps1
    ```

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

Ideation GOAT includes a comprehensive unit testing suite that uses mocks to run completely offline without requiring internet access or API credentials.

Run the test suite using standard Python:
```bash
.venv/bin/python -m unittest discover -s tests
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
