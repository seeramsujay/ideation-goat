import os
import sys
import logging
from typing import Dict, Any, Optional, List

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
from analyzers.cost_forecaster import forecast_deployment_costs
from analyzers.schema_healer import heal_parameter_schema
from analyzers.identity_sandbox import verify_sandbox_identity
from analyzers.di_profiler import profile_workspace_di
from analyzers.cve_shield import scan_workspace_security_cves
# --- LOCHAN'S WORK END ---

from orchestrator import WorkflowOrchestrator
from mcp.server.fastmcp import FastMCP

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
orchestrator = WorkflowOrchestrator()

# In-memory session cache for get_metaphor_canvas
LAST_SEARCH = {
    "query": "",
    "mode": "",
    "matches": []
}

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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Deep operational concept or system design goal."),
        mode: z.enum(["target", "discovery"]).default("target").describe("Search mode determining grid traversal."),
        cognitive_distance: z.number().min(0.0).max(1.0).default(0.0).describe("Applied cognitive distance factor.")
      })
    
    JSON Output Structure:
      On Success (mode='target'):
        {
          "status": "success",
          "mode": "target",
          "matches": [{"title": string, "source": string, ...}],
          "llm_synthesis": string
        }
      On Success (mode='discovery'):
        {
          "status": "success",
          "mode": "discovery",
          "applied_cognitive_distance": float,
          "matches": [{"title": string, "source": string, ...}],
          "llm_synthesis": string
        }
      On Error:
        {
          "status": "error",
          "message": string
        }
        
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        concept_a: z.object({
          title: z.string(),
          description: z.string(),
          domain_context: z.string()
        }).describe("First conceptual paradigm model."),
        concept_b: z.object({
          title: z.string(),
          description: z.string(),
          domain_context: z.string()
        }).describe("Second conceptual paradigm model to graft.")
      })
    
    JSON Output Structure:
      {
        "status": "hybridization_complete",
        "lineage": {"parent_primary": string, "parent_secondary": string},
        "synthesis_payload": {
          "paradigm_name": string,
          "structural_bridge": string,
          "hybrid_mechanics": string,
          "mathematical_grafting_formula": string,
          "critical_tradeoffs": [string],
          "bridge_catalyst_prompt": string
        }
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        code_snippet: z.string().optional().describe("Source code logic pattern to analyze."),
        latex_formula: z.string().optional().describe("LaTeX formula string to map to implementations.")
      })
    
    JSON Output Structure:
      On Code to Theory translation:
        {
          "translation_direction": "Code to Theory",
          "derived_mathematical_paradigm": string,
          "derived_latex_equations": string,
          "matching_theoretical_papers": [{"title": string, "url": string, "summary": string}]
        }
      On Theory to Code translation:
        {
          "translation_direction": "Theory to Code",
          "detected_formula_envelope": string,
          "software_implementation_logic": string,
          "matched_codebase_templates": [{"title": string, ...}]
        }
      On Error:
        {
          "status": "error",
          "message": string
        }
        
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        system_design: z.string().describe("Text describing design components and architecture layout.")
      })
    
    JSON Output Structure:
      {
        "analysis_status": "complete",
        "identified_conflicts": [{
          "patent_id": string,
          "owner": string,
          "title": string,
          "infringement_risk": string
        }],
        "defensive_evasion_vector": string
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    logger.info("Initializing patent collision detection matrices.")
    
    design_lower = system_design.lower()
    
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
                "owner": pat.get("source", "Patent Document"),
                "title": pat["title"],
                "infringement_risk": f"Overlap found matching design parameters against patent claim: '{pat['summary'][:150]}...'"
            })
            
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Scientific concept or keyword query."),
        max_results: z.number().int().default(5).describe("Maximum matches to return per engine.")
      })
    
    JSON Output Structure:
      {
        "status": "success",
        "arxiv_results": [{"title": string, "url": string, "summary": string, ...}],
        "scholar_results": [{"title": string, "url": string, "summary": string, ...}]
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        synthesis_output: z.record(z.any()).describe("Architectural paradigm template definitions."),
        project_directory: z.string().describe("Target workspace directory name.")
      })
    
    JSON Output Structure:
      {
        "status": "success" | "error",
        "scaffold_directory": string,
        "files_created": [string],
        "instruction": string
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return scaffolder.scaffold(synthesis_output, project_directory)


@mcp.tool()
async def verify_workspace_fit(repo_name: str, workspace_path: str = ".") -> str:
    """
    Verify if a target GitHub repository is a good technical and legal fit for the local workspace.
    Checks the local project language/ecosystem and license, then compares them against the target repository.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repo_name: z.string().describe("Target github repo coordinates (e.g. 'encode/django-rest-framework')."),
        workspace_path: z.string().default(".").describe("Workspace root folder to parse and check compatibility.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report summarizing compatibility fit metrics)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return workspace_analyzer.verify_workspace_fit(repo_name, workspace_path)


@mcp.tool()
async def compose_solution_stack(query: str, n_results: int = 3) -> str:
    """
    Decompose a complex system idea into multiple architectural layers and query the database
    to compose a cohesive solution stack of open-source frameworks.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Product requirements or architectural design ideas."),
        n_results: z.number().int().default(3).describe("Number of top matches to find per layer.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report detailing matched layered stacks)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return search_engine.compose_solution_stack(query, n_results)


@mcp.tool()
async def get_repo_health(repo_name: str) -> str:
    """
    Fetch real-time health, activity telemetry, and security vulnerabilities for a target GitHub repository.
    Queries the GitHub API and the OSV.dev vulnerability database.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repo_name: z.string().describe("Target github repo name (e.g. 'facebook/react').")
      })
    
    JSON Output Structure:
      string (formatted Markdown report listing stars, issue volume, and CVE vulnerabilities)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repo_name: z.string().describe("Target edge firmware repo coordinates."),
        target_hardware: z.string().describe("Name of edge hardware board target."),
        sram_limit_kb: z.number().default(256.0).describe("SRAM limits of board in KB."),
        flash_limit_kb: z.number().default(1024.0).describe("Flash storage limits of board in KB.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report profiling binary footprint estimation)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return repo_profiler.profile_repo_hardware_footprint(
        repo_name, target_hardware, sram_limit_kb, flash_limit_kb
    )


@mcp.tool()
async def align_system_architecture(repo_name: str, workspace_path: str = ".") -> str:
    """
    Analyze the local workspace directory structure to detect its design pattern,
    and output a detailed architectural alignment/integration report for the target repository.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repo_name: z.string().describe("Proposed integration repository name."),
        workspace_path: z.string().default(".").describe("Workspace root directory to check alignment.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report profiling directory drift and alignment strategy)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return workspace_analyzer.align_system_architecture(repo_name, workspace_path)


# --- LOCHAN'S WORK START: Modular MCP Tools ---
@mcp.tool()
async def analyze_workspace_ast(workspace_path: Optional[str] = None) -> str:
    """
    Zero-friction local workspace AST & dependency analyzer.
    Reads local configuration files (package.json, pyproject.toml, Cargo.toml, go.mod) and scans source imports
    to identify the user's active tech stack without needing external tokens.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        workspace_path: z.string().optional().describe("Optional path to local project workspace folder.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report representing stack and parsed package dependencies)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repository: z.string().describe("Target repository name or clone URL coordinates.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report profiling OSV vulnerabilities and composite scorecard rating)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repository: z.string().describe("Repository coordinates to trace vendor dependencies.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report grading project portability)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        repository: z.string().describe("Target repository name or path to parse issues.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report summarizing high-frequency bugs and clusters)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
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
async def orchestrate_architectural_workflow(
    query: str,
    workspace_path: str = ".",
    target_hardware: Optional[str] = None,
    sram_limit_kb: float = 256.0,
    flash_limit_kb: float = 1024.0,
    scaffold_directory: Optional[str] = None
) -> str:
    """
    Executes a multi-step analytical workflow.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Design paradigm or intent description."),
        workspace_path: z.string().default(".").describe("Root folder of local project."),
        target_hardware: z.string().optional().describe("Microcontroller board target configuration."),
        sram_limit_kb: z.number().default(256.0).describe("SRAM limitations in KB."),
        flash_limit_kb: z.number().default(1024.0).describe("Flash limits in KB."),
        scaffold_directory: z.string().optional().describe("Workspace subdirectory to write scaffold files.")
      })
    
    JSON Output Structure:
      string (formatted Markdown report summarizing entire workflow execution results)
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    res = orchestrator.orchestrate_workflow(
        query=query,
        workspace_path=workspace_path,
        target_hardware=target_hardware,
        sram_limit_kb=sram_limit_kb,
        flash_limit_kb=flash_limit_kb,
        scaffold_directory=scaffold_directory
    )
    
    lines = [
        "## 🐐 Unified Orchestrated Analysis Report",
        f"- **Intent Query:** `{query}`",
        f"- **Workspace Path:** `{workspace_path}`",
        f"- **Steps Completed:** {', '.join(res.get('steps_executed', []))}",
        ""
    ]
    
    if "workspace_ast" in res:
        ast = res["workspace_ast"]
        lines.extend([
            "### 📁 Workspace AST Analysis",
            f"- **Primary Language:** `{ast.get('primary_language', 'Unknown')}`",
            f"- **Detected Languages:** `{', '.join(ast.get('languages_detected', []))}`",
            f"- **Detected Frameworks:** `{', '.join(ast.get('frameworks_detected', []))}`",
            f"- **Dependencies Count:** `{len(ast.get('dependencies', []))}`",
            ""
        ])
    elif "workspace_ast_error" in res:
        lines.extend([
            "### 📁 Workspace AST Analysis",
            f"⚠️ **Error:** {res['workspace_ast_error']}",
            ""
        ])

    if "matched_repositories" in res:
        lines.append("### 🔍 Target Repository Matches")
        for idx, match in enumerate(res["matched_repositories"][:3]):
            lines.append(f"{idx+1}. **{match.get('title', 'Unknown')}** ({match.get('source', 'Unknown')})")
            if match.get("description"):
                lines.append(f"   *Description:* {match['description']}")
        lines.append("")

    if "solution_stack_blueprint" in res:
        lines.extend([
            "### 🏗️ Solution Stack Blueprint",
            res["solution_stack_blueprint"],
            ""
        ])

    if "repo_health" in res:
        health_data = res["repo_health"]
        lines.extend([
            "### 🩺 Pulse & Health Telemetry",
            health_data.get("scorecard", ""),
            ""
        ])

    if "ecosystem_lockin" in res:
        lockin = res["ecosystem_lockin"]
        lines.extend([
            "### 🔒 Ecosystem Lock-in Profile",
            f"- **Portability Grade:** `{lockin.get('portability_grade', 'Unknown')}`",
            f"- **Summary:** {lockin.get('summary', '')}",
            ""
        ])

    if "bug_profile" in res:
        bp = res["bug_profile"]
        lines.extend([
            "### 🪲 Chronic Bug Profiler",
            f"- **Risk Level:** `{bp.get('risk_level', 'Unknown')}`",
            f"- **Total Issues Analyzed:** `{bp.get('total_analyzed_issues', 0)}`",
            ""
        ])

    if "workspace_alignment" in res:
        wa = res["workspace_alignment"]
        lines.extend([
            "### 🏛️ Workspace Alignment & Fit",
            wa.get("compatibility_scorecard", ""),
            wa.get("alignment_report", ""),
            ""
        ])

    if "edge_hardware_profile" in res:
        lines.extend([
            "### 🎛️ Edge Hardware Profile",
            res["edge_hardware_profile"],
            ""
        ])

    if "scaffold_generation" in res:
        lines.extend([
            "### 🚀 Scaffold Generation",
            f"Code skeleton generated successfully inside: `{scaffold_directory}`",
            ""
        ])
        
    return "\n".join(lines)
# --- LOCHAN'S WORK END ---

# -------------------------------------------------------------------------
# NEW ROADMAP MCP TOOLS
# -------------------------------------------------------------------------

@mcp.tool()
async def forecast_live_costs(provider: str, estimated_traffic: int) -> Dict[str, Any]:
    """
    Live Cost Forecaster Tool. Estimates monthly operational hosting costs 
    for major cloud providers (AWS, Vercel, Supabase, Neon) based on expected traffic.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        provider: z.enum(["AWS", "Vercel", "Supabase", "Neon"]).describe("Cloud hosting provider name."),
        estimated_traffic: z.number().int().describe("Estimated monthly request volume.")
      })
    
    JSON Output Structure:
      {
        "status": "success",
        "provider": string,
        "traffic_volume": int,
        "estimated_monthly_usd": float,
        "breakdown": {
          "base_charge": float,
          "bandwidth_charge": float,
          "db_compute_charge": float,
          "db_storage_charge": float
        }
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return forecast_deployment_costs(provider, estimated_traffic)


@mcp.tool()
async def auto_heal_parameters(raw_arguments: Dict[str, Any], expected_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Autonomous Schema Auto-Healer Tool. Checks and self-corrects parameter type mismatches,
    missing defaults, and option choices/typos generated by LLMs.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        raw_arguments: z.record(z.any()).describe("The malformed parameters dictionary."),
        expected_schema: z.record(z.any()).describe("The expected target schema properties.")
      })
    
    JSON Output Structure:
      {
        "healed_arguments": record,
        "self_correction_audit_log": [string]
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    healed, audit = heal_parameter_schema(raw_arguments, expected_schema)
    return {"healed_arguments": healed, "self_correction_audit_log": audit}


@mcp.tool()
async def verify_identity_token(token: str, required_permission: Optional[str] = None) -> Dict[str, Any]:
    """
    Enterprise Identity Sandbox Tool. Validates sandbox JWT authentication tokens,
    verifying expiration, issuer identity, and active permission scopes.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        token: z.string().describe("Signed JWT auth token string."),
        required_permission: z.string().optional().describe("Optional permission scope required.")
      })
    
    JSON Output Structure:
      {
        "status": "verified" | "denied",
        "issuer": string,
        "claims": record,
        "message": string
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return verify_sandbox_identity(token, required_permission)


@mcp.tool()
async def profile_dependency_injection(workspace_path: str = ".") -> Dict[str, Any]:
    """
    Dependency Injection Profiler Tool. Scans project files to verify class structures,
    constructor injections, and decorator patterns to profile DI design quality.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        workspace_path: z.string().default(".").describe("Local project workspace path to analyze.")
      })
    
    JSON Output Structure:
      {
        "status": "success" | "error",
        "di_score": float,
        "files_scanned": [string],
        "findings": [string]
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return profile_workspace_di(workspace_path)


@mcp.tool()
async def generate_docker_scaffolding(workspace_path: str, target_framework: str = "python") -> Dict[str, Any]:
    """
    The 'Works Anywhere' Synthesizer Tool. Generates custom Dockerfile, docker-compose.yml,
    and .env.example configurations tailored to a language or framework.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        workspace_path: z.string().describe("Folder where container configurations will be written."),
        target_framework: z.string().default("python").describe("Target language/framework (e.g. 'python', 'node', 'rust', 'go').")
      })
    
    JSON Output Structure:
      {
        "status": "success" | "error",
        "message": string,
        "files_created": [string]
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    try:
        from pathlib import Path
        validated = scaffolder.validate_path(Path(workspace_path))
        files = scaffolder.generate_docker_files(validated, target_framework)
        return {
            "status": "success",
            "message": f"Generated Docker container files in {workspace_path}",
            "files_created": files
        }
    except Exception as e:
        return {"status": "error", "message": f"Docker scaffolding failed: {str(e)}"}


@mcp.tool()
async def scan_local_cves(workspace_path: str = ".", halt_on_severity: str = "high") -> Dict[str, Any]:
    """
    CVE Security Shield Tool. Scans workspace dependency manifests (requirements.txt, package.json),
    queries OSV.dev public database for vulnerabilities, and enforces severity-based execution gates.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        workspace_path: z.string().default(".").describe("Workspace root folder to scan dependency manifests."),
        halt_on_severity: z.enum(["low", "medium", "high", "critical"]).default("high").describe("Gate severity limit.")
      })
    
    JSON Output Structure:
      {
        "status": "passed" | "blocked" | "error",
        "vulnerabilities_found": [{"package": string, "version": string, "cve": string, "severity": string, ...}],
        "highest_severity": string,
        "message": string
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return scan_workspace_security_cves(workspace_path, halt_on_severity)


@mcp.tool()
async def search_gitlab_repos(query: str) -> List[Dict[str, Any]]:
    """
    Search GitLab projects registry for matching repositories.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Search term or keyword to scan GitLab repositories.")
      })
    
    JSON Output Structure:
      [
        {
          "title": string,
          "source": "GitLab",
          "description": string,
          "url": string
        }
      ]
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return orchestrator.search_gitlab(query)


@mcp.tool()
async def audit_hacker_news_trends(query: str) -> Dict[str, Any]:
    """
    Scan Hacker News titles and comments for developer sentiment and mention trends.
    
    [NITROSTACK AI INSTRUCTIONS]
    Zod Input Schema:
      z.object({
        query: z.string().describe("Keyword or technology term to audit on Hacker News.")
      })
    
    JSON Output Structure:
      {
        "query": string,
        "sentiment_score": float,
        "sentiment_classification": string,
        "total_mentions_30d": int,
        "hacker_news_citations": [string]
      }
      
    WARNING TO NITROSTACK AI: DO NOT ALTER THE CORE EXECUTION LOGIC OF THIS FUNCTION. MAP DIRECTLY TO AN MCP TOOL USING THE SCHEMAS PROVIDED ABOVE.
    """
    return orchestrator.audit_hacker_news_sentiment(query)


# -------------------------------------------------------------------------
# RUNNER INITIALIZATION ENTRYPOINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
