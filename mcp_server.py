import os
import json
import chromadb
from chromadb.utils import embedding_functions
from mcp.server.fastmcp import FastMCP
import data_ingestion

from analyzers.workspace_analyzer import analyze_workspace
from analyzers.compatibility_scorer import score_compatibility
from analyzers.health_analyzer import analyze_repo_health
from analyzers.lockin_profiler import check_ecosystem_lockin as run_lockin_profiler
from analyzers.bug_profiler import analyze_repo_bugs as run_bug_profiler

# Initialize FastMCP Server
mcp = FastMCP("GitHub Idea Matcher & Architectural Consultant")

# Initialize ChromaDB
def get_db():
    client = chromadb.PersistentClient(path="./chroma_data")
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name="github_repos", 
        embedding_function=default_ef
    )
    return collection

@mcp.tool()
def search_repos(query: str, language: str = "All", n_results: int = 5) -> str:
    """
    Semantically search for GitHub repositories based on a natural language idea or intent.
    
    Parameters:
    - query (str): The project idea, intent, or description to match (e.g., 'fast microservices framework with gRPC').
    - language (str): Optional programming language filter (e.g., 'Python', 'Rust', 'JavaScript', 'TypeScript', 'Go', 'All').
    - n_results (int): Number of top matching results to return (default is 5).
    """
    collection = get_db()
    
    # Check if database is empty
    count = collection.count()
    if count == 0:
        return (
            "The GitHub Idea Matcher database is currently empty. "
            "Please run the 'ingest_repos' tool first (e.g. for language='Python') to populate the database."
        )
        
    where_clause = {}
    if language and language.lower() != "all":
        lang_cap = language.capitalize()
        if language.lower() == "javascript":
            lang_cap = "JavaScript"
        elif language.lower() == "typescript":
            lang_cap = "TypeScript"
        where_clause = {"language": lang_cap}
        
    query_args = {
        "query_texts": [query],
        "n_results": n_results
    }
    if where_clause:
        query_args["where"] = where_clause
        
    try:
        results = collection.query(**query_args)
    except Exception as e:
        return f"Error querying database: {str(e)}"
        
    if not results or not results['ids'] or len(results['ids'][0]) == 0:
        return f"No matches found for query '{query}' (Filter: {language})."
        
    output = []
    output.append(f"### 🧠 Semantic matches for: '{query}' (Filter: {language})\n")
    
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        repo_name = metadata.get('name', 'Unknown')
        repo_url = metadata.get('url', '#')
        repo_lang = metadata.get('language', 'Unknown')
        repo_stars = metadata.get('stars', 0)
        matched_text = results['documents'][0][i]
        
        if repo_stars >= 1000:
            stars_str = f"{repo_stars / 1000:.1f}k"
        else:
            stars_str = str(repo_stars)
            
        output.append(f"{i+1}. **[{repo_name}]({repo_url})**")
        output.append(f"   *Language:* `{repo_lang}` | *Stars:* ⭐ {stars_str}")
        output.append(f"   *Matched Context:* {matched_text}")
        output.append("")
        
    return "\n".join(output)

@mcp.tool()
def analyze_workspace_ast(workspace_path: str = None) -> str:
    """
    Zero-friction local workspace AST & dependency analyzer.
    Reads local configuration files (package.json, pyproject.toml, Cargo.toml, go.mod) and scans source imports
    to identify the user's active tech stack without needing external tokens.
    
    Parameters:
    - workspace_path (str): Optional path to the local project directory. Defaults to current working directory.
    """
    profile = analyze_workspace(workspace_path)
    if "error" in profile:
        return f"Error analyzing workspace AST: {profile['error']}"
        
    output = [
        f"### 📁 Workspace AST & Architecture Profile (`{profile['path']}`)",
        f"- **Primary Language Detected:** `{profile['primary_language']}`",
        f"- **All Languages Detected:** `{', '.join(profile['languages_detected']) if profile['languages_detected'] else 'None'}`",
        f"- **Frameworks & Core Libraries:** `{', '.join(profile['frameworks_detected']) if profile['frameworks_detected'] else 'None'}`",
        f"- **Build Tools:** `{', '.join(profile['build_tools']) if profile['build_tools'] else 'None'}`",
        f"- **Total Dependencies Parsed:** {len(profile['dependencies'])} packages (`{', '.join(profile['dependencies'][:15])}...`)"
    ]
    return "\n".join(output)

@mcp.tool()
def check_repo_health(repository: str) -> str:
    """
    Automated supply-chain risk and maintenance health auditor for any GitHub repository.
    Queries OSV.dev vulnerability databases and commit/maintainer activity over unauthenticated/read-only APIs.
    
    Parameters:
    - repository (str): Repository full name (e.g. 'fastapi/fastapi' or 'expressjs/express') or URL.
    """
    health = analyze_repo_health(repository)
    metrics = health.get("metrics", {})
    
    output = [
        f"### 🩺 Open-Source Health & Tech Debt Audit (`{metrics.get('repo', repository)}`)",
        f"- **Composite Health Score:** `{health.get('health_score', 0)} / 100` ({health.get('status', 'Unknown')})",
        f"- **Known OSV.dev Vulnerabilities (CVEs):** `{metrics.get('cve_count', 0)}`",
        f"- **Last Commit / Push Date:** `{metrics.get('last_commit_date', 'Unknown')}`",
        f"- **Active Contributors:** `{metrics.get('contributors_count', 1)}+`",
        f"- **Archived Status:** `{metrics.get('archived', False)}`"
    ]
    
    if health.get("flags"):
        output.append("\n**⚠️ Risk Flags & Warnings:**")
        for flag in health["flags"]:
            output.append(f"- {flag}")
    else:
        output.append("\n✅ *No critical security vulnerabilities or inactivity risks flagged.*")
        
    return "\n".join(output)

@mcp.tool()
def check_ecosystem_lockin(repository: str) -> str:
    """
    Deep dependency tree scanner that evaluates long-term cloud/ecosystem portability.
    Identifies hard lock-in dependencies tied to proprietary cloud platforms (AWS, Vercel, GCP, Azure, Cloudflare).
    
    Parameters:
    - repository (str): Repository full name (e.g. 'fastapi/fastapi' or 'vercel/next.js') or URL.
    """
    lockin = run_lockin_profiler(repository)
    
    output = [
        f"### 🌐 Ecosystem Lock-In & Portability Profile (`{lockin.get('repo', repository)}`)",
        f"- **Portability Grade:** `{lockin.get('portability_grade', 'Unknown')}`",
        f"- **Total Dependencies Evaluated:** `{lockin.get('total_dependencies_checked', 0)}`",
        f"\n**Summary:**\n{lockin.get('summary', '')}"
    ]
    
    locked_deps = lockin.get("locked_dependencies", [])
    if locked_deps:
        output.append("\n**🔒 Locked Vendor Dependencies Found:**")
        for ld in locked_deps:
            output.append(f"- **`{ld['package']}`** → *{ld['vendor']}* ({ld['reason']})")
    else:
        output.append("\n✅ *Zero vendor lock-in dependencies found. Fully portable across self-hosted and multi-cloud environments.*")
        
    return "\n".join(output)

@mcp.tool()
def analyze_repo_bugs(repository: str) -> str:
    """
    Semantic issue-clustering engine that surfaces chronic structural bugs and known pitfalls.
    Fetches recent bug reports and runs TF-IDF / N-gram clustering analysis to find repeating pain points.
    
    Parameters:
    - repository (str): Repository full name (e.g. 'pallets/flask' or 'facebook/react') or URL.
    """
    bugs = run_bug_profiler(repository)
    total_analyzed = bugs.get("total_analyzed_issues", 0)
    
    if total_analyzed == 0:
        return f"Could not fetch sufficient issue reports for `{repository}` (or repository has zero reported bugs)."
        
    output = [
        f"### 🪲 Chronic Bug Profiler & Issue Landscape (`{bugs.get('repo', repository)}`)",
        f"- **Total Recent Issues Analyzed:** `{total_analyzed}`",
        f"- **Overall Bug Risk Level:** `{bugs.get('risk_level', 'Unknown')}`\n",
        "**⚡ Top High-Frequency Pitfalls:**"
    ]
    
    pitfalls = bugs.get("top_pitfalls", [])
    for idx, p in enumerate(pitfalls):
        icon = "🚨" if p.get("is_critical") else "ℹ️"
        output.append(f"{idx+1}. {icon} **{p['label']}** (`{p['percentage']}%` of recent bug reports - {p['count']} occurrences)")
        if p.get("example_issues"):
            output.append(f"   *Examples:* \"{p['example_issues'][0]}\"")
            if len(p['example_issues']) > 1:
                output.append(f"               \"{p['example_issues'][1]}\"")
        output.append("")
        
    return "\n".join(output)

@mcp.tool()
def ingest_repos(language: str = "Python", max_repos: int = 20) -> str:
    """
    Ingest top starred repositories of a specific programming language into the semantic database.
    This runs data ingestion from the GitHub API, retrieves READMEs, chunks/cleans them, and stores embeddings.
    
    Parameters:
    - language (str): Programming language (e.g. 'Python', 'Rust', 'JavaScript', 'TypeScript', 'Go').
    - max_repos (int): Number of top starred repositories to download and process (default: 20).
    """
    lang_cap = language.capitalize()
    if language.lower() == "javascript":
        lang_cap = "JavaScript"
    elif language.lower() == "typescript":
        lang_cap = "TypeScript"
        
    token_present = "yes" if os.getenv("GITHUB_TOKEN") else "no"
    
    try:
        collection = get_db()
        data_ingestion.ingest_data(collection, language=lang_cap, max_repos=max_repos)
        
        count = collection.count()
        return (
            f"Successfully completed ingestion for {lang_cap} (max {max_repos} repos). "
            f"Database now contains {count} chunks in total. "
            f"(GitHub Token present: {token_present})"
        )
    except Exception as e:
        return f"Ingestion failed: {str(e)}"

@mcp.resource("github-ideas://stats")
def get_db_stats() -> str:
    """
    Get statistics about the local vector database.
    """
    try:
        collection = get_db()
        count = collection.count()
        
        results = collection.get(include=["metadatas"])
        languages = set()
        repos = set()
        if results and results.get("metadatas"):
            for meta in results["metadatas"]:
                if meta.get("language"):
                    languages.add(meta["language"])
                if meta.get("name"):
                    repos.add(meta["name"])
                    
        return (
            f"### 📊 GitHub Idea Matcher Database Stats\n\n"
            f"- **Total Semantic Chunks:** {count}\n"
            f"- **Indexed Repositories:** {len(repos)}\n"
            f"- **Languages Available:** {', '.join(languages) if languages else 'None'}"
        )
    except Exception as e:
        return f"Error retrieving stats: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
