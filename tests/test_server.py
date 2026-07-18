import os
import sys
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Dict, Any

# Adjust path to import root modules properly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the server tools and data structures to test
import server
from server import (
    search_knowledge_grid,
    breed_concepts,
    bridge_code_and_theory,
    assess_viability,
    write_scaffolding_files,
    get_metaphor_canvas,
    verify_workspace_fit,
    compose_solution_stack,
    get_repo_health,
    profile_repo_hardware_footprint,
    align_system_architecture,
    search_academic_papers,
    analyze_workspace_ast,
    check_repo_health as server_check_repo_health,
    check_ecosystem_lockin as server_check_ecosystem_lockin,
    analyze_repo_bugs as server_analyze_repo_bugs,
    orchestrate_architectural_workflow
)

# -------------------------------------------------------------------------
# MOCK DATA FOR arXiv XML RESPONSES
# -------------------------------------------------------------------------
# A mock XML string that matches the Atom XML structure of the arXiv API.
# It contains one non-CS paper (q-bio.NC) and one CS paper (cs.DS) to test 
# the domain-filtering algorithm of Discovery Mode.
MOCK_ARXIV_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>A Formalization of In-Memory Eviction Algorithms</title>
    <summary>We present a formal framework for understanding cache eviction using neural decay processes.</summary>
    <id>http://arxiv.org/abs/2401.1234v1</id>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="q-bio.NC"/>
  </entry>
  <entry>
    <title>High-Performance Graph Partitioning for Networks</title>
    <summary>This paper introduces graph-theoretic flow optimizations in CDN networks.</summary>
    <id>http://arxiv.org/abs/2402.5678v1</id>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.DS"/>
  </entry>
</feed>
"""

class TestIdeationGoatServer(unittest.TestCase):
    """
    Test suite for the Ideation GOAT MCP server tools and resources.
    Designed for maximum execution speed by mocking external HTTP endpoints and DB states.
    """

    def setUp(self):
        """
        Runs before each test case. Resets the global memory state.
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        server.LAST_SEARCH = {
            "query": "",
            "mode": "",
            "matches": []
        }
        # Mock Scholar and Patent clients to avoid real network hits during existing tests
        from unittest.mock import MagicMock
        server.search_engine.scholar_client.search = MagicMock(return_value=[])
        server.search_engine.patent_client.search = MagicMock(return_value=[])

    def tearDown(self):
        """
        Cleans up the event loop after the test.
        """
        self.loop.close()
        asyncio.set_event_loop(None)

    @patch("urllib.request.urlopen")
    def test_search_knowledge_grid_target_mode(self, mock_urlopen):
        """
        Verify that Target Mode returns direct domain matches and queries arXiv.
        """
        # Mocking the arXiv network response
        mock_response = MagicMock()
        mock_response.read.return_value = MOCK_ARXIV_XML
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Execute target mode search query asynchronously
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            search_knowledge_grid(query="caching", mode="target")
        )

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["mode"], "target")
        
        # Verify result contains matches from both local repositories and arXiv
        matches = response["matches"]
        self.assertGreater(len(matches), 0)
        
        # Check that we received mock repositories (e.g. CacheGraphene or similar)
        sources = [m["source"] for m in matches]
        self.assertIn("GitHub", sources)
        self.assertIn("arXiv", sources)

    @patch("urllib.request.urlopen")
    def test_search_knowledge_grid_discovery_mode(self, mock_urlopen):
        """
        Verify that Discovery Mode ignores CS papers (Inverse-Similarity Filter)
        and correctly appends biological/physical analogs.
        """
        mock_response = MagicMock()
        mock_response.read.return_value = MOCK_ARXIV_XML
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Execute discovery mode search query
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            search_knowledge_grid(query="caching and eviction", mode="discovery", cognitive_distance=0.8)
        )

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["mode"], "discovery")
        self.assertEqual(response["applied_cognitive_distance"], 0.8)

        matches = response["matches"]
        
        # Verify the CS paper (cs.DS) was filtered out and q-bio.NC was kept
        arxiv_categories = [m["source"] for m in matches if "arXiv" in m["source"]]
        for category in arxiv_categories:
            self.assertNotIn("cs.", category)
            self.assertIn("q-bio.", category)

        # Verify that cross-domain analogies (e.g. Cephalopod Neural Decay) were added
        types = [m.get("type") for m in matches]
        self.assertIn("Cross-Domain Analogy", types)
        
        # Verify that the catalyst prompt field exists for cross-domain bridging
        analogy_node = next(m for m in matches if m.get("type") == "Cross-Domain Analogy")
        self.assertIn("bridge_catalyst_prompt", analogy_node)

    def test_breed_concepts(self):
        """
        Tests the Breeding tool by cross-pollinating two distinct conceptual structures.
        """
        concept_a = {
            "title": "CacheGraphene",
            "description": "Thread-safe LRU database memory storage cache",
            "domain_context": "Computer Science"
        }
        concept_b = {
            "title": "Cephalopod Neurons",
            "description": "Non-linear neurotransmitter decay optimizing brain energy levels",
            "domain_context": "Marine Biology"
        }

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            breed_concepts(concept_a=concept_a, concept_b=concept_b)
        )

        self.assertEqual(response["status"], "hybridization_complete")
        
        payload = response["synthesis_payload"]
        self.assertEqual(payload["paradigm_name"], "Cephalopod Neurons-Infused CacheGraphene Architecture")
        self.assertIn("mathematical_grafting_formula", payload)
        self.assertIn("bridge_catalyst_prompt", payload)

    @patch("urllib.request.urlopen")
    def test_bridge_code_and_theory_code_to_math(self, mock_urlopen):
        """
        Test translating code logic into mathematical representations and searching papers.
        """
        mock_response = MagicMock()
        mock_response.read.return_value = MOCK_ARXIV_XML
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        code_snippet = """
        def check_eviction(key):
            if time.time() - creation_times[key] > ttl:
                evict(key)
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            bridge_code_and_theory(code_snippet=code_snippet)
        )

        self.assertEqual(response["translation_direction"], "Code to Theory")
        self.assertIn("decay", response["derived_mathematical_paradigm"].lower())
        self.assertIn("D_t", response["derived_latex_equations"])
        self.assertTrue(len(response["matching_theoretical_papers"]) > 0)

    def test_bridge_code_and_theory_math_to_code(self):
        """
        Test translating LaTeX equations into software codebase recommendations.
        """
        latex_formula = r"D_t = D_0 \cdot e^{-\lambda t}"

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            bridge_code_and_theory(latex_formula=latex_formula)
        )

        self.assertEqual(response["translation_direction"], "Theory to Code")
        self.assertIn("eviction", response["software_implementation_logic"])
        
        templates = [r["title"] for r in response["matched_codebase_templates"]]
        self.assertIn("CacheGraphene", templates)

    def test_assess_viability_collision_detection(self):
        """
        Test that patent checks trigger appropriate evasion vectors.
        """
        # Testing a database sharding concept
        loop = asyncio.get_event_loop()
        sharding_check = loop.run_until_complete(
            assess_viability(system_design="Distributed cluster database with content vector sharding.")
        )
        self.assertTrue(len(sharding_check["identified_conflicts"]) > 0)
        self.assertIn("time-slice write density", sharding_check["defensive_evasion_vector"])

        # Testing a clean concept with no patent matches
        clean_check = loop.run_until_complete(
            assess_viability(system_design="A modular UI templating compiler for visual CSS grids.")
        )
        self.assertEqual(len(clean_check["identified_conflicts"]), 0)
        self.assertIn("GPL-compatible", clean_check["defensive_evasion_vector"])

    def test_write_scaffolding_files(self):
        """
        Verify that scaffolding correctly boots directories and skeleton code inside the workspace.
        """
        synthesis_output = {
            "synthesis_payload": {
                "paradigm_name": "Test-Grafted Cache Engine",
                "structural_bridge": "Mock bridge connecting tests to code.",
                "hybrid_mechanics": "Rupture states and decay loops.",
                "mathematical_grafting_formula": "S_c = f(A, B)",
                "critical_tradeoffs": ["High overhead"]
            }
        }

        # Create isolated temporary directory inside workspace for testing
        with TemporaryDirectory(dir="./") as temp_dir:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                write_scaffolding_files(synthesis_output=synthesis_output, project_directory=temp_dir)
            )

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["scaffold_directory"], str(Path(temp_dir).resolve()))

            # Verify that files were physically created on disk
            for filename in result["files_created"]:
                file_path = Path(temp_dir) / filename
                self.assertTrue(file_path.exists(), f"File {filename} was not created.")

            # Verify contents of math_engine.py
            with open(Path(temp_dir) / "math_engine.py", "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("calculate_graft_metrics", content)
                self.assertIn("S_c = f(A, B)", content)

    def test_scaffolder_security_path_traversal_prevention(self):
        """
        Verify that scaffolding files outside the allowed workspace root is prevented.
        """
        synthesis_output = {
            "synthesis_payload": {
                "paradigm_name": "Test-Grafted Cache Engine",
                "structural_bridge": "Mock bridge connecting tests to code.",
                "hybrid_mechanics": "Rupture states and decay loops.",
                "mathematical_grafting_formula": "S_c = f(A, B)",
                "critical_tradeoffs": ["High overhead"]
            }
        }
        
        # Deliberately use a path outside the workspace root (e.g. system temp directory)
        # to trigger the path validation security filter.
        with TemporaryDirectory() as outside_temp_dir:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                write_scaffolding_files(synthesis_output=synthesis_output, project_directory=outside_temp_dir)
            )
            
            self.assertEqual(result["status"], "error")
            self.assertIn("Security Violation", result["message"])

    @patch("urllib.request.urlopen")
    def test_metaphor_canvas_resource(self, mock_urlopen):
        """
        Verify that the metaphor canvas resource correctly returns the graph topology
        for the last executed search.
        """
        mock_response = MagicMock()
        mock_response.read.return_value = MOCK_ARXIV_XML
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Execute a search first to populate the canvas state
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            search_knowledge_grid(query="caching", mode="target")
        )

        # Retrieve metaphor canvas constellation
        canvas = get_metaphor_canvas()
        
        self.assertEqual(canvas["status"], "active")
        self.assertEqual(canvas["last_query"], "caching")
        self.assertEqual(canvas["mode_executed"], "target")

        # Verify that nodes and edges are populated correctly
        topology = canvas["graph_topology"]
        self.assertTrue(len(topology["nodes"]) > 0)
        self.assertTrue(len(topology["edges"]) > 0)
        
        # Verify edges connect search origin to results
        root_node = next(n for n in topology["nodes"] if n["id"] == "root-query")
        self.assertIn("Intent", root_node["label"])

    @patch("workspace_analyzer.Github")
    def test_verify_workspace_fit(self, mock_github):
        # Setup mock Github client
        mock_g = MagicMock()
        mock_github.return_value = mock_g
        mock_repo = MagicMock()
        mock_repo.language = "Python"
        mock_repo.license.spdx_id = "Apache-2.0"
        mock_g.get_repo.return_value = mock_repo

        # Create a temp directory representing a Python workspace
        with TemporaryDirectory(dir="./") as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("mcp>=1.0.0")

            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(
                verify_workspace_fit(repo_name="psf/requests", workspace_path=temp_dir)
            )
            self.assertIn("Scorecard", res)
            self.assertIn("Python", res)
            self.assertIn("Apache-2.0", res)
            self.assertIn("Compatible", res)

    def test_compose_solution_stack(self):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            compose_solution_stack(query="secure database cache", n_results=1)
        )
        self.assertIn("Solution Stack Blueprint", res)
        self.assertIn("Database", res)
        self.assertIn("CacheGraphene", res)

    @patch("urllib.request.urlopen")
    @patch("repo_profiler.Github")
    def test_get_repo_health(self, mock_github, mock_urlopen):
        # Mock OSV.dev call
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"vulns": []}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Mock Github repo metadata
        mock_g = MagicMock()
        mock_github.return_value = mock_g
        mock_repo = MagicMock()
        mock_repo.stargazers_count = 1000
        mock_repo.forks_count = 200
        mock_repo.open_issues_count = 5
        mock_repo.language = "Python"
        mock_repo.description = "Test request repo"
        from datetime import datetime, timezone
        mock_repo.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        mock_repo.pushed_at = datetime.now(timezone.utc)
        mock_repo.size = 2048
        
        # Commits mock
        mock_commit = MagicMock()
        mock_commit.sha = "abcdef123"
        mock_repo.get_commits.return_value = [mock_commit]
        mock_repo.get_pulls.return_value = []
        mock_g.get_repo.return_value = mock_repo

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            get_repo_health(repo_name="psf/requests")
        )
        self.assertIn("Pulse & Health Telemetry", res)
        self.assertIn("Vitality Score", res)
        self.assertIn("1,000", res)

    @patch("repo_profiler.Github")
    def test_profile_repo_hardware_footprint(self, mock_github):
        mock_g = MagicMock()
        mock_github.return_value = mock_g
        mock_repo = MagicMock()
        mock_repo.size = 500
        mock_repo.language = "C/C++"
        
        # Mock file structures (returns CMakeLists.txt and headers)
        mock_file_1 = MagicMock()
        mock_file_1.name = "CMakeLists.txt"
        mock_file_2 = MagicMock()
        mock_file_2.name = "main.h"
        mock_file_2.path = "main.h"
        mock_file_2.decoded_content = b"void run_mcu();"
        mock_repo.get_contents.side_effect = lambda path: (
            [mock_file_1, mock_file_2] if path == "" else mock_file_2
        )
        mock_g.get_repo.return_value = mock_repo

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            profile_repo_hardware_footprint(repo_name="lvgl/lvgl", target_hardware="ESP32")
        )
        self.assertIn("Edge-Deploy Footprint Profile", res)
        self.assertIn("ESP32", res)
        self.assertIn("Bare-metal C/C++", res)

    def test_align_system_architecture(self):
        # Create a temp directory representing Clean Hexagonal architecture layout
        with TemporaryDirectory(dir="./") as temp_dir:
            os.makedirs(Path(temp_dir) / "domain" / "ports", exist_ok=True)
            os.makedirs(Path(temp_dir) / "infrastructure" / "adapters", exist_ok=True)

            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(
                align_system_architecture(repo_name="sqlalchemy", workspace_path=temp_dir)
            )
            self.assertIn("Architectural Vector Alignment Report", res)
            self.assertIn("Clean / Hexagonal", res)
            self.assertIn("Database", res)

    @patch('urllib.request.urlopen')
    def test_scholar_client_search(self, mock_urlopen):
        # Mock Response
        from unittest.mock import MagicMock
        import json
        sem_response = MagicMock()
        sem_response.read.return_value = json.dumps({
            "data": [{
                "paperId": "quantum-cache-id",
                "title": "Quantum Caching in Neurobiology",
                "abstract": "A study of quantum cache effects.",
                "citationCount": 42,
                "externalIds": {
                    "DOI": "10.1000/xyz123"
                },
                "openAccessPdf": {
                    "url": "https://example.com/semantic_oa.pdf"
                }
            }]
        }).encode('utf-8')

        unpaywall_response = MagicMock()
        unpaywall_response.read.return_value = json.dumps({
            "is_oa": True,
            "best_oa_location": {
                "url_for_pdf": "https://example.com/quantum.pdf"
            }
        }).encode('utf-8')

        mock_urlopen.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=sem_response)),
            MagicMock(__enter__=MagicMock(return_value=unpaywall_response))
        ]
    
        from scholar_client import ScholarClient
        client = ScholarClient()
        papers = client.search("quantum cache")
    
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["title"], "Quantum Caching in Neurobiology")
        self.assertEqual(papers[0]["citations"], 42)
        self.assertEqual(papers[0]["url"], "https://example.com/quantum.pdf")
        self.assertEqual(papers[0]["doi"], "10.1000/xyz123")

    @patch('urllib.request.urlopen')
    def test_patent_client_search(self, mock_urlopen):
        from unittest.mock import MagicMock
        import json
        from config import settings
        settings.GOOGLE_PATENTS_API_KEY = "fake_patents_key"  # force API execution path
        serpapi_response = MagicMock()
        serpapi_response.read.return_value = json.dumps({
            "organic_results": [{
                "patent_id": "patent/US8110241B2/en",
                "patent_link": "https://patents.google.com/patent/US8110241B2/en",
                "title": "Cache Eviction Composite Systems",
                "snippet": "A method to evict items.",
                "publication_date": "2026-01-01",
                "publication_number": "9999999"
            }]
        }).encode('utf-8')

        mock_urlopen.return_value.__enter__.return_value = serpapi_response
 
        from patent_client import PatentClient
        client = PatentClient()
        patents = client.search("cache eviction")
 
        self.assertEqual(len(patents), 1)
        self.assertEqual(patents[0]["patent_number"], "9999999")
        self.assertEqual(patents[0]["title"], "Cache Eviction Composite Systems")
        settings.GOOGLE_PATENTS_API_KEY = None  # restore

    @patch('urllib.request.urlopen')
    def test_search_academic_papers_tool(self, mock_urlopen):
        # We need to restore the mock for scholar search in this test case
        from unittest.mock import MagicMock
        import json
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "organic_results": [{
                "title": "Quantum Caching in Neurobiology",
                "publication_info": {
                    "summary": "A study of quantum cache effects."
                },
                "link": "https://example.com/quantum",
                "inline_links": {
                    "cited_by": {
                        "total": 42
                    }
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        server.search_engine.scholar_client.search = MagicMock(return_value=[{
            "source": "Semantic Scholar",
            "title": "Quantum Caching in Neurobiology",
            "url": "https://example.com/quantum",
            "summary": "A study of quantum cache effects.",
            "citations": 42
        }])

        with patch.object(server.search_engine.arxiv_client, 'search', return_value=[{"title": "ArXiv Paper", "url": "url", "summary": "summary", "category": "cs.SE", "source": "arXiv"}]):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(
                search_academic_papers(query="cache", max_results=2)
            )
            self.assertEqual(res["status"], "success")
            self.assertEqual(len(res["arxiv_results"]), 1)
            self.assertEqual(len(res["scholar_results"]), 1)

    def test_analyze_workspace_ast(self):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            analyze_workspace_ast(workspace_path=".")
        )
        self.assertIn("Workspace AST & Architecture Profile", res)
        self.assertIn("Python", res)

    @patch("server.analyze_repo_health")
    def test_check_repo_health_tool(self, mock_analyze):
        mock_analyze.return_value = {
            "health_score": 90,
            "status": "Healthy",
            "flags": [],
            "metrics": {
                "repo": "psf/requests",
                "cve_count": 0,
                "last_commit_date": "2026-07-09",
                "contributors_count": 10,
                "archived": False
            }
        }
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            server_check_repo_health(repository="psf/requests")
        )
        self.assertIn("Open-Source Health & Tech Debt Audit", res)
        self.assertIn("90 / 100", res)
        self.assertIn("Healthy", res)

    @patch("server.run_lockin_profiler")
    def test_check_ecosystem_lockin_tool(self, mock_lockin):
        mock_lockin.return_value = {
            "repo": "psf/requests",
            "portability_grade": "A",
            "total_dependencies_checked": 0,
            "locked_dependencies": [],
            "summary": "This framework earns a Grade A for portability."
        }
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            server_check_ecosystem_lockin(repository="psf/requests")
        )
        self.assertIn("Ecosystem Lock-In & Portability Profile", res)
        self.assertIn("- **Portability Grade:** `A`", res)

    @patch("server.run_bug_profiler")
    def test_analyze_repo_bugs_tool(self, mock_bugs):
        mock_bugs.return_value = {
            "repo": "psf/requests",
            "total_analyzed_issues": 10,
            "risk_level": "Low",
            "top_pitfalls": [
                {
                    "label": "Connection timeout issues",
                    "percentage": 20.0,
                    "count": 2,
                    "example_issues": ["Timeout when fetching large file"],
                    "is_critical": False
                }
            ]
        }
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            server_analyze_repo_bugs(repository="psf/requests")
        )
        self.assertIn("Chronic Bug Profiler & Issue Landscape", res)
        self.assertIn("Connection timeout issues", res)

    def test_orchestrate_architectural_workflow_tool(self):
        """
        Verify that orchestrate_architectural_workflow calls the orchestrator
        and correctly formats the dictionary report into a readable markdown summary.
        """
        mock_report = {
            "query": "caching and eviction",
            "status": "success",
            "steps_executed": ["workspace_ast_scan", "target_search", "stack_composition"],
            "workspace_ast": {
                "primary_language": "Python",
                "languages_detected": ["Python"],
                "frameworks_detected": ["FastAPI"],
                "dependencies": ["fastapi", "pydantic"]
            },
            "matched_repositories": [
                {
                    "title": "psf/requests",
                    "source": "GitHub",
                    "description": "Python HTTP for Humans."
                }
            ],
            "solution_stack_blueprint": "Custom Stack: FastAPI + CacheGraphene",
            "repo_health": {
                "scorecard": "Vitality Score: 95 / 100",
                "analysis": {}
            }
        }

        with patch("server.orchestrator.orchestrate_workflow", return_value=mock_report):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(
                orchestrate_architectural_workflow(query="caching and eviction")
            )
            self.assertIn("Unified Orchestrated Analysis Report", res)
            self.assertIn("FastAPI", res)
            self.assertIn("psf/requests", res)
            self.assertIn("Custom Stack: FastAPI + CacheGraphene", res)

    def test_workflow_orchestrator_module_success(self):
        """
        Test the underlying WorkflowOrchestrator class logic.
        Mocks individual analyzer/search steps to verify integration flows correctly.
        """
        from orchestrator import WorkflowOrchestrator
        orchestrator_instance = WorkflowOrchestrator()

        # Mock subcomponents to avoid HTTP hits or DB reads
        with patch.object(orchestrator_instance.search_engine, "search_target", return_value=[{"title": "psf/requests", "source": "GitHub"}]), \
             patch.object(orchestrator_instance.search_engine, "compose_solution_stack", return_value="Blueprint Stack"), \
             patch("orchestrator.analyze_workspace", return_value={"primary_language": "Python", "languages_detected": ["Python"], "frameworks_detected": [], "dependencies": []}), \
             patch("orchestrator.analyze_repo_health", return_value={"health_score": 90, "metrics": {"repo": "psf/requests"}}), \
             patch.object(orchestrator_instance.repo_profiler, "get_repo_health", return_value="Scorecard"), \
             patch("orchestrator.run_lockin_profiler", return_value={"repo": "psf/requests", "portability_grade": "A"}), \
             patch("orchestrator.run_bug_profiler", return_value={"repo": "psf/requests", "total_analyzed_issues": 5}), \
             patch.object(orchestrator_instance.workspace_analyzer, "verify_workspace_fit", return_value="Fit Scorecard"), \
             patch.object(orchestrator_instance.workspace_analyzer, "align_system_architecture", return_value="Alignment Report"):

            res = orchestrator_instance.orchestrate_workflow(
                query="caching",
                workspace_path=".",
                target_hardware=None
            )
            self.assertEqual(res["status"], "success")
            self.assertIn("workspace_ast_scan", res["steps_executed"])
            self.assertIn("target_search", res["steps_executed"])
            self.assertIn("repo_health_check", res["steps_executed"])
            self.assertEqual(res["workspace_ast"]["primary_language"], "Python")

    def test_forecast_live_costs(self):
        """Test the live cost forecaster tool."""
        from server import forecast_live_costs
        loop = asyncio.get_event_loop()
        
        # Test Vercel
        res = loop.run_until_complete(forecast_live_costs(provider="Vercel", estimated_traffic=50000))
        self.assertEqual(res["provider"], "Vercel")
        self.assertTrue(res["free_tier_covered"])
        self.assertEqual(res["total_cost"], 0.0)
        
        # Test Vercel Paid
        res_paid = loop.run_until_complete(forecast_live_costs(provider="Vercel", estimated_traffic=10_000_000))
        self.assertEqual(res_paid["price_scaling_tier"], "Pro Tier")
        self.assertGreater(res_paid["total_cost"], 0.0)

    def test_auto_heal_parameters(self):
        """Test the autonomous schema auto-healer tool."""
        from server import auto_heal_parameters
        loop = asyncio.get_event_loop()
        
        raw_args = {
            "max_results": "5",          # Should be coerced to integer
            "enable_cache": "true",       # Should be coerced to boolean
            "mode": "targt"               # Should correct typo to "target"
        }
        schema = {
            "max_results": {"type": int, "default": 10},
            "enable_cache": {"type": bool, "default": False},
            "mode": {"type": str, "choices": ["target", "discovery"], "default": "target"}
        }
        
        res = loop.run_until_complete(auto_heal_parameters(raw_args, schema))
        healed = res["healed_arguments"]
        audit = res["self_correction_audit_log"]
        
        self.assertEqual(healed["max_results"], 5)
        self.assertEqual(healed["enable_cache"], True)
        self.assertEqual(healed["mode"], "target")
        self.assertIn("max_results", audit)
        self.assertIn("mode", audit)

    def test_verify_identity_token(self):
        """Test the enterprise identity sandbox tool."""
        from server import verify_identity_token
        from analyzers.identity_sandbox import generate_mock_jwt_token
        loop = asyncio.get_event_loop()
        
        # Generate token
        token = generate_mock_jwt_token(user_id="dev-agent-99", roles=["architect"], permissions=["write_files"])
        
        # Verify valid token
        res = loop.run_until_complete(verify_identity_token(token, "write_files"))
        self.assertEqual(res["status"], "authenticated")
        self.assertTrue(res["authorized"])
        self.assertEqual(res["user_id"], "dev-agent-99")
        
        # Verify missing permission
        res_denied = loop.run_until_complete(verify_identity_token(token, "admin_all"))
        self.assertEqual(res_denied["status"], "unauthorized")
        self.assertFalse(res_denied["authorized"])

    def test_profile_dependency_injection(self):
        """Test the dependency injection profiler tool."""
        from server import profile_dependency_injection
        loop = asyncio.get_event_loop()
        
        res = loop.run_until_complete(profile_dependency_injection(workspace_path="."))
        self.assertIn("workspace_path", res)
        self.assertIn("di_score", res)
        self.assertIn("di_grade", res)
        self.assertIn("scanned_files", res)

    def test_generate_docker_scaffolding(self):
        """Test the works anywhere synthesizer tool."""
        from server import generate_docker_scaffolding
        import tempfile
        loop = asyncio.get_event_loop()
        
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            res = loop.run_until_complete(generate_docker_scaffolding(workspace_path=temp_dir, target_framework="python"))
            self.assertEqual(res["status"], "success")
            self.assertIn("Dockerfile", res["files_created"])
            self.assertIn("docker-compose.yml", res["files_created"])
            
            # Verify files exist
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "Dockerfile")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "docker-compose.yml")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, ".env.example")))

    def test_scan_local_cves(self):
        """Test the CVE security shield tool."""
        from server import scan_local_cves
        loop = asyncio.get_event_loop()
        
        with patch("analyzers.cve_shield.fetch_osv_vulnerabilities") as mock_fetch:
            # Setup mock to return a CVE for PyPI package
            mock_fetch.return_value = [
                {
                    "id": "GHSA-xxxx-yyyy-zzzz",
                    "summary": "Mock SQL Injection vulnerability",
                    "severity": [{"type": "CVSS_V3", "score": "9.8"}]
                }
            ]
            res = loop.run_until_complete(scan_local_cves(workspace_path=".", halt_on_severity="high"))
            self.assertEqual(res["status"], "BLOCKED")
            self.assertEqual(res["highest_severity_found"], "CRITICAL")
            self.assertTrue(res["gate_triggered"])
            self.assertGreater(res["packages_scanned"], 0)

    def test_search_gitlab_repos(self):
        """Test the GitLab repository search tool."""
        from server import search_gitlab_repos
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(search_gitlab_repos(query="redis"))
        self.assertGreater(len(res), 0)
        self.assertEqual(res[0]["source"], "GitLab")
        self.assertIn("redis", res[0]["title"])

    def test_audit_hacker_news_trends(self):
        """Test the Hacker News trends tracking tool."""
        from server import audit_hacker_news_trends
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(audit_hacker_news_trends(query="caching"))
        self.assertEqual(res["query"], "caching")
        self.assertGreater(res["sentiment_score"], 0.0)
        self.assertGreater(len(res["hacker_news_citations"]), 0)

    def test_master_router_domain_routing(self):
        """Test the Master Router domain classification and execution paths."""
        from orchestrator import WorkflowOrchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Test routing decisions
        self.assertEqual(orchestrator.route_to_domain("scientific paper search"), "Domain 2")
        self.assertEqual(orchestrator.route_to_domain("streamlit UI design"), "Domain 3")
        self.assertEqual(orchestrator.route_to_domain("redis cache implementation"), "Domain 1")

        # Test Domain 2 mock execution
        res_d2 = orchestrator.orchestrate_workflow(query="quantum theory paper")
        self.assertEqual(res_d2["routed_domain"], "Domain 2")
        self.assertEqual(res_d2["status"], "success")
        self.assertIn("academic_search", res_d2["steps_executed"])
        self.assertIn("framework_extraction", res_d2["steps_executed"])
        self.assertIn("github_framework_search", res_d2["steps_executed"])
        self.assertIn("extracted_frameworks", res_d2)
        self.assertIn("github_framework_search", res_d2)

        # Test Domain 3 mock execution
        res_d3 = orchestrator.orchestrate_workflow(query="Tailwind UI dashboard")
        self.assertEqual(res_d3["routed_domain"], "Domain 3")
        self.assertEqual(res_d3["status"], "success")
        self.assertIn("ui_design_route", res_d3["steps_executed"])

if __name__ == "__main__":
    unittest.main()
