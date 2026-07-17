<div align="center">
  <img src="logo.png" alt="Ideation Goat Logo" width="200" height="200">
  <h1>Ideation Goat</h1>
  <p><strong>Find your next framework or research paper not by keywords, but by <em>original intent</em>.</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Streamlit-1.32+-red.svg" alt="Streamlit">
    <img src="https://img.shields.io/badge/ChromaDB-Vector_DB-purple.svg" alt="ChromaDB">
    <img src="https://img.shields.io/badge/License-GPL--3.0-green.svg" alt="License">
  </p>
</div>

---

## 🧠 The Problem
Traditional search tools rely on keywords. If you search for "fast backend with login", you might miss a revolutionary repository called "HyperVault" simply because it doesn't use your specific keywords in its title or tags. Similarly, finding relevant scientific papers is often hindered by jargon and exact phrasing.

**Ideation Goat** uses Semantic Search (Vector Embeddings) to understand the *meaning* of your request, matching it against the deep technical and theoretical context found in thousands of repository READMEs, Google Scholar profiles, and arXiv papers.

## ✨ Features
- **Semantic Mapping**: Uses the `all-MiniLM-L6-v2` model to map natural language ideas to the high-dimensional vector space of GitHub descriptions and research paper abstracts.
- **Multi-Source Search**: Matches intent against both active open-source software and academic research papers (Google Scholar and arXiv).
- **Persistent Local Intelligence**: Powered by ChromaDB for local vector storage—no cloud required for MVP.
- **Intelligent Ingestion**: A dedicated pipeline that cleans markdown, removes noisy badges, chunks READMEs, and parses paper content to capture the "soul" of an idea.
- **Language Filtering**: Multi-dimensional filtering to find the right tool in the right ecosystem (Python, Rust, etc.).

## 🚀 Getting Started

### 1. Prerequisites (Test Machine)
Ensure you have Python 3.9+ installed on your test machine. Note: This project is designed to run its heavy ML workloads on dedicated lab hardware.

### 2. Installation
```bash
git clone https://github.com/suzaykid/ideation-goat.git
cd ideation-goat
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GITHUB_TOKEN=your_github_personal_access_token
```

### 4. Data Ingestion
Populate your local vector database with real GitHub data:
```bash
python data_ingestion.py
```

### 5. Launch the Matcher
```bash
streamlit run app.py
```

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/)
- **Embeddings**: Sentence-Transformers (Local MiniLM via ONNX - no heavy PyTorch required)
- **API**: [PyGithub](https://github.com/PyGithub/PyGithub)
- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## 🤖 Model Context Protocol (MCP) Integration

You can run this project as a local MCP server, allowing LLM hosts (such as Claude Desktop or Cursor) to call the semantic search database directly.

### Exposed Tools & Resources:
- **`search_repos` (Tool)**: Semantically query repositories using a natural language idea or intent (with optional language filters).
- **`ingest_repos` (Tool)**: Request the crawler to fetch and chunk the top repositories for a specific programming language.
- **`github-ideas://stats` (Resource)**: Query database coverage stats (number of chunks, languages, and repositories).

### Claude Desktop Setup
Add the following configuration to your `claude_desktop_config.json` (usually located at `~/.config/Claude/claude_desktop_config.json` on Linux or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "ideation-goat": {
      "command": "/home/suzaykid/Projects/ideation-goat/.gss/bin/python",
      "args": [
        "/home/suzaykid/Projects/ideation-goat/mcp_server.py"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_personal_access_token"
      }
    }
  }
}
```

## 🗺️ Roadmap
Check our [Archives/roadmap.md](Archives/roadmap.md) for the full vision, including:
- [x] Model Context Protocol (MCP) Local Server
- [ ] Cloud Vector DB Migration (Pinecone/Supabase)
- [ ] LLM Synthesis for "Why this repo fits you"
- [ ] Next.js + Tailwind CSS Production Frontend

## 📄 License
This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.


---

## 🛡️ Licensing & Privacy Protection

Because this repository contains personal code, portfolios, or intellectual property, **strict privacy protections are in place**.

### ⚠️ Prohibitions on AI Training & Scraping
This repository is published for direct human viewing only. Automated data scraping, harvesting, and crawling are strictly prohibited under the author's personal copyright terms.

**By accessing this repository or its contents, you agree to the following terms:**
*   **NO AI/LLM Ingestion:** Any ingestion of code, text, layouts, designs, or assets for training, validation, testing, or tuning of machine learning models, neural networks, or artificial intelligence systems (such as Large Language Models) is strictly prohibited.
*   **NO Automated Data Scraping:** Any automated extraction, parsing, harvesting, or scraping of content by bots, crawlers, scripts, or spiders is prohibited.
*   **Personal Use Only:** Human viewing for personal or educational review is permitted. No duplication, modification, adaptation, or commercial distribution of this work is allowed without express written permission.
