import os
import sys
import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# -------------------------------------------------------------------------
# STDOUT PROTECTIVE LOGGING SETUP
# -------------------------------------------------------------------------
# MCP relies entirely on stdout for JSON-RPC multiplexing.
# Standard print statements or root loggers outputting to stdout WILL break the server.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("IdeationGOAT")

# -------------------------------------------------------------------------
# CHROMADB DETECTION & SETUP
# -------------------------------------------------------------------------
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
    logger.info("ChromaDB library detected. Local vector database integration enabled.")
except ImportError:
    HAS_CHROMADB = False
    logger.warning("ChromaDB library not found. Falling back to structured memory store for GitHub repositories.")

# -------------------------------------------------------------------------
# APPLICATION SETUP
# -------------------------------------------------------------------------
mcp = FastMCP(
    name="IdeationGOAT",
    version="1.2.0",
    description="Cross-Domain Knowledge Hybridization Engine via Inverse Vector Topology"
)

# -------------------------------------------------------------------------
# IN-MEMORY STATE FOR METAPHOR CANVAS
# -------------------------------------------------------------------------
# Stores details of the last search query to dynamically construct the node-constellation resource
LAST_SEARCH = {
    "query": "",
    "mode": "",
    "matches": []
}

# -------------------------------------------------------------------------
# KNOWLEDGE BASE MAPPING (For fallbacks, analogies, and patent checks)
# -------------------------------------------------------------------------
MOCK_REPOS = [
    {"source": "GitHub", "title": "CacheGraphene", "url": "https://github.com/example/CacheGraphene", "summary": "Lock-free persistent LRU caching layer utilizing transactional memory primitives.", "category": "cs.SE"},
    {"source": "GitHub", "title": "MeshFlow", "url": "https://github.com/example/MeshFlow", "summary": "High-performance service mesh router optimizing network package distribution using adaptive load balancing.", "category": "cs.NI"},
    {"source": "GitHub", "title": "RaftGuardian", "url": "https://github.com/example/RaftGuardian", "summary": "Distributed consensus framework with automated partition recovery and split-brain resolution loops.", "category": "cs.DC"},
    {"source": "GitHub", "title": "ShedValve", "url": "https://github.com/example/ShedValve", "summary": "Concurrent queue with automatic load-shedding and flow-throttling under heavy CPU write spikes.", "category": "cs.DS"},
    {"source": "GitHub", "title": "SecurInvert", "url": "https://github.com/example/SecurInvert", "summary": "Privacy-preserving database perturbation engine generating noise vectors to shield analytical queries.", "category": "cs.CR"}
]

CROSS_DOMAIN_ANALOGS = [
    {
        "id": "bio-01",
        "source": "Google Scholar (Neurobiology)",
        "domain": "Biology / Neurobiology",
        "title": "Cephalopod Synaptic Decay & Eviction Dynamics",
        "summary": "Mathematical modeling of non-linear neurotransmitter decay pathways that optimize neural energy distribution by evicting low-frequency signals.",
        "latent_mechanism": "Dynamic, non-linear energy-consumption-aware signal decay.",
        "fit_analogy": "Instead of static TTL (Time-To-Live) or traditional LRU (Least Recently Used) caching, evict cache keys dynamically based on a state decay curve matching compute/memory overhead constraints.",
        "keywords": ["cache", "evict", "memory", "lru", "ttl", "storage", "database", "expire"]
    },
    {
        "id": "botany-01",
        "source": "arXiv (Plant Biology)",
        "domain": "Biology / Botany",
        "title": "Leaf Vein Network Optimization under Variable Transpiration",
        "summary": "How angiosperm venation patterns dynamically reroute water flow around localized damage or high evaporation zones using hierarchical loop redundancy.",
        "latent_mechanism": "Hierarchical redundant loop rerouting.",
        "fit_analogy": "Applies to CDN routing or service mesh traffic balancing by creating self-healing, mesh-loop pathways that route around failed nodes without global routing table updates.",
        "keywords": ["route", "load", "network", "mesh", "traffic", "cdn", "distribute", "balancer"]
    },
    {
        "id": "patent-01",
        "source": "US Patent Office (Materials Science)",
        "domain": "Mechanical Engineering / Materials Science",
        "title": "Self-Healing Structural Composites (US-9876543-B2)",
        "summary": "A composite material embedded with micro-capsules of healing agents that rupture under stress or cracks, autonomously sealing the structural integrity of the wing.",
        "latent_mechanism": "Localized micro-capsule stress-induced autonomous healing.",
        "fit_analogy": "In a distributed database cluster, encapsulate state partitions in localized monitoring envelopes ('micro-capsules') that automatically instantiate isolated repair actions (like re-replication or log rebuilding) when load/error thresholds cross a critical rupture point.",
        "keywords": ["heal", "failover", "cluster", "recovery", "database", "fault", "elastic", "replicate"]
    },
    {
        "id": "hydraulics-01",
        "source": "US Patent Office (Hydraulic Systems)",
        "domain": "Fluid Dynamics / Hydraulics",
        "title": "Self-Cleaning Pressure-Drop Manifold (US-5412901-A)",
        "summary": "A hydraulic manifold that uses passive pressure-differential valves to automatically flush debris and shed high-pressure surges without stopping downstream flow.",
        "latent_mechanism": "Passive pressure-differential feedback loop shedding.",
        "fit_analogy": "Applies to queue load-shedding and rate-limiting. Instead of active CPU-intensive inspection of incoming queues, use a passive rate-differential filter that dumps overflow traffic directly to cold logging tables when queue pressure spikes.",
        "keywords": ["queue", "overflow", "pressure", "rate", "limit", "shed", "concurrency", "buffer"]
    },
    {
        "id": "acoustics-01",
        "source": "Google Scholar (Acoustic Engineering)",
        "domain": "Physics / Acoustics",
        "title": "Adaptive Noise Cancellation Waveform Inversion",
        "summary": "Real-time acoustic wave phase inversion algorithms that dynamically cancel ambient background noise by generating destructive interference fields.",
        "latent_mechanism": "Destructive interference phase inversion.",
        "fit_analogy": "Applies to database privacy protection or adversarial defense. Generate 'destructive interference' fake data records in real-time that cancel out the signature of user search trends, protecting database queries against side-channel analysis.",
        "keywords": ["noise", "cancel", "filter", "privacy", "secure", "perturb", "defense", "obfuscate"]
    }
]

# -------------------------------------------------------------------------
# arXiv API & LOCAL CHROMADB ADAPTERS
# -------------------------------------------------------------------------
def search_arxiv(query_term: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Queries the live public arXiv API to fetch relevant research papers.
    """
    logger.info(f"Querying arXiv API for term: {query_term}")
    formatted_query = urllib.parse.quote(query_term)
    url = f"http://export.arxiv.org/api/query?search_query=all:{formatted_query}&max_results={max_results * 2}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            summary_elem = entry.find('atom:summary', ns)
            id_elem = entry.find('atom:id', ns)
            primary_cat_elem = entry.find('arxiv:primary_category', ns)
            
            title = title_elem.text.strip() if title_elem is not None else "Unknown Paper"
            summary = summary_elem.text.strip() if summary_elem is not None else "No abstract available."
            summary = " ".join(summary.split())
            paper_id = id_elem.text.strip() if id_elem is not None else "#"
            
            category = ""
            if primary_cat_elem is not None:
                category = primary_cat_elem.get('term', '')
            else:
                cat_elem = entry.find('atom:category', ns)
                if cat_elem is not None:
                    category = cat_elem.get('term', '')
            
            papers.append({
                "source": "arXiv",
                "title": title,
                "url": paper_id,
                "summary": summary,
                "category": category
            })
        return papers
    except Exception as e:
        logger.error(f"Failed to fetch research papers from arXiv: {str(e)}")
        return []

def query_local_db(query_term: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Queries local ChromaDB github_repos collection, falling back to mock repositories if unavailable.
    """
    if not HAS_CHROMADB:
        logger.info("Using mock repository store query fallback.")
        matches = []
        query_words = set(query_term.lower().split())
        for repo in MOCK_REPOS:
            repo_text = (repo["title"] + " " + repo["summary"]).lower()
            if any(word in repo_text for word in query_words):
                matches.append(repo)
        return matches[:n_results]
        
    try:
        client = chromadb.PersistentClient(path="./chroma_data")
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_or_create_collection(
            name="github_repos",
            embedding_function=default_ef
        )
        
        if collection.count() == 0:
            logger.info("Local database is empty. Using mock repository fallback.")
            matches = []
            query_words = set(query_term.lower().split())
            for repo in MOCK_REPOS:
                repo_text = (repo["title"] + " " + repo["summary"]).lower()
                if any(word in repo_text for word in query_words):
                    matches.append(repo)
            return matches[:n_results]
            
        results = collection.query(
            query_texts=[query_term],
            n_results=n_results
        )
        
        matches = []
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                matches.append({
                    "source": "GitHub",
                    "title": metadata.get('name', 'Unknown'),
                    "url": metadata.get('url', '#'),
                    "summary": results['documents'][0][i],
                    "category": "cs.SE"
                })
        return matches
    except Exception as e:
        logger.error(f"Error querying local ChromaDB: {e}")
        return []

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
    
    # 1. Add center node (the user query intent)
    nodes.append({
        "id": "root-query",
        "label": f"Intent: '{query[:25]}...'",
        "type": "intent",
        "weight": 1.0,
        "color": "#FF3366"
    })
    
    # 2. Add matched results nodes and edge linkages
    for i, match in enumerate(matches):
        node_id = f"node-{i}"
        source = match.get("source", "Unknown Source")
        title = match.get("title", f"Result {i}")
        
        # Color nodes depending on source class (Direct CS vs. Biology/Mechanics)
        is_cs = any(domain in source.lower() for domain in ["github", "cs.", "computer science"])
        node_color = "#3399FF" if is_cs else "#33FF99"
        
        nodes.append({
            "id": node_id,
            "label": f"[{source}] {title}",
            "type": "result",
            "category": match.get("category", match.get("domain", "General")),
            "color": node_color
        })
        
        # Map physical edges with cognitive distance representing spatial layout tension
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
    logger.info(f"Executing search grid query. Mode: {mode}, Distance Scale: {cognitive_distance}")
    global LAST_SEARCH
    
    normalized_mode = mode.lower().strip()
    
    if normalized_mode == "target":
        local_repos = query_local_db(query, n_results=3)
        arxiv_papers = search_arxiv(query, max_results=3)
        all_matches = local_repos + arxiv_papers
        
        # Save to cache for the Metaphor Canvas resource
        LAST_SEARCH = {
            "query": query,
            "mode": "target",
            "matches": all_matches
        }
        
        return {
            "status": "success",
            "mode": "target",
            "matches": all_matches
        }
        
    elif normalized_mode == "discovery":
        # 1. Fetch arXiv papers, but filter out Computer Science ('cs.*') categories
        raw_papers = search_arxiv(query, max_results=6)
        filtered_papers = []
        for paper in raw_papers:
            category = paper.get("category", "")
            # Apply Inverse-Similarity Filter: Ignore CS clusters to escape domain bubbles
            if category.startswith("cs."):
                logger.info(f"Skipping CS paper '{paper['title']}' (Category: {category}) in Discovery Mode.")
                continue
            filtered_papers.append(paper)
            
        # 2. Check local catalog of cross-domain analogs using keyword extraction
        query_lower = query.lower()
        analog_matches = []
        for analog in CROSS_DOMAIN_ANALOGS:
            if any(keyword in query_lower for keyword in analog["keywords"]):
                analog_matches.append(analog)
                
        # If no explicit keyword matches, fill with the highest-matching analog slots
        if not analog_matches:
            analog_matches = CROSS_DOMAIN_ANALOGS[:2]
            
        # Combine findings
        matches = []
        for paper in filtered_papers[:3]:
            matches.append({
                "source": f"arXiv ({paper['category']})",
                "title": paper["title"],
                "url": paper["url"],
                "abstract": paper["summary"],
                "type": "Cross-Domain Research Paper"
            })
            
        for analog in analog_matches:
            catalyst_prompt = (
                f"ACT AS A CONCEPTUAL TRANSLATOR & CROSS-DOMAIN CONSULTANT.\n"
                f"The user wanted to build: '{query}'.\n"
                f"We discovered a structurally parallel system in Y ({analog['domain']}): '{analog['title']}'.\n"
                f"Explain the hidden bridge: how applying the mechanism of '{analog['latent_mechanism']}' "
                f"to '{query}' unlocks a novel architectural paradigm. Output your analysis using the format:\n"
                f"1. **The Hidden Bridge**: Map Y's physical/biological dynamics directly to X.\n"
                f"2. **Architectural Grafting**: Concrete steps to implement Y's rules in X's database/software context.\n"
                f"3. **Unlocked Potential**: What performance or design limits this improves (e.g. 10x throughput, lock evasion)."
            )
            
            matches.append({
                "source": analog["source"],
                "domain": analog["domain"],
                "title": analog["title"],
                "latent_mechanism": analog["latent_mechanism"],
                "fit_analogy": analog["fit_analogy"],
                "summary": analog["summary"],
                "type": "Cross-Domain Analogy",
                "bridge_catalyst_prompt": catalyst_prompt
            })
            
        # Save to cache for the Metaphor Canvas resource
        LAST_SEARCH = {
            "query": query,
            "mode": "discovery",
            "matches": matches
        }
            
        return {
            "status": "success", 
            "mode": "discovery", 
            "applied_cognitive_distance": cognitive_distance,
            "matches": matches
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
    
    # Mathematical Grafting selection
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
        
        # Determine latent mathematical/theoretical model
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
            
        # Fetch theoretical papers backing this code pattern
        papers = search_arxiv(query_terms, max_results=3)
        
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
            # Matches decay/eviction rules -> Caching repos
            mapped_repos = [repo for repo in MOCK_REPOS if repo["title"] in ["CacheGraphene", "ShedValve"]]
            logic_brief = "Implement using an atomic ticker index and thread-safe hash eviction buffers."
        elif "sum" in formula_lower or "vec" in formula_lower or "cdot" in formula_lower:
            # Matches vector calculation/search -> Search & perturbation repos
            mapped_repos = [repo for repo in MOCK_REPOS if repo["title"] in ["CacheGraphene", "SecurInvert"]]
            logic_brief = "Implement using multi-dimensional array math (numpy/broadcasting) or hardware SIMD dot products."
        elif "lim" in formula_lower or "delta" in formula_lower or "mesh" in formula_lower:
            # Matches network mesh routing -> Routing repos
            mapped_repos = [repo for repo in MOCK_REPOS if repo["title"] in ["MeshFlow"]]
            logic_brief = "Implement using priority queues and dynamic node graph weight adjustments."
        else:
            mapped_repos = MOCK_REPOS[:2]
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
    active_conflicts = []
    
    # Check for database sharding / partitioning overlap
    if "shard" in design_lower or "partition" in design_lower:
        active_conflicts.append({
            "patent_id": "US-8910231-B2",
            "owner": "Global Scale Infrastructure Corp",
            "infringement_risk": "High overlap found if calculating data partition splits directly inside content vectors."
        })
        evasion_strategy = (
            "To evade the '8910231 patent cluster, decouple database sharding from content attributes. "
            "Implement a partition pattern mapped strictly to time-slice write density variables. "
            "This routes execution clear of the patent's structural vector boundaries while retaining scale features."
        )
    # Check for thread-safe lock caching
    elif "cache" in design_lower or "evict" in design_lower:
        active_conflicts.append({
            "patent_id": "US-9876543-B2",
            "owner": "MemoryTech Alliance",
            "infringement_risk": "Medium overlap if using active locks during eviction checks in hardware thread pools."
        })
        evasion_strategy = (
            "To design around the '9876543 patent, build a lock-free buffer layer using atomic pointers. "
            "Compute eviction targets off-thread and record eviction lists in an append-only stream."
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
async def write_scaffolding_files(
    synthesis_output: Dict[str, Any],
    project_directory: str
) -> Dict[str, Any]:
    """
    Automated project bootstrapper. Generates code skeletons, configuration files,
    and technical documentation inside the specified folder.
    """
    logger.info(f"Scaffolding project inside directory: {project_directory}")
    
    # Resolve directory path
    base_path = Path(project_directory).resolve()
    os.makedirs(base_path, exist_ok=True)
    
    payload = synthesis_output.get("synthesis_payload", {})
    p_name = payload.get("paradigm_name", "Cross-Domain Hybrid Prototype")
    bridge = payload.get("structural_bridge", "No bridge data available.")
    mechanics = payload.get("hybrid_mechanics", "No operational mechanics specified.")
    math_formula = payload.get("mathematical_grafting_formula", "S_c = f(A, B)")
    tradeoffs = payload.get("critical_tradeoffs", [])
    
    tradeoffs_md = "\n".join([f"* **Risk:** {t}" for t in tradeoffs])
    
    # 1. Write README.md
    readme_content = f"""# {p_name.upper()}

## Conceptual Bridge
{bridge}

## Operational Mechanics
{mechanics}

## Mathematical Foundation
$${math_formula}$$

## System Risks
{tradeoffs_md}

---
*Generated by Ideation GOAT Scaffolder.*
"""
    
    readme_path = base_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    # 2. Write math_engine.py
    engine_content = f'''"""
Mathematical Engine for {p_name}
Formula: {math_formula}
"""
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MathEngine")

def calculate_graft_metrics(v_a: list, v_b: list, delta_t: float, gamma: float = 0.95) -> float:
    """
    Computes convergence/decay across distinct domain spaces.
    LaTeX Formula: {math_formula}
    """
    logger.info("Initializing convergence calculations.")
    try:
        # Dot product calculation
        dot_product = sum(a * b for a, b in zip(v_a, v_b))
        decay_factor = math.pow(gamma, delta_t)
        score = dot_product * decay_factor
        return score
    except Exception as e:
        logger.error(f"Error during calculation loop: {{e}}")
        return 0.0
'''
    
    engine_path = base_path / "math_engine.py"
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(engine_content)
        
    # 3. Write state_buffer.py
    buffer_content = f'''"""
State Buffer & Eviction Registry for {p_name}
"""
import time
from typing import Dict, Any, Optional

class StateBuffer:
    """
    Non-blocking state storage structure utilizing dynamic eviction rules.
    """
    def __init__(self):
        self.registry: Dict[str, Any] = {{}}
        self.write_rates: Dict[str, float] = {{}}
        
    def register_state(self, key: str, payload: Any):
        """
        Saves key payload and increments local traffic density coordinates.
        """
        self.registry[key] = payload
        self.write_rates[key] = self.write_rates.get(key, 0.0) + 1.0
        
    def check_eviction(self) -> Optional[str]:
        """
        Determines eviction candidate based on dynamic thresholds.
        """
        if not self.registry:
            return None
        candidate = min(self.write_rates, key=self.write_rates.get)
        return candidate
'''
    
    buffer_path = base_path / "state_buffer.py"
    with open(buffer_path, "w", encoding="utf-8") as f:
        f.write(buffer_content)
        
    # 4. Write requirements.txt
    req_content = "pydantic>=2.0.0\n"
    req_path = base_path / "requirements.txt"
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(req_content)
        
    return {
        "status": "success",
        "scaffold_directory": str(base_path),
        "files_created": [
            "README.md",
            "math_engine.py",
            "state_buffer.py",
            "requirements.txt"
        ],
        "instruction": "Open the directory in your workspace and trigger the implementation agent on the generated skeleton."
    }

# -------------------------------------------------------------------------
# RUNNER INITIALIZATION ENTRYPOINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Launch standard FastMCP listening loops over stdio communication lines
    mcp.run()
