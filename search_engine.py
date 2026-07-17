import logging
import urllib.request
import json
from typing import List, Dict, Any
from config import settings
from arxiv_client import ArXivClient
from scholar_client import ScholarClient
from patent_client import PatentClient

logger = logging.getLogger("IdeationGOAT.SearchEngine")

try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

class CrossDomainSearchEngine:
    """
    Search engine managing direct index matching (Target Mode)
    and cross-domain structural analog matching (Discovery Mode).
    """
    
    def __init__(self):
        self.arxiv_client = ArXivClient()
        self.scholar_client = ScholarClient()
        self.patent_client = PatentClient()
        self.mock_repos = [
            {"source": "GitHub", "title": "CacheGraphene", "url": "https://github.com/example/CacheGraphene", "summary": "Lock-free persistent LRU caching layer utilizing transactional memory primitives.", "category": "cs.SE"},
            {"source": "GitHub", "title": "MeshFlow", "url": "https://github.com/example/MeshFlow", "summary": "High-performance service mesh router optimizing network package distribution using adaptive load balancing.", "category": "cs.NI"},
            {"source": "GitHub", "title": "RaftGuardian", "url": "https://github.com/example/RaftGuardian", "summary": "Distributed consensus framework with automated partition recovery and split-brain resolution loops.", "category": "cs.DC"},
            {"source": "GitHub", "title": "ShedValve", "url": "https://github.com/example/ShedValve", "summary": "Concurrent queue with automatic load-shedding and flow-throttling under heavy CPU write spikes.", "category": "cs.DS"},
            {"source": "GitHub", "title": "SecurInvert", "url": "https://github.com/example/SecurInvert", "summary": "Privacy-preserving database perturbation engine generating noise vectors to shield analytical queries.", "category": "cs.CR"}
        ]
        
        self.cross_domain_analogs = [
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
                "source": "Google Patents (Materials Science)",
                "domain": "Mechanical Engineering / Materials Science",
                "title": "Self-Healing Structural Composites (US-9876543-B2)",
                "summary": "A composite material embedded with micro-capsules of healing agents that rupture under stress or cracks, autonomously sealing the structural integrity of the wing.",
                "latent_mechanism": "Localized micro-capsule stress-induced autonomous healing.",
                "fit_analogy": "In a distributed database cluster, encapsulate state partitions in localized monitoring envelopes ('micro-capsules') that automatically instantiate isolated repair actions (like re-replication or log rebuilding) when load/error thresholds cross a critical rupture point.",
                "keywords": ["heal", "failover", "cluster", "recovery", "database", "fault", "elastic", "replicate"]
            },
            {
                "id": "hydraulics-01",
                "source": "Google Patents (Hydraulic Systems)",
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

    def query_vector_db(self, query_term: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the vector database:
        1. Supabase (pgvector RPC) if SUPABASE_URL and SUPABASE_KEY are set.
        2. Pinecone if PINECONE_API_KEY and PINECONE_INDEX_URL are set.
        3. Local ChromaDB as a standard fallback.
        """
        embedding = None
        if HAS_CHROMADB:
            try:
                default_ef = embedding_functions.DefaultEmbeddingFunction()
                embedding = default_ef([query_term])[0]
            except Exception as e:
                logger.warning(f"Could not compute embedding locally: {str(e)}")

        # 1. Supabase (pgvector RPC)
        if settings.SUPABASE_URL and settings.SUPABASE_KEY and embedding is not None:
            try:
                url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/rpc/match_repositories"
                headers = {
                    "Content-Type": "application/json",
                    "apikey": settings.SUPABASE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}"
                }
                body = {
                    "query_embedding": embedding,
                    "match_threshold": 0.2,
                    "match_count": n_results
                }
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                
                matches = []
                for item in res_data:
                    matches.append({
                        "source": "GitHub (Supabase)",
                        "title": item.get('name', 'Unknown'),
                        "url": item.get('url', '#'),
                        "summary": item.get('summary', '') or item.get('description', ''),
                        "language": item.get('language', 'Unknown'),
                        "stars": int(item.get('stars', 0)),
                        "category": item.get('category', 'cs.SE')
                    })
                if matches:
                    logger.info(f"Retrieved {len(matches)} matches from Supabase pgvector.")
                    return matches
            except Exception as e:
                logger.error(f"Supabase pgvector query failed: {str(e)}. Falling back.")

        # 2. Pinecone
        if settings.PINECONE_API_KEY and settings.PINECONE_INDEX_URL and embedding is not None:
            try:
                url = f"{settings.PINECONE_INDEX_URL.rstrip('/')}/query"
                headers = {
                    "Content-Type": "application/json",
                    "Api-Key": settings.PINECONE_API_KEY
                }
                body = {
                    "vector": embedding,
                    "topK": n_results,
                    "includeMetadata": True
                }
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                
                matches = []
                for item in res_data.get('matches', []):
                    metadata = item.get('metadata', {})
                    matches.append({
                        "source": "GitHub (Pinecone)",
                        "title": metadata.get('name', 'Unknown'),
                        "url": metadata.get('url', '#'),
                        "summary": metadata.get('summary', '') or metadata.get('description', ''),
                        "language": metadata.get('language', 'Unknown'),
                        "stars": int(metadata.get('stars', 0)),
                        "category": metadata.get('category', 'cs.SE')
                    })
                if matches:
                    logger.info(f"Retrieved {len(matches)} matches from Pinecone index.")
                    return matches
            except Exception as e:
                logger.error(f"Pinecone query failed: {str(e)}. Falling back.")

        # 3. Fallback to local ChromaDB
        return self.query_local_db(query_term, n_results)

    def query_local_db(self, query_term: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves repositories from ChromaDB or falls back to mock list.
        """
        if not HAS_CHROMADB:
            logger.info("ChromaDB library not available. Defaulting to mock local repositories.")
            return self._query_mock_repos(query_term, n_results)
            
        try:
            client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
            default_ef = embedding_functions.DefaultEmbeddingFunction()
            collection = client.get_or_create_collection(
                name=settings.CHROMADB_COLLECTION,
                embedding_function=default_ef
            )
            
            if collection.count() == 0:
                logger.info("ChromaDB collection is empty. Defaulting to mock local repositories.")
                return self._query_mock_repos(query_term, n_results)
                
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
                        "language": metadata.get('language', 'Unknown'),
                        "stars": int(metadata.get('stars', 0)),
                        "category": "cs.SE"
                    })
            return matches
        except Exception as e:
            logger.error(f"Error executing local ChromaDB vector query: {str(e)}")
            return self._query_mock_repos(query_term, n_results)

    def _query_mock_repos(self, query_term: str, n_results: int) -> List[Dict[str, Any]]:
        matches = []
        query_words = set(query_term.lower().split())
        for repo in self.mock_repos:
            repo_text = (repo["title"] + " " + repo["summary"]).lower()
            if any(word in repo_text for word in query_words):
                matches.append(repo)
        return matches[:n_results]

    def search_target(self, query: str) -> List[Dict[str, Any]]:
        """
        Target Mode: Gathers direct implementation code from GitHub and papers from arXiv.
        """
        local_matches = self.query_vector_db(query, n_results=3)
        arxiv_matches = self.arxiv_client.search(query, max_results=settings.ARXIV_MAX_RESULTS)
        return local_matches + arxiv_matches

    def search_discovery(self, query: str, cognitive_distance: float) -> List[Dict[str, Any]]:
        """
        Discovery Mode: Inverse-Similarity Serendipity Search.
        Skips exact CS domain matches, forcing search into biology, mechanics, physics.
        """
        raw_papers = self.arxiv_client.search(query, max_results=4)
        scholar_papers = self.scholar_client.search(query, max_results=3)
        
        # Combine academic papers
        all_academic = []
        for paper in raw_papers:
            all_academic.append(paper)
        for paper in scholar_papers:
            all_academic.append({
                "source": "Google Scholar",
                "title": paper["title"],
                "url": paper["url"],
                "summary": paper["summary"],
                "category": "non-cs"
            })
            
        # Apply Inverse-Similarity Filter: Ignore CS clusters to escape domain bubbles
        filtered_papers = []
        for paper in all_academic:
            category = paper.get("category", "")
            if category.startswith("cs."):
                logger.info(f"Filtering out CS paper '{paper['title']}' (Category: {category}) in Discovery Mode.")
                continue
            filtered_papers.append(paper)
            
        # Match query keywords to cross-domain analogy catalog
        query_lower = query.lower()
        analog_matches = []
        for analog in self.cross_domain_analogs:
            if any(kw in query_lower for kw in analog["keywords"]):
                analog_matches.append(analog)
                
        if not analog_matches:
            analog_matches = self.cross_domain_analogs[:2]
            
        matches = []
        for paper in filtered_papers[:3]:
            category_suffix = f" - {paper['category']}" if paper.get('category') else ""
            matches.append({
                "source": f"Academic Research ({paper['source']}{category_suffix})",
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
            
        return matches

    def compose_solution_stack(self, query: str, n_results: int = 3) -> str:
        """
        Decompose a complex system idea into multiple architectural layers and query the database
        to compose a cohesive solution stack of open-source frameworks.
        """
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
        
        query_lower = query.lower()
        active_layers = {}
        
        for layer_name, config in layers.items():
            if any(kw in query_lower for kw in config["keywords"]) or len(query_lower.split()) < 4:
                active_layers[layer_name] = config
                
        if not active_layers:
            active_layers = layers
            
        output = []
        output.append(f"# 🏗️ Architectural Solution Stack Blueprint for: '{query}'\n")
        output.append("This blueprint was generated by analyzing the sub-components of your idea and matching them against indexed frameworks.\n")
        
        for layer_name, config in active_layers.items():
            layer_query = f"{query} {config['subquery']}"
            results = self.query_vector_db(layer_query, n_results=n_results)
            
            output.append(f"### 📦 Layer: {layer_name}")
            
            if not results:
                output.append("No matched components found in the local index for this layer.")
                output.append("")
                continue
                
            for i, match in enumerate(results):
                title = match.get("title", "Unknown")
                url = match.get("url", "#")
                summary = match.get("summary", "No details available.")
                
                stars = match.get("stars", 0)
                if stars:
                    stars_str = f"{stars / 1000:.1f}k" if stars >= 1000 else str(stars)
                    stars_part = f" | *Stars:* ⭐ {stars_str}"
                else:
                    stars_part = ""
                    
                output.append(f"{i+1}. **[{title}]({url})**")
                output.append(f"   *Language:* `{match.get('language', 'Unknown')}`{stars_part}")
                snippet = summary[:200] + "..." if len(summary) > 200 else summary
                output.append(f"   *Role:* {snippet}")
            output.append("")
            
        output.append("---")
        output.append("### 🔗 Integration & Compatibility Guide")
        output.append("Ensure the components you select share a common language ecosystem or communicate via standardized network protocols (REST, WebSockets, or gRPC). For instance, a TypeScript-based offline storage engine pairs perfectly with a React Native or Node.js runtime.")
        
        return "\n".join(output)

    def synthesize_why_fits(self, query: str, matches: List[Dict[str, Any]]) -> str:
        """
        Uses an LLM (Gemini or OpenAI) to generate a brief summary explaining
        why the top matched frameworks fit the user's idea and how they solve it.
        """
        if not matches:
            return "No matches found to synthesize."
            
        summary_text = "\n".join([f"- {m.get('title', m.get('name', 'Unknown'))}: {m.get('summary', m.get('abstract', ''))}" for m in matches[:3]])
        
        # 1. Try Gemini
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={settings.GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                prompt_content = (
                    f"The user wants to build: '{query}'.\n"
                    f"Here are the top matched tools/frameworks:\n{summary_text}\n"
                    f"Provide a concise, 2-3 sentence expert synthesis explaining why these options "
                    f"are a good fit and how the developer should combine or use them."
                )
                body = {
                    "contents": [{
                        "parts": [{"text": prompt_content}]
                    }]
                }
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            except Exception as e:
                logger.warning(f"Gemini synthesis failed: {str(e)}")
                
        # 2. Try OpenAI
        if settings.OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
                }
                prompt_content = (
                    f"The user wants to build: '{query}'.\n"
                    f"Here are the top matched tools/frameworks:\n{summary_text}\n"
                    f"Provide a concise, 2-3 sentence expert synthesis explaining why these options "
                    f"are a good fit and how the developer should combine or use them."
                )
                body = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt_content}],
                    "max_tokens": 150
                }
                req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                
                text = res_data['choices'][0]['message']['content']
                return text.strip()
            except Exception as e:
                logger.warning(f"OpenAI synthesis failed: {str(e)}")
                
        # 3. Dynamic Rule-based Fallback (High-quality heuristic)
        explanation = []
        explanation.append("### 🧠 Architectural Synthesis (Rule-based Fallback)")
        explanation.append(f"Based on your requirements to build **'{query}'**, we matched the following frameworks:")
        for m in matches[:3]:
            title = m.get('title', m.get('name', 'Unknown'))
            source = m.get('source', 'Index')
            explanation.append(f"- **{title}** ({source}): Best suited to handle the core operational characteristics of your intent.")
        
        explanation.append("\n**Recommendation**: Integrate these components using clean interfaces. For example, wrap the storage engine within a repository adapter and access it from your business logic layer to prevent direct dependency coupling.")
        return "\n".join(explanation)


