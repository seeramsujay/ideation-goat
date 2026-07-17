import os
import chromadb
from chromadb.utils import embedding_functions
from mcp.server.fastmcp import FastMCP
import data_ingestion
import requests

# Initialize FastMCP Server
mcp = FastMCP("GitHub Idea Matcher")

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
        # standard capitalizations
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
        
        # Star formatting
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
def ingest_repos(language: str = "Python", max_repos: int = 20) -> str:
    """
    Ingest top starred repositories of a specific programming language into the semantic database.
    This runs data ingestion from the GitHub API, retrieves READMEs, chunks/cleans them, and stores embeddings.
    
    Parameters:
    - language (str): Programming language (e.g. 'Python', 'Rust', 'JavaScript', 'TypeScript', 'Go').
    - max_repos (int): Number of top starred repositories to download and process (default: 20).
    """
    # Capitalize correctly
    lang_cap = language.capitalize()
    if language.lower() == "javascript":
        lang_cap = "JavaScript"
    elif language.lower() == "typescript":
        lang_cap = "TypeScript"
        
    # We must ensure GITHUB_TOKEN is set or prompt
    token_present = "yes" if os.getenv("GITHUB_TOKEN") else "no"
    
    try:
        collection = get_db()
        # Trigger ingestion function from data_ingestion module
        data_ingestion.ingest_data(collection, language=lang_cap, max_repos=max_repos)
        
        # Count new database stats
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
        
        # Get unique languages if possible
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

@mcp.tool()
def verify_workspace_fit(repo_name: str, workspace_path: str = ".") -> str:
    """
    Verify if a target GitHub repository is a good technical and legal fit for the local workspace.
    Checks the local project language/ecosystem and license, then compares them against the target repository.
    
    Parameters:
    - repo_name (str): The full GitHub repository name (e.g. 'psf/requests').
    - workspace_path (str): Path to the local workspace to scan (defaults to '.').
    """
    import os
    import json
    
    # 1. Scan local workspace
    detected_languages = set()
    detected_licenses = set()
    
    # Simple check of files in the workspace path (up to 2 levels)
    try:
        for root, dirs, files in os.walk(workspace_path):
            # Prune directories to not go too deep
            if '.git' in dirs:
                dirs.remove('.git')
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
            if '.venv' in dirs:
                dirs.remove('.venv')
            if 'venv' in dirs:
                dirs.remove('venv')
            
            # Check depth
            depth = root[len(workspace_path):].count(os.sep)
            if depth > 2:
                continue
                
            for file in files:
                file_lower = file.lower()
                # Language detection
                if file_lower == 'package.json':
                    detected_languages.add('JavaScript/TypeScript')
                    # Try to extract license from package.json
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'license' in data:
                                if isinstance(data['license'], dict) and 'type' in data['license']:
                                    detected_licenses.add(data['license']['type'])
                                elif isinstance(data['license'], str):
                                    detected_licenses.add(data['license'])
                    except Exception:
                        pass
                elif file_lower in ['requirements.txt', 'poetry.lock', 'pipfile', 'pyproject.toml']:
                    detected_languages.add('Python')
                elif file_lower == 'cargo.toml':
                    detected_languages.add('Rust')
                    # Try to extract license from Cargo.toml
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip().startswith('license'):
                                    parts = line.split('=')
                                    if len(parts) > 1:
                                        lic = parts[1].strip().strip('"').strip("'")
                                        detected_licenses.add(lic)
                    except Exception:
                        pass
                elif file_lower == 'go.mod':
                    detected_languages.add('Go')
                elif file_lower in ['cmakelists.txt', 'makefile']:
                    detected_languages.add('C/C++')
                
                # License file detection
                if file_lower in ['license', 'license.txt', 'license.md', 'copying', 'copying.txt']:
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read(500).lower() # Read first 500 chars
                            if 'mit license' in content or 'mit' in content:
                                detected_licenses.add('MIT')
                            elif 'apache license' in content or 'apache' in content:
                                detected_licenses.add('Apache-2.0')
                            elif 'gnu general public license' in content or 'gpl' in content:
                                if 'version 3' in content:
                                    detected_licenses.add('GPL-3.0')
                                else:
                                    detected_licenses.add('GPL')
                            elif 'bsd' in content:
                                detected_licenses.add('BSD')
                    except Exception:
                        pass
    except Exception as e:
        return f"Error scanning workspace: {str(e)}"
        
    # Default fallback if nothing found
    if not detected_languages:
        detected_languages.add('Not specified')
    workspace_license = 'Proprietary'
    if detected_licenses:
        # Pick the first detected license
        workspace_license = list(detected_licenses)[0]
    
    # 2. Get target repo license and language
    # Initialize Github client
    from github import Github, Auth
    token = os.getenv("GITHUB_TOKEN")
    g_client = Github(auth=Auth.Token(token)) if token else Github()
    
    try:
        repo = g_client.get_repo(repo_name)
        target_lang = repo.language or "Unknown"
        
        # Get target license
        target_license = "Unknown"
        try:
            license_obj = repo.license
            if license_obj:
                target_license = license_obj.spdx_id or license_obj.key or license_obj.name or "Unknown"
        except Exception:
            pass
    except Exception as e:
        return f"Error fetching GitHub repository metadata: {str(e)}"
        
    # 3. Perform compatibility check
    lang_match = False
    for wl in detected_languages:
        if wl.lower() == 'not specified':
            lang_match = True
            break
        # Match python to python, rust to rust, etc.
        if wl.lower() in target_lang.lower() or target_lang.lower() in wl.lower():
            lang_match = True
        elif 'javascript' in wl.lower() or 'typescript' in wl.lower():
            if 'javascript' in target_lang.lower() or 'typescript' in target_lang.lower():
                lang_match = True
                
    # License conflict rules
    copyleft_licenses = ['gpl', 'gpl-3.0', 'gpl-2.0', 'agpl-3.0', 'agpl', 'lgpl', 'lgpl-3.0', 'lgpl-2.1']
    permissive_licenses = ['mit', 'apache-2.0', 'bsd-3-clause', 'bsd-2-clause', 'unlicense', 'cc0-1.0']
    
    is_target_copyleft = any(cl in target_license.lower() for cl in copyleft_licenses)
    is_workspace_permissive = any(p in workspace_license.lower() for p in permissive_licenses) or workspace_license.lower() == 'proprietary'
    
    license_conflict = False
    license_warning = ""
    if is_target_copyleft and is_workspace_permissive:
        license_conflict = True
        license_warning = (
            f"⚠️ **License Conflict Warning**: The workspace license is '{workspace_license}' (permissive/proprietary), "
            f"but the target repo '{repo_name}' uses '{target_license}' (copyleft). "
            f"Integrating copyleft code into a proprietary or permissively licensed workspace "
            f"may force the entire project to be licensed under copyleft terms."
        )
        
    status = "Compatible"
    if not lang_match:
        status = "Language Mismatch"
    if license_conflict:
        status = "License Conflict" if status == "Compatible" else "Conflict & Mismatch"
        
    # Generate report
    output = []
    output.append(f"## 📋 Workspace Compatibility Scorecard for `{repo_name}`")
    output.append("")
    output.append("| Feature | Workspace Environment | Target Repository | Match Status |")
    output.append("| --- | --- | --- | --- |")
    output.append(f"| **Language** | {', '.join(detected_languages)} | {target_lang} | {'✅ Match' if lang_match else '❌ Mismatch'} |")
    output.append(f"| **License** | {workspace_license} | {target_license} | {'⚠️ Copyleft Warning' if license_conflict else '✅ Permissive / Compatible'} |")
    output.append("")
    output.append(f"### **Overall Status**: `{status}`")
    output.append("")
    if license_warning:
        output.append(license_warning)
        output.append("")
    if not lang_match and target_lang != "Unknown":
        output.append(f"⚠️ **Language Mismatch Warning**: Workspace uses `{', '.join(detected_languages)}` but target uses `{target_lang}`. Make sure you can integrate multi-language projects.")
        output.append("")
        
    return "\n".join(output)

@mcp.tool()
def compose_solution_stack(query: str, n_results: int = 3) -> str:
    """
    Decompose a complex system idea into multiple architectural layers and query the database
    to compose a cohesive solution stack of open-source frameworks.
    
    Parameters:
    - query (str): The product idea or requirements (e.g. 'secure local-first mobile app with sync').
    - n_results (int): Number of top matches to find per layer (default: 3).
    """
    collection = get_db()
    
    # Check if database is empty
    count = collection.count()
    if count == 0:
        return "ChromaDB database is empty. Please run ingestion first."
        
    # Standard layers we want to compose
    layers = {
        "Frontend / Client": {
            "keywords": ["ui", "frontend", "mobile", "web", "app", "react", "vue", "flutter", "ios", "android", "client"],
            "subquery": "frontend UI client app mobile web framework user interface"
        },
        "Backend / API": {
            "keywords": ["backend", "server", "api", "routing", "microservice", "http", "grpc", "framework"],
            "subquery": "backend API server web framework routing controller microservice"
        },
        "Database / Storage": {
            "keywords": ["database", "storage", "sql", "nosql", "orm", "caching", "cache", "sqlite", "postgres", "redis", "offline"],
            "subquery": "database storage SQL NoSQL ORM caching persistence offline"
        },
        "Security / Auth": {
            "keywords": ["security", "auth", "authentication", "encryption", "cryptography", "jwt", "cipher", "secure"],
            "subquery": "security authentication authorization cryptography encryption token JWT cipher"
        },
        "Transport / Sync": {
            "keywords": ["sync", "syncing", "transport", "websocket", "network", "communication", "pubsub", "real-time"],
            "subquery": "real-time syncing network transport communication websocket pubsub socket"
        }
    }
    
    # Determine which layers are relevant based on query keywords
    # If query is very short or no keywords match, query all layers to compose a complete stack
    query_lower = query.lower()
    active_layers = {}
    
    for layer_name, config in layers.items():
        if any(kw in query_lower for kw in config["keywords"]) or len(query_lower.split()) < 4:
            active_layers[layer_name] = config
            
    # If no active layers matched, fall back to all layers
    if not active_layers:
        active_layers = layers
        
    output = []
    output.append(f"# 🏗️ Architectural Solution Stack Blueprint for: '{query}'\n")
    output.append("This blueprint was generated by analyzing the sub-components of your idea and matching them against indexed frameworks in ChromaDB.\n")
    
    for layer_name, config in active_layers.items():
        # Combine user's query with the layer's subquery to get a highly relevant search
        layer_query = f"{query} {config['subquery']}"
        try:
            results = collection.query(
                query_texts=[layer_query],
                n_results=n_results
            )
        except Exception as e:
            output.append(f"### **Layer: {layer_name}**")
            output.append(f"Error querying layer: {str(e)}\n")
            continue
            
        output.append(f"### 📦 Layer: {layer_name}")
        
        if not results or not results['ids'] or len(results['ids'][0]) == 0:
            output.append("No matched components found in the local index for this layer.")
            output.append("")
            continue
            
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            repo_name = metadata.get('name', 'Unknown')
            repo_url = metadata.get('url', '#')
            repo_lang = metadata.get('language', 'Unknown')
            repo_stars = metadata.get('stars', 0)
            matched_text = results['documents'][0][i]
            
            # Star formatting
            if repo_stars >= 1000:
                stars_str = f"{repo_stars / 1000:.1f}k"
            else:
                stars_str = str(repo_stars)
                
            output.append(f"{i+1}. **[{repo_name}]({repo_url})**")
            output.append(f"   *Language:* `{repo_lang}` | *Stars:* ⭐ {stars_str}")
            # Snippet of match
            snippet = matched_text[:200] + "..." if len(matched_text) > 200 else matched_text
            output.append(f"   *Role:* {snippet}")
        output.append("")
        
    output.append("---")
    output.append("### 🔗 Integration & Compatibility Guide")
    output.append("Ensure the components you select share a common language ecosystem or communicate via standardized network protocols (REST, WebSockets, or gRPC). For instance, a TypeScript-based offline storage engine pairs perfectly with a React Native or Node.js runtime.")
    
    return "\n".join(output)

@mcp.tool()
def get_repo_health(repo_name: str) -> str:
    """
    Fetch real-time health, activity telemetry, and security vulnerabilities for a target GitHub repository.
    Queries the GitHub API and the OSV.dev vulnerability database.
    
    Parameters:
    - repo_name (str): The full GitHub repository name (e.g. 'encode/django-rest-framework').
    """
    import os
    import requests
    from datetime import datetime, timedelta, timezone
    from github import Github, Auth
    
    # 1. Fetch GitHub data
    token = os.getenv("GITHUB_TOKEN")
    g_client = Github(auth=Auth.Token(token)) if token else Github()
    
    try:
        repo = g_client.get_repo(repo_name)
        stars = repo.stargazers_count
        forks = repo.forks_count
        open_issues = repo.open_issues_count
        created_at = repo.created_at
        pushed_at = repo.pushed_at
        size = repo.size
        language = repo.language or "Unknown"
        description = repo.description or ""
    except Exception as e:
        return f"Error fetching GitHub repository data for '{repo_name}': {str(e)}"
        
    # Calculate commit activity in last 30 days
    since_date = datetime.now(timezone.utc) - timedelta(days=30)
    commits_count = 0
    recent_commits_failed = False
    try:
        commits = repo.get_commits(since=since_date)
        for _ in commits:
            commits_count += 1
            if commits_count >= 100:
                break
    except Exception:
        recent_commits_failed = True
        commits_count = -1
        
    # Calculate recent PR activity
    open_prs = 0
    closed_prs = 0
    try:
        pulls = repo.get_pulls(state='all', sort='updated')
        count_checked = 0
        for pr in pulls:
            if count_checked >= 30:
                break
            count_checked += 1
            if pr.updated_at >= since_date:
                if pr.state == 'closed':
                    closed_prs += 1
                else:
                    open_prs += 1
    except Exception:
        pass
        
    # 2. OSV.dev Vulnerability Query using latest commit SHA
    latest_sha = None
    vulnerabilities = []
    try:
        latest_sha = repo.get_commits()[0].sha
    except Exception:
        pass
        
    if latest_sha:
        try:
            osv_url = "https://api.osv.dev/v1/query"
            response = requests.post(osv_url, json={"commit": latest_sha}, timeout=5)
            if response.status_code == 200:
                res_data = response.json()
                if "vulns" in res_data:
                    for vuln in res_data["vulns"]:
                        vuln_id = vuln.get("id", "Unknown ID")
                        summary = vuln.get("summary", "No summary provided")
                        details = vuln.get("details", "")
                        short_details = details[:120] + "..." if len(details) > 120 else details
                        vulnerabilities.append(f"- **{vuln_id}**: {summary} ({short_details})")
        except Exception as e:
            vulnerabilities.append(f"*(Could not query OSV database: {str(e)})*")
            
    # 3. Calculate Vitality Score (0-100)
    last_push_days = (datetime.now(timezone.utc) - pushed_at).days
    
    # Recency score (max 40)
    if last_push_days <= 7:
        recency_score = 40
    elif last_push_days <= 30:
        recency_score = 30
    elif last_push_days <= 90:
        recency_score = 20
    elif last_push_days <= 180:
        recency_score = 10
    else:
        recency_score = 0
        
    # Commit frequency score (max 30)
    if commits_count >= 20:
        freq_score = 30
    elif commits_count >= 10:
        freq_score = 25
    elif commits_count >= 5:
        freq_score = 20
    elif commits_count >= 1:
        freq_score = 10
    else:
        freq_score = 0
        
    # Issue/Community health score (max 30)
    issue_ratio = open_issues / (stars + 1)
    if issue_ratio < 0.02:
        ratio_score = 15
    elif issue_ratio < 0.05:
        ratio_score = 10
    else:
        ratio_score = 5
        
    if closed_prs >= 5:
        pr_score = 15
    elif closed_prs >= 1:
        pr_score = 10
    else:
        pr_score = 5
        
    community_score = ratio_score + pr_score
    vitality_score = recency_score + freq_score + community_score
    
    # 4. Generate report
    output = []
    output.append(f"## 🩺 Pulse & Health Telemetry for `{repo_name}`")
    output.append(f"*{description}*")
    output.append("")
    output.append(f"### **Vitality Score**: `{vitality_score}/100`")
    
    filled_bars = int(vitality_score / 10)
    bar_str = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
    output.append(f"{bar_str}")
    output.append("")
    
    output.append("### 📊 Metrics")
    output.append(f"- ⭐ **Stars:** {stars:,}")
    output.append(f"- 🍴 **Forks:** {forks:,}")
    output.append(f"- 🐛 **Open Issues:** {open_issues:,}")
    output.append(f"- 📅 **Created At:** {created_at.strftime('%Y-%m-%d')}")
    output.append(f"- 🚀 **Last Pushed:** {pushed_at.strftime('%Y-%m-%d')} ({last_push_days} days ago)")
    if commits_count >= 0:
        output.append(f"- 📈 **Commits (last 30 days):** {commits_count}")
    else:
        output.append("- 📈 **Commits (last 30 days):** *Failed to fetch*")
    output.append(f"- 🤝 **PR Activity (last 30 days):** {open_prs} Open, {closed_prs} Closed")
    output.append(f"- 💾 **Codebase Size:** {size / 1024:.2f} MB")
    
    output.append("")
    output.append("### 🛡️ Security Vulnerabilities (OSV.dev)")
    if vulnerabilities:
        real_vulns = [v for v in vulnerabilities if not v.startswith("*")]
        if real_vulns:
            output.append(f"⚠️ **Vulnerabilities Found:** The latest commit `{latest_sha[:8] if latest_sha else ''}` matches known vulnerabilities in the OSV database:")
            for v in vulnerabilities:
                output.append(v)
        else:
            output.append("⚠️ **Network / Details:**")
            for v in vulnerabilities:
                output.append(v)
    else:
        output.append("✅ No known vulnerabilities found for the latest commit SHA in the OSV database.")
        
    output.append("")
    output.append("### 💡 Verdict")
    if vitality_score >= 80 and not vulnerabilities:
        output.append("🌟 **Excellent:** This repository is highly active, well-maintained, and has no critical vulnerabilities. It is safe for production use.")
    elif vitality_score >= 50:
        output.append("⚠️ **Healthy with Caution:** The repository is moderately active. Ensure the maintenance rate aligns with your project lifecycle.")
    else:
        output.append("❌ **High Risk:** The repository is either abandoned or has extremely low maintenance activity. Consider finding alternatives to avoid technical debt.")
        
    return "\n".join(output)

@mcp.tool()
def profile_repo_hardware_footprint(
    repo_name: str, 
    target_hardware: str, 
    sram_limit_kb: float = 256.0, 
    flash_limit_kb: float = 1024.0
) -> str:
    """
    Profile the structural and resource footprint of a target repository against edge hardware limits.
    Analyzes project layout, file extensions, and dependency weight.
    
    Parameters:
    - repo_name (str): The full GitHub repository name (e.g. 'lvgl/lvgl').
    - target_hardware (str): The name of your microcontroller/hardware board (e.g. 'ESP32', 'STM32', 'Arduino').
    - sram_limit_kb (float): SRAM memory limit of your board in KB (default: 256.0).
    - flash_limit_kb (float): Flash storage limit of your board in KB (default: 1024.0).
    """
    import os
    from github import Github, Auth
    
    token = os.getenv("GITHUB_TOKEN")
    g_client = Github(auth=Auth.Token(token)) if token else Github()
    
    try:
        repo = g_client.get_repo(repo_name)
        root_contents = repo.get_contents("")
        file_names = [f.name.lower() for f in root_contents]
    except Exception as e:
        return f"Error connecting to GitHub repository '{repo_name}': {str(e)}"
        
    mcu_lang = "C/C++"
    has_cargo = "cargo.toml" in file_names
    has_package = "package.json" in file_names
    has_requirements = "requirements.txt" in file_names
    has_cmakelists = "cmakelists.txt" in file_names or "makefile" in file_names
    
    est_sram = 0.0
    est_flash = 0.0
    warnings = []
    
    if has_cargo:
        mcu_lang = "Rust"
        try:
            cargo_file = repo.get_contents("Cargo.toml")
            cargo_content = cargo_file.decoded_content.decode("utf-8").lower()
            if "no_std" in cargo_content or "alloc" in cargo_content:
                est_sram = 15.0
                est_flash = 45.0
                warnings.append("✅ Rust crate appears to support `no_std`. Suitable for bare-metal.")
            else:
                est_sram = 512.0
                est_flash = 1024.0
                warnings.append("⚠️ Rust crate does not explicitly declare `no_std`. Standard library `std` may exceed SRAM limits on thin microcontrollers.")
        except Exception:
            est_sram = 128.0
            est_flash = 256.0
            warnings.append("⚠️ Failed to parse Cargo.toml. Assuming standard Rust std footprint.")
            
    elif has_requirements:
        mcu_lang = "MicroPython / Python"
        est_sram = 120.0
        est_flash = 512.0
        warnings.append("⚠️ Python code detected. Will require MicroPython/CircuitPython interpreter on the microcontroller.")
        warnings.append("⚠️ Python code is dynamically allocated and could cause high heap/SRAM consumption and fragmentation.")
        
    elif has_package:
        mcu_lang = "JavaScript / JerryScript"
        est_sram = 180.0
        est_flash = 600.0
        warnings.append("⚠️ JavaScript code detected. Requires QuickJS or JerryScript engine, which have high overhead on Cortex-M boards.")
        
    elif has_cmakelists or any(f.endswith('.h') or f.endswith('.c') or f.endswith('.cpp') for f in file_names):
        mcu_lang = "C/C++"
        uses_stl = False
        try:
            h_files = [f for f in root_contents if f.name.endswith('.h') or f.name.endswith('.hpp')]
            if h_files:
                sample_file = repo.get_contents(h_files[0].path)
                sample_content = sample_file.decoded_content.decode("utf-8")
                if "std::" in sample_content or "vector" in sample_content or "string" in sample_content:
                    uses_stl = True
        except Exception:
            pass
            
        if uses_stl:
            est_sram = 64.0
            est_flash = 200.0
            warnings.append("⚠️ C++ library uses standard template library (STL) headers (vector/string), which cause heap usage and binary bloat.")
        else:
            est_sram = 20.0
            est_flash = 80.0
            warnings.append("✅ Bare-metal C/C++ codebase with low overhead. Highly compatible with small microcontrollers.")
            
    else:
        mcu_lang = repo.language or "C/C++"
        est_sram = 50.0
        est_flash = 150.0
        warnings.append("⚠️ Unknown framework structure. Footprint estimated based on language.")
        
    if repo.size > 10000:
        est_flash += 300.0
        est_sram += 50.0
        warnings.append(f"⚠️ Large repository size ({repo.size / 1024:.1f}MB). Binary footprint may expand depending on compiled features.")
        
    sram_ok = est_sram <= sram_limit_kb
    flash_ok = est_flash <= flash_limit_kb
    
    score = 100
    if not sram_ok:
        score -= 50
    if not flash_ok:
        score -= 30
        
    output = []
    output.append(f"## 🎛️ Edge-Deploy Footprint Profile for `{repo_name}`")
    output.append(f"**Target Microcontroller/Hardware:** `{target_hardware}`")
    output.append(f"**Core Language Ecosystem:** `{mcu_lang}`")
    output.append("")
    output.append("| Resource Metric | Estimated Footprint | Specified Hardware Limit | Match Status |")
    output.append("| --- | --- | --- | --- |")
    output.append(f"| **SRAM / RAM** | {est_sram:.1f} KB | {sram_limit_kb:.1f} KB | {'✅ Fits' if sram_ok else '❌ Exceeded'} |")
    output.append(f"| **Flash Storage** | {est_flash:.1f} KB | {flash_limit_kb:.1f} KB | {'✅ Fits' if flash_ok else '❌ Exceeded'} |")
    output.append("")
    output.append(f"### **Hardware Fit Score**: `{score}/100`")
    output.append("")
    output.append("### 🔍 Static Analysis Findings:")
    for w in warnings:
        output.append(w)
        
    output.append("")
    output.append("### 💡 Deployment Recommendation:")
    if score == 100:
        output.append(f"🟢 **Deployable:** `{repo_name}` is extremely lightweight and will easily fit on the `{target_hardware}`. Go ahead with integration.")
    elif score >= 50:
        output.append(f"🟡 **Optimizations Required:** You can run this codebase on `{target_hardware}`, but you must optimize memory layouts, compile with optimization flags (e.g. `-Os`), and disable unnecessary library modules.")
    else:
        output.append(f"🔴 **Incompatible / High Risk:** This library is too heavy for the `{target_hardware}` spec. SRAM or Flash requirements will lead to build errors or runtime out-of-memory crashes. Consider a C/Rust bare-metal alternative.")
        
    return "\n".join(output)

@mcp.tool()
def align_system_architecture(repo_name: str, workspace_path: str = ".") -> str:
    """
    Analyze the local workspace directory structure to detect its design pattern,
    and output a detailed architectural alignment/integration report for the target repository.
    
    Parameters:
    - repo_name (str): Proposed repository.
    - workspace_path (str): Path to workspace (defaults to '.').
    """
    import os
    
    dirs_found = set()
    try:
        for root, dirs, files in os.walk(workspace_path):
            if '.git' in dirs:
                dirs.remove('.git')
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
            if '.venv' in dirs:
                dirs.remove('.venv')
                
            depth = root[len(workspace_path):].count(os.sep)
            if depth > 1:
                continue
                
            for d in dirs:
                dirs_found.add(d.lower())
    except Exception as e:
        return f"Error scanning workspace directories: {str(e)}"
        
    clean_folders = {'domain', 'ports', 'adapters', 'infrastructure', 'application', 'usecases', 'entities'}
    mvc_folders = {'models', 'views', 'controllers', 'templates'}
    layered_folders = {'services', 'repositories', 'api', 'controllers', 'dao', 'db'}
    
    pattern = "Ad-hoc / Scripting Monolith"
    description = "No specific architecture folders detected. Code is organized in ad-hoc modules or scripts."
    
    if len(clean_folders.intersection(dirs_found)) >= 2:
        pattern = "Clean / Hexagonal Architecture (Ports & Adapters)"
        description = "Workspace enforces separation of domain business logic from infrastructure/external libraries using boundaries."
    elif len(mvc_folders.intersection(dirs_found)) >= 2:
        pattern = "Model-View-Controller (MVC)"
        description = "Workspace is organized into database models, UI views, and routing/controller components."
    elif len(layered_folders.intersection(dirs_found)) >= 2:
        pattern = "Layered Architecture (N-Tier)"
        description = "Workspace isolates presentation, business services, and database repository layers."
        
    repo_lower = repo_name.lower()
    role = "Utility Library"
    
    db_keywords = ['db', 'sql', 'redis', 'mongo', 'orm', 'prisma', 'alchemy', 'store', 'postgres']
    web_keywords = ['http', 'api', 'flask', 'django', 'express', 'fastapi', 'grpc', 'web', 'route', 'server']
    ui_keywords = ['ui', 'component', 'tailwind', 'css', 'react', 'button', 'theme', 'color', 'view']
    
    if any(kw in repo_lower for kw in db_keywords):
        role = "Database / Storage Layer"
    elif any(kw in repo_lower for kw in web_keywords):
        role = "Web API / External Client"
    elif any(kw in repo_lower for kw in ui_keywords):
        role = "UI Component / Presentation"
        
    advice = []
    diagram = ""
    
    if "Clean" in pattern:
        if role in ["Database / Storage Layer", "Web API / External Client"]:
            advice.append(f"⚠️ **Domain Boundary Alert**: Since the workspace uses Hexagonal/Clean Architecture, do NOT import `{repo_name}` directly in your core domain/usecase layers.")
            advice.append(f"👉 **Integration Pathway**: Define a Port interface (e.g. `UserRepository` or `APIClient`) inside your `domain/ports` folder. Implement the adapter wrapping `{repo_name}` in the `infrastructure/adapters` directory. Inject it at runtime.")
            
            diagram = (
                "```mermaid\n"
                "graph TD\n"
                "  subgraph Domain Layer\n"
                "    Usecase[Business Logic/Usecase]\n"
                "    Port[Port Interface: e.g. IStorage] -->|Defines| Usecase\n"
                "  end\n"
                "  subgraph Infrastructure Layer\n"
                "    Adapter[Adapter Implementation] -->|Implements| Port\n"
                "    Adapter -->|Calls| Lib[\"Target Library: " + repo_name + "\"]\n"
                "  end\n"
                "```"
            )
        else:
            advice.append(f"✅ Core Utility: `{repo_name}` can be consumed as a standard utility, but keep it isolated if it communicates with outside resources.")
    elif "MVC" in pattern:
        if role == "Database / Storage Layer":
            advice.append(f"👉 **Integration Pathway**: Place your database models under the `models` folder, and initialize `{repo_name}` inside a central database configuration file. Ensure controllers do not make raw SQL queries directly.")
            diagram = (
                "```mermaid\n"
                "graph TD\n"
                "  Controller[Controller / Router] --> Models[Models Layer]\n"
                "  Models --> DB[\"Target Library: " + repo_name + "\"]\n"
                "  Controller --> View[View / Templates]\n"
                "```"
            )
        elif role == "Web API / External Client":
            advice.append(f"👉 **Integration Pathway**: Wrap your API requests in a dedicated controller helper or services folder to keep the core routers thin and testable.")
        else:
            advice.append(f"✅ Standard MVC integration. Import `{repo_name}` directly inside the layer that requires it (Controller or View).")
    elif "Layered" in pattern:
        if role == "Database / Storage Layer":
            advice.append(f"👉 **Integration Pathway**: Integrate `{repo_name}` strictly in the `Repository` or `DAO` layer. The `Service` and `API` layers should only interact with repositories, never with the raw database library.")
            diagram = (
                "```mermaid\n"
                "graph TD\n"
                "  API[API Controller Layer] --> Service[Service / Business Layer]\n"
                "  Service --> Repo[Repository Layer]\n"
                "  Repo --> Lib[\"Target Library: " + repo_name + "\"]\n"
                "```"
            )
        else:
            advice.append(f"👉 **Integration Pathway**: Keep `{repo_name}` usages bounded inside its corresponding layer.")
    else:
        advice.append("💡 **Architectural Suggestion**: The workspace doesn't have a strict pattern. As the project grows, consider separating business logic from framework-specific code.")
        advice.append(f"👉 **Integration Pathway**: Create a helper module or utility folder, and wrap `{repo_name}` calls inside helper functions rather than distributing them throughout your scripts.")
        diagram = (
            "```mermaid\n"
            "graph TD\n"
            "  Main[app.py / main.py] --> Helper[Helper Wrapper Module]\n"
            "  Helper --> Lib[\"Target Library: " + repo_name + "\"]\n"
            "```"
        )
        
    output = []
    output.append(f"## 🏛️ Architectural Vector Alignment Report for `{repo_name}`")
    output.append(f"**Workspace Pattern Detected:** `{pattern}`")
    output.append(f"*{description}*")
    output.append("")
    output.append(f"**Target Library Architectural Role:** `{role}`")
    output.append("")
    output.append("### 📌 Integration Recommendations:")
    for a in advice:
        output.append(a)
    output.append("")
    if diagram:
        output.append("### 🗺️ Integration Dependency Graph:")
        output.append(diagram)
        output.append("")
        
    return "\n".join(output)

if __name__ == "__main__":
    mcp.run(transport="stdio")
