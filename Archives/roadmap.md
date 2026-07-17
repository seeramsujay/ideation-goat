# **Ideation Goat: Development Roadmap**

This roadmap takes the project from a local prototype to a scalable, production-ready web application. It follows a "Lean" approach: build the core value first, then scale the infrastructure.

## **Phase 1: The Local Prototype (MVP)**

**Timeline:** 1-3 Days  
**Goal:** Prove that semantic search yields better results than keyword search on a small scale.

* **Step 1: The Script (Done)**  
  * Use the Streamlit \+ ChromaDB Python script to establish the baseline.  
* **Step 2: API Integration Basics**  
  * Register for a GitHub Developer Token.  
  * Install PyGithub to interact with the API.  
* **Step 3: First Real Data Pull**  
  * Write a script to fetch the top 500 most-starred repositories in a specific language (e.g., Python or JavaScript).  
  * Extract: Repository Name, URL, Description, and the first 1000 characters of the README.md.  
* **Step 4: Local Persistence**  
  * Modify ChromaDB in your script to save to disk (chromadb.PersistentClient) so you don't have to re-embed the 500 repos every time you restart the app.

## **Phase 2: Data Pipeline & Cleaning**

**Timeline:** 1-2 Weeks  
**Goal:** Expand the dataset to 5,000+ repositories and improve the quality of the embeddings.

* **Step 1: Text Cleaning (Crucial)**  
  * Write a Python function to parse the README.md files.  
  * *Remove:* Raw code blocks, installation instructions, license text, and badges.  
  * *Keep:* "About", "Features", and "Why use this?" sections.  
* **Step 2: Intelligent Chunking**  
  * If a README is too long, split it into chunks (e.g., 500 words each) and embed them separately, linking them back to the same parent repository.  
* **Step 3: Database Expansion**  
  * Run your ingestion script to pull and embed 5,000 to 10,000 repositories.  
  * Categorize them using GitHub's repository topics/tags as metadata.  
* **Step 4: UI Filters**  
  * Add dropdowns in your Streamlit app to filter by language (e.g., "Only show me Rust frameworks").

## **Phase 3: Cloud Infrastructure & Scaling**

**Timeline:** Weeks 3-4  
**Goal:** Move off your local machine so anyone on the internet can use it without crashing your computer.

* **Step 1: Cloud Vector Database**  
  * Migrate your vector data from local ChromaDB to a hosted solution.  
  * *Options:* Pinecone (generous free tier), Qdrant, or Supabase pgvector.  
* **Step 2: API Backend Development**  
  * Build a dedicated backend API using **FastAPI** (Python).  
  * Create an endpoint (e.g., POST /search) that takes the user's idea, embeds it, queries the cloud vector DB, and returns the JSON results.  
* **Step 3: Better Embeddings (Optional but Recommended)**  
  * Evaluate if the free local MiniLM model is accurate enough.  
  * If not, switch to an API-based model like OpenAI's text-embedding-3-small or Google Vertex AI embeddings for higher semantic accuracy.

## **Phase 4: Production Web App & LLM Synthesis**

**Timeline:** Weeks 5-6  
**Goal:** Build a consumer-facing product with a polished UI and intelligent AI summaries.

* **Step 1: Frontend Migration**  
  * Retire Streamlit for the public-facing app.  
  * Build a modern frontend using React (Next.js) or Vue, styled with Tailwind CSS.  
  * Connect this frontend to your FastAPI backend.  
* **Step 2: LLM Synthesis (The "Magic" Feature)**  
  * Instead of just showing the top 5 repos, pass those 5 repos \+ the user's prompt to an LLM (like Gemini or GPT-4o-mini).  
  * *Prompt the LLM:* "The user wants to build \[Idea\]. Here are the top 5 GitHub frameworks we found. Write a short paragraph explaining which one is the absolute best fit for their specific idea and why."  
  * Display this synthesized answer at the top of the UI.  
* **Step 3: Automation**  
  * Set up a cron job or GitHub Action to run your ingestion script weekly, looking for new trending repositories to automatically add to your Vector DB.

## **Phase 5: Model Context Protocol (MCP) Server Integration**

**Timeline:** Ongoing  
**Goal:** Allow AI clients (like Claude Desktop, Cursor, or custom agents) to semantically query and ingest repositories via standardized tool interfaces.

* **Step 1: Local MCP Server Implementation (Done)**
  * Create `mcp_server.py` using Python's official `mcp` SDK (FastMCP).
  * Expose the core search logic as a reusable tool: `search_repos`.
  * Expose database stats as an MCP resource: `github-ideas://stats`.
* **Step 2: Ingestion Triggering via Tool (Done)**
  * Register the `ingest_repos` tool, allowing AI agents to command the server to fetch and index new programming languages on-demand.
* **Step 3: Client Integration and Testing (Done)**
  * Add configuration documentation for popular LLM clients (such as Claude Desktop config and Cursor).
* **Step 4: Scale to Production SSE Server (Pending)**
  * Migrate the stdio transport to an HTTP SSE (Server-Sent Events) model using FastAPI, enabling remote hosting and multi-tenant AI access to the central search database.

