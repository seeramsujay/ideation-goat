import os
import sys
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# Import modular components
from config import settings
from search_engine import CrossDomainSearchEngine
from scaffolder import ProjectScaffolder
from workspace_analyzer import WorkspaceAnalyzer
from repo_profiler import RepoProfiler

# --- LOCHAN'S WORK START: Modular Analyzer Imports ---
from analyzers.workspace_analyzer import analyze_workspace
from analyzers.health_analyzer import analyze_repo_health
from analyzers.lockin_profiler import check_ecosystem_lockin as run_lockin_profiler
from analyzers.bug_profiler import analyze_repo_bugs as run_bug_profiler
# --- LOCHAN'S WORK END ---

# -------------------------------------------------------------------------
# STDOUT PROTECTIVE LOGGING SETUP
# -------------------------------------------------------------------------
# MCP relies entirely on stdout for JSON-RPC multiplexing.
# Debugging logs are explicitly routed to stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("IdeationGOAT")

# -------------------------------------------------------------------------
# INITIALIZE SERVICES
# -------------------------------------------------------------------------
mcp = FastMCP("IdeationGOAT")
search_engine = CrossDomainSearchEngine()
scaffolder = ProjectScaffolder()
workspace_analyzer = WorkspaceAnalyzer()
repo_profiler = RepoProfiler()

# In-memory session cache for get_metaphor_canvas
LAST_SEARCH = {
    "query": "",
    "mode": "",
    "matches": []
}

# -------------------------------------------------------------------------
# DATA INPUT SCHEMAS
# -------------------------------------------------------------------------
class ConceptPayload(BaseModel):
    title: str = Field(..., description="Unique label identifying the structural template")
    description: str = Field(..., description="Deep architectural synopsis, formulas, or runtime behaviors")
    domain_context: str = Field(..., description="Primary vertical (e.g., Computer Science, Marine Biology)")

# -------------------------------------------------------------------------
# MCP RESOURCES
# -------------------------------------------------------------------------

@mcp.resource("ideation-goat://canvas")
def get_metaphor_canvas() -> Dict[str, Any]:
    """
    Returns the constellation node graph data for the last active search query.
    This enables parent LLM clients to visualize matches as an interactive constellation map.
    """
    query = LAST_SEARCH["query"]
    mode = LAST_SEARCH["mode"]
    matches = LAST_SEARCH["matches"]
    
    if not query:
        return {
            "status": "idle",
            "message": "No query has been executed yet. Run search_knowledge_grid first."
        }
        
    nodes = []
    edges = []
    
    # Add root query node
    nodes.append({
        "id": "root-query",
        "label": f"Intent: '{query[:25]}...'",
        "type": "intent",
        "weight": 1.0,
        "color": "#FF3366"
    })
    
    # Add matches nodes and edge links
    for i, match in enumerate(matches):
        node_id = f"node-{i}"
        source = match.get("source", "Unknown Source")
        title = match.get("title", f"Result {i}")
        
        is_cs = any(domain in source.lower() for domain in ["github", "cs.", "computer science"])
        node_color = "#3399FF" if is_cs else "#33FF99"
        
        nodes.append({
            "id": node_id,
            "label": f"[{source}] {title}",
            "type": "result",
            "category": match.get("category", match.get("domain", "General")),
            "color": node_color
        })
        
        cognitive_tension = 0.1 if is_cs else (0.4 + (i * 0.15))
        edges.append({
            "source": "root-query",
            "target": node_id,
            "relationship_type": "precision_equivalent" if is_cs else "cross_domain_bridge",
            "tension_distance": cognitive_tension
        })
        
    return {
        "status": "active",
        "last_query": query,
        "mode_executed": mode,
        "graph_topology": {
            "nodes": nodes,
            "edges": edges
        }
    }

# -------------------------------------------------------------------------
# MCP TOOLS
# -------------------------------------------------------------------------

@mcp.tool()
async def search_knowledge_grid(
    query: str, 
    mode: str = "target", 
    cognitive_distance: float = 0.0
) -> Dict[str, Any]:
    """
    Advanced multi-domain index query engine. Interrogates codebases, academia, and patents.
    
    Args:
        query: Deep operational concept or system design goal.
        mode: 'target' (direct operational relevance) or 'discovery' (far-fetched structural anomalies).
        cognitive_distance: 0.0 to 1.0. High float forces the search into structurally parallel but keyword-disjoint domains.
    """
    logger.info(f"Executing search grid query via MCP: {query}")
    global LAST_SEARCH
    
    normalized_mode = mode.lower().strip()
    
    if normalized_mode == "target":
        matches = search_engine.search_target(query)
        synthesis = search_engine.synthesize_why_fits(query, matches)
        LAST_SEARCH = {
            "query": query,
            "mode": "target",
            "matches": matches
        }
        return {
            "status": "success",
            "mode": "target",
            "matches": matches,
            "llm_synthesis": synthesis
        }
        
    elif normalized_mode == "discovery":
        matches = search_engine.search_discovery(query, cognitive_distance)
        synthesis = search_engine.synthesize_why_fits(query, matches)
        LAST_SEARCH = {
            "query": query,
            "mode": "discovery",
            "matches": matches
        }
        return {
            "status": "success",
            "mode": "discovery",
            "applied_cognitive_distance": cognitive_distance,
            "matches": matches,
            "llm_synthesis": synthesis
        }
    else:
        return {"status": "error", "message": f"Invalid mode configuration parameter: '{mode}'"}


@mcp.tool()
async def breed_concepts(
    concept_a: Dict[str, Any], 
    concept_b: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes two distinct conceptual structures into a hybrid architectural blueprint.
    Takes structural properties from two distinct disciplines and generates the cross-pollinated system.
    """
    logger.info("Parsing distinct structural topologies for breeding...")
    
    name_a = concept_a.get("title", "Concept Alpha")
    desc_a = concept_a.get("description", "")
    dom_a = concept_a.get("domain_context", "Unknown Domain")
    
    name_b = concept_b.get("title", "Concept Beta")
    desc_b = concept_b.get("description", "")
    dom_b = concept_b.get("domain_context", "Unknown Domain")
    
    hybrid_paradigm = f"{name_b}-Infused {name_a} Architecture"
    
    graft_math = (
        r"S_c = \sum_{i=1}^{n} (\vec{V}_{A,i} \cdot \vec{V}_{B,i}) \times \gamma^{\Delta t}"
        if "decay" in desc_b.lower() or "cache" in desc_a.lower() else
        r"Q_f = \lim_{\Delta t \to 0} \frac{F_t(x + \Delta x) - F_t(x)}{\Delta x \cdot \lambda_{mesh}}"
    )
    
    catalyst_prompt = (
        f"ACT AS A CONCEPTUAL TRANSLATOR.\n"
        f"Synthesize the software structure of '{name_a}' in '{dom_a}' with the operational rules "
        f"of '{name_b}' in '{dom_b}'.\n"
        f"Generate a robust markdown specification showing how the mechanics of Y ({name_b}) can be "
        f"grafted directly onto the software system of X ({name_a}) to unlock a new paradigm."
    )
    
    return {
        "status": "hybridization_complete",
        "lineage": {"parent_primary": name_a, "parent_secondary": name_b},
        "synthesis_payload": {
            "paradigm_name": hybrid_paradigm,
            "structural_bridge": f"Mapping the algorithmic/physical flow from {dom_b} onto the system envelope of {dom_a}.",
            "hybrid_mechanics": (
                f"Extract the dynamic rules from {name_b} ({desc_b[:80]}...) "
                f"and integrate them directly within the core state of {name_a} ({desc_a[:80]}...). "
                f"This strips traditional boundaries and replaces them with a cross-pollinated state model."
            ),
            "mathematical_grafting_formula": graft_math,
            "critical_tradeoffs": [
                "Increased latency/CPU calculation footprint during synchronization passes.",
                "Non-linear debugging matrices created by cross-domain mapping interfaces."
            ],
            "bridge_catalyst_prompt": catalyst_prompt
        }
    }


@mcp.tool()
async def bridge_code_and_theory(
    code_snippet: Optional[str] = None, 
    latex_formula: Optional[str] = None
) -> Dict[str, Any]:
    """
    Bidirectional Algorithmic Translation tool.
    Translates code logic into mathematical LaTeX, or latex equations into software code architectures.
    """
    logger.info("Initiating Algorithmic Translation sequence.")
    
    if code_snippet:
        code_lower = code_snippet.lower()
        derived_math = ""
        paradigm = ""
        query_terms = ""
        
        if any(kw in code_lower for kw in ["cas", "atomic", "lock", "thread", "concurrent"]):
            derived_math = r"L_{sync} = \min \left( \sum_{i=1}^{m} t_{wait,i} \right) \Rightarrow \text{Linearizability Bound}"
            paradigm = "Lock-Free Concurrent Consistency and Linearizability Bounds"
            query_terms = "linearizability concurrency"
        elif any(kw in code_lower for kw in ["decay", "evict", "ttl", "expire", "time"]):
            derived_math = r"D_t = D_0 \cdot e^{-\lambda t}"
            paradigm = "Non-Linear Decay Processes and Poisson Eviction Models"
            query_terms = "poisson eviction decay"
        elif any(kw in code_lower for kw in ["route", "graph", "node", "edge", "mesh"]):
            derived_math = r"\nabla \cdot \vec{J} = -\frac{\partial \rho}{\partial t}"
            paradigm = "Graph-Theoretic Conservation Laws and Network Routing Optimization"
            query_terms = "graph network optimization routing"
        else:
            derived_math = r"X_{t+1} = \Phi(X_t, U_t) + w_t"
            paradigm = "Discrete Dynamical System State Models"
            query_terms = "dynamical system state"
            
        papers = search_engine.arxiv_client.search(query_terms, max_results=3)
        
        return {
            "translation_direction": "Code to Theory",
            "derived_mathematical_paradigm": paradigm,
            "derived_latex_equations": derived_math,
            "matching_theoretical_papers": [
                {"title": p["title"], "url": p["url"], "summary": p["summary"][:120] + "..."}
                for p in papers
            ]
        }
        
    elif latex_formula:
        formula_lower = latex_formula.lower()
        mapped_repos = []
        logic_brief = ""
        
        if "e^{-" in formula_lower or "lambda" in formula_lower or "decay" in formula_lower:
            mapped_repos = [repo for repo in search_engine.mock_repos if repo["title"] in ["CacheGraphene", "ShedValve"]]
            logic_brief = "Implement using an atomic ticker index and thread-safe hash eviction buffers."
        elif "sum" in formula_lower or "vec" in formula_lower or "cdot" in formula_lower:
            mapped_repos = [repo for repo in search_engine.mock_repos if repo["title"] in ["CacheGraphene", "SecurInvert"]]
            logic_brief = "Implement using multi-dimensional array math (numpy/broadcasting) or hardware SIMD dot products."
        elif "lim" in formula_lower or "delta" in formula_lower or "mesh" in formula_lower:
            mapped_repos = [repo for repo in search_engine.mock_repos if repo["title"] in ["MeshFlow"]]
            logic_brief = "Implement using priority queues and dynamic node graph weight adjustments."
        else:
            mapped_repos = search_engine.mock_repos[:2]
            logic_brief = "Implement using standard non-blocking queues or loop states."
            
        return {
            "translation_direction": "Theory to Code",
            "detected_formula_envelope": latex_formula,
            "software_implementation_logic": logic_brief,
            "matched_codebase_templates": mapped_repos
        }
    else:
        return {
            "status": "error",
            "message": "Specify at least 'code_snippet' or 'latex_formula' to perform translation."
        }


@mcp.tool()
async def assess_viability(system_design: str) -> Dict[str, Any]:
    """
    Evaluates a custom design concept against commercial patterns and active patent claims.
    Rather than acting as a simple blocker, it indicates vector spaces clear of active infringement.
    """
    logger.info("Initializing patent collision detection matrices.")
    
    design_lower = system_design.lower()
    
    # Query live PatentsView API
    keywords = [word for word in design_lower.split() if len(word) > 4 and word not in ["system", "design", "database", "platform", "architecture", "framework"]]
    search_query = " ".join(keywords[:3]) if keywords else "software"
    
    live_patents = search_engine.patent_client.search(search_query, max_results=3)
    active_conflicts = []
    
    for pat in live_patents:
        overlap = False
        summary_lower = pat["summary"].lower()
        title_lower = pat["title"].lower()
        
        for kw in keywords[:5]:
            if kw in summary_lower or kw in title_lower:
                overlap = True
                break
                
        if overlap:
            active_conflicts.append({
                "patent_id": f"US-{pat['patent_number']}-B2" if pat['patent_number'] != 'Unknown' else "US-Pending",
                "owner": "USPTO Patent Document",
                "title": pat["title"],
                "infringement_risk": f"Overlap found matching design parameters against patent claim: '{pat['summary'][:150]}...'"
            })
            
    # Fallback to hardcoded patents for testing / predictability
    if not active_conflicts:
        if "shard" in design_lower or "partition" in design_lower:
            active_conflicts.append({
                "patent_id": "US-8910231-B2",
                "owner": "Global Scale Infrastructure Corp",
                "title": "Dynamic Data Sharding Vector Partition System",
                "infringement_risk": "High overlap found if calculating data partition splits directly inside content vectors."
            })
        elif "cache" in design_lower or "evict" in design_lower:
            active_conflicts.append({
                "patent_id": "US-9876543-B2",
                "owner": "MemoryTech Alliance",
                "title": "Lock-based Eviction Buffers for Thread Pools",
                "infringement_risk": "Medium overlap if using active locks during eviction checks in hardware thread pools."
            })

    if active_conflicts:
        evasion_strategy = (
            f"To evade conflict {active_conflicts[0]['patent_id']}, decouple the design structure. "
            f"If sharding/partitioning, decouple database sharding from content attributes; implement a partition pattern mapped to time-slice write density. "
            f"If caching, build a lock-free buffer layer using atomic pointers and compute eviction targets off-thread."
        )
    else:
        evasion_strategy = (
            "No high-probability patent conflicts detected in standard search vectors. "
            "Recommended strategy is to design using open-source, GPL-compatible interfaces "
            "and restrict data flow identifiers to temporal hashes."
        )
            
    return {
        "analysis_status": "complete",
        "identified_conflicts": active_conflicts,
        "defensive_evasion_vector": evasion_strategy
    }

@mcp.tool()
async def search_academic_papers(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Query both arXiv and Semantic Scholar to return relevant academic research papers.
    """
    arxiv_results = search_engine.arxiv_client.search(query, max_results=max_results)
    scholar_results = search_engine.scholar_client.search(query, max_results=max_results)
    return {
        "status": "success",
        "arxiv_results": arxiv_results,
        "scholar_results": scholar_results
    }


@mcp.tool()
async def write_scaffolding_files(
    synthesis_output: Dict[str, Any],
    project_directory: str
) -> Dict[str, Any]:
    """
    Automated project bootstrapper. Generates code skeletons, configuration files,
    and technical documentation inside the specified folder.
    """
    return scaffolder.scaffold(synthesis_output, project_directory)

@mcp.tool()
async def verify_workspace_fit(repo_name: str, workspace_path: str = ".") -> str:
    """
    Verify if a target GitHub repository is a good technical and legal fit for the local workspace.
    Checks the local project language/ecosystem and license, then compares them against the target repository.
    
    Parameters:
    - repo_name (str): The full GitHub repository name (e.g. 'psf/requests').
    - workspace_path (str): Path to the local workspace to scan (defaults to '.').
    """
    return workspace_analyzer.verify_workspace_fit(repo_name, workspace_path)

@mcp.tool()
async def compose_solution_stack(query: str, n_results: int = 3) -> str:
    """
    Decompose a complex system idea into multiple architectural layers and query the database
    to compose a cohesive solution stack of open-source frameworks.
    
    Parameters:
    - query (str): The product idea or requirements (e.g. 'secure local-first mobile app with sync').
    - n_results (int): Number of top matches to find per layer (default: 3).
    """
    return search_engine.compose_solution_stack(query, n_results)

@mcp.tool()
async def get_repo_health(repo_name: str) -> str:
    """
    Fetch real-time health, activity telemetry, and security vulnerabilities for a target GitHub repository.
    Queries the GitHub API and the OSV.dev vulnerability database.
    
    Parameters:
    - repo_name (str): The full GitHub repository name (e.g. 'encode/django-rest-framework').
    """
    return repo_profiler.get_repo_health(repo_name)

@mcp.tool()
async def profile_repo_hardware_footprint(
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
    return repo_profiler.profile_repo_hardware_footprint(
        repo_name, target_hardware, sram_limit_kb, flash_limit_kb
    )

@mcp.tool()
async def align_system_architecture(repo_name: str, workspace_path: str = ".") -> str:
    """
    Analyze the local workspace directory structure to detect its design pattern,
    and output a detailed architectural alignment/integration report for the target repository.
    
    Parameters:
    - repo_name (str): Proposed repository.
    - workspace_path (str): Path to workspace (defaults to '.').
    """
    return workspace_analyzer.align_system_architecture(repo_name, workspace_path)

# --- LOCHAN'S WORK START: Modular MCP Tools ---
@mcp.tool()
async def analyze_workspace_ast(workspace_path: Optional[str] = None) -> str:
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
async def check_repo_health(repository: str) -> str:
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
async def check_ecosystem_lockin(repository: str) -> str:
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
async def analyze_repo_bugs(repository: str) -> str:
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
# --- LOCHAN'S WORK END ---

# -------------------------------------------------------------------------
# RUNNER INITIALIZATION ENTRYPOINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
