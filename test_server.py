import os
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Dict, Any

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
    analyze_repo_bugs as server_analyze_repo_bugs
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
        server.LAST_SEARCH = {
            "query": "",
            "mode": "",
            "matches": []
        }
        # Mock Scholar and Patent clients to avoid real network hits during existing tests
        from unittest.mock import MagicMock
        server.search_engine.scholar_client.search = MagicMock(return_value=[])
        server.search_engine.patent_client.search = MagicMock(return_value=[])

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
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": [{
                "title": "Quantum Caching in Neurobiology",
                "abstract": "A study of quantum cache effects.",
                "url": "https://example.com/quantum",
                "paperId": "12345",
                "citationCount": 42
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        from scholar_client import ScholarClient
        client = ScholarClient()
        papers = client.search("quantum cache")
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["title"], "Quantum Caching in Neurobiology")
        self.assertEqual(papers[0]["citations"], 42)

    @patch('urllib.request.urlopen')
    def test_patent_client_search(self, mock_urlopen):
        from unittest.mock import MagicMock
        import json
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "patents": [{
                "patent_number": "9999999",
                "patent_title": "Cache Eviction Composite Systems",
                "patent_abstract": "A method to evict items.",
                "patent_date": "2026-01-01"
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        from patent_client import PatentClient
        client = PatentClient()
        patents = client.search("cache eviction")

        self.assertEqual(len(patents), 1)
        self.assertEqual(patents[0]["patent_number"], "9999999")
        self.assertEqual(patents[0]["title"], "Cache Eviction Composite Systems")

    @patch('urllib.request.urlopen')
    def test_search_academic_papers_tool(self, mock_urlopen):
        # We need to restore the mock for scholar search in this test case
        from unittest.mock import MagicMock
        import json
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": [{
                "title": "Quantum Caching in Neurobiology",
                "abstract": "A study of quantum cache effects.",
                "url": "https://example.com/quantum",
                "paperId": "12345",
                "citationCount": 42
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

if __name__ == "__main__":
    unittest.main()
