# 🛠️ Sujay Addons & Reference Guide

This file tracks the project credentials, workspace modifications, and reference commands for **Ideation GOAT**.

---

## 👤 Git Configuration
The local Git credentials for this repository have been configured as follows:
* **Username:** `seeramsujay`
* **Email:** `sujayat2007@gmail.com`

---

## 🏗️ Architectural Transition Reference
The project has shifted from a visual Streamlit application to a pure **Model Context Protocol (MCP) Server** running over standard input/output (`stdio`).

### 📦 Files Reorganized
* **`server.py`**: The active entrypoint of the Ideation GOAT MCP server.
* **`app.py`**: Deleted (Streamlit UI components discarded).
* **`mcp_server.py`** $\rightarrow$ `Archives/mcp_server_v1.py`: Archived the original local indexing MCP server.

---

## 📊 Active MCP Resources

### 1. `ideation-goat://canvas`
* **Purpose**: Exposes graph node-and-edge constellation map metadata for the last executed search.
* **Visual Structure**: 
  * `nodes`: Contains the query center-point, precision code repositories (colored blue), and cross-domain paper/biological analogs (colored green).
  * `edges`: Connects nodes with `tension_distance` based on calculated cognitive distance.

---

## 🤖 Active MCP Tools Reference

### 1. `search_knowledge_grid`
* **Purpose**: Query the multi-domain knowledge grid across GitHub repos, arXiv papers, and Patent databases.
* **Modes**:
  * `target`: High-precision direct functional matching. Queries local ChromaDB repos and calls the **live arXiv API** for domain-specific papers.
  * `discovery`: Deep cross-domain analogical matching. Integrates the **Inverse-Similarity Filter** to discard computer science research papers (`cs.*` categories) and instead fetches papers from physics, quantitative biology, quantitative finance, math, and matches them to a curated catalog of physical/biological structural analogs (e.g. cephalopod neural decay, leaf venation, hydraulic manifolds).
* **"The Catalyst" Prompt**: In `discovery` mode, returns a custom `bridge_catalyst_prompt` field tailored to your query, prompting the client LLM to synthesize the connection and act as a Conceptual Translator.
* **Parameters**:
  * `query` (str): Search intent.
  * `mode` (str): `"target"` or `"discovery"`.
  * `cognitive_distance` (float): Force factor between `0.0` and `1.0`.

### 2. `breed_concepts`
* **Purpose**: Synthesizes two distinct structural templates from different domains into a hybrid architectural specification.
* **Output**: Returns a `synthesis_payload` including a custom `bridge_catalyst_prompt` and a `mathematical_grafting_formula` (LaTeX) mapped to the parents' operational characteristics.
* **Parameters**:
  * `concept_a` (dict): Title, description, and domain context.
  * `concept_b` (dict): Title, description, and domain context.

### 3. `bridge_code_and_theory`
* **Purpose**: Bidirectional Algorithmic Translation bridge connecting code and mathematical models.
* **Functionality**:
  * **Code $\rightarrow$ Theory**: Parses code snippets (concurrency primitives, eviction queues, network routings) and maps them to LaTeX formulas and live matching arXiv papers.
  * **Theory $\rightarrow$ Code**: Parses LaTeX-heavy equations and maps them to software implementations and codebase templates.
* **Parameters**:
  * `code_snippet` (str, optional): Code block to translate.
  * `latex_formula` (str, optional): LaTeX formula to translate.

### 4. `assess_viability`
* **Purpose**: Evaluates a system design against commercial competitor patterns and active patent claims (e.g., database sharding). Returns precise **semantic vector gaps** and a **defensive evasion strategy** (e.g., time-slice write density sharding rather than content sharding) to design around conflicts.
* **Parameters**:
  * `system_design` (str): High-level system design text.

### 5. `write_scaffolding_files`
* **Purpose**: Automated project bootstrapper. Generates a physical project folder in the workspace containing:
  * `README.md`: Synthesized conceptual spec.
  * `math_engine.py`: A Python module template containing code functions mapped to LaTeX equations.
  * `state_buffer.py`: Core system control logic.
  * `requirements.txt`: Standard environment configuration.
* **Parameters**:
  * `synthesis_output` (dict): Breeding payload from `breed_concepts`.
  * `project_directory` (str): Target folder path.

---

## 🚀 Running the Server Locally

Verify dependencies are installed:
```bash
pip install -r requirements.txt
```

Launch the MCP server in `stdio` mode:
```bash
python server.py
```
