"""
Ideation GOAT Workflow Orchestrator.

Aggregates workspace scanning, repository matching, health metrics,
ecosystem lock-in scanning, chronic bug profiling, edge hardware footprint checks,
and workspace alignment into a single cohesive, multi-step pipeline.
"""

import os
import logging
from typing import Dict, Any, Optional, List

from config import settings
from search_engine import CrossDomainSearchEngine
from scaffolder import ProjectScaffolder
from workspace_analyzer import WorkspaceAnalyzer
from repo_profiler import RepoProfiler

# Import modular analyzers
from analyzers.workspace_analyzer import analyze_workspace
from analyzers.health_analyzer import analyze_repo_health
from analyzers.lockin_profiler import check_ecosystem_lockin as run_lockin_profiler
from analyzers.bug_profiler import analyze_repo_bugs as run_bug_profiler

logger = logging.getLogger("IdeationGOAT.Orchestrator")

class WorkflowOrchestrator:
    """
    Orchestrates the end-to-end analytical pipeline for ideation and workspace validation.
    Runs diagnostics across local AST structures, public dependency registries,
    vulnerability databases, hardware footprint constraints, and generates structural blueprints.
    """

    def __init__(self):
        """
        Initializes the orchestrator with required client engines.
        """
        self.search_engine = CrossDomainSearchEngine()
        self.scaffolder = ProjectScaffolder()
        self.workspace_analyzer = WorkspaceAnalyzer()
        self.repo_profiler = RepoProfiler()

    def orchestrate_workflow(
        self,
        query: str,
        workspace_path: str = ".",
        target_hardware: Optional[str] = None,
        sram_limit_kb: float = 256.0,
        flash_limit_kb: float = 1024.0,
        scaffold_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the multi-step analytical workflow:
        1. Analyzes local workspace AST & dependencies.
        2. Queries the vector database/APIs for matching target repositories.
        3. Composes a multi-layered software solution stack.
        4. Profiles health and supply-chain vulnerabilities of the top match.
        5. Assesses vendor/ecosystem lock-in risks for the top match.
        6. Clusters chronic issues/bugs of the top match.
        7. Evaluates license compatibility and alignment to local design patterns.
        8. Profiles edge hardware footprints (if target hardware specified).
        9. Generates scaffolding skeletons (if scaffold directory specified).

        Args:
            query: Deep operational concept or design intent.
            workspace_path: Path to the local developer workspace.
            target_hardware: Optional name of microcontroller/edge hardware target.
            sram_limit_kb: SRAM constraints of edge board.
            flash_limit_kb: Flash constraints of edge board.
            scaffold_directory: Optional folder path to write scaffold skeleton files.

        Returns:
            A dictionary containing the detailed step-by-step diagnostic reports.
        """
        logger.info(f"Initiating orchestrated workflow sequence for query: '{query}'")
        workflow_report: Dict[str, Any] = {
            "query": query,
            "status": "partial_success",
            "steps_executed": []
        }

        # Step 1: Analyze local workspace AST
        logger.info("Executing Step 1: Workspace AST Parsing.")
        try:
            workspace_ast = analyze_workspace(workspace_path)
            workflow_report["workspace_ast"] = workspace_ast
            workflow_report["steps_executed"].append("workspace_ast_scan")
        except Exception as e:
            logger.error(f"Workspace AST analysis failed: {str(e)}")
            workflow_report["workspace_ast_error"] = str(e)

        # Step 2: Search matching repositories (Target Mode)
        logger.info("Executing Step 2: Target Repository Search.")
        top_match_repo: Optional[str] = None
        try:
            matches = self.search_engine.search_target(query)
            workflow_report["matched_repositories"] = matches
            workflow_report["steps_executed"].append("target_search")
            
            # Extract top GitHub repository name if available
            for match in matches:
                if match.get("source") == "GitHub" and "title" in match:
                    # If title contains slashes, it's likely a full name (e.g. owner/repo)
                    # otherwise it could be a mock or raw name, check if we need to prefix it
                    title = match["title"]
                    # If it's a mock repo, use it as is or resolve to a valid shape
                    top_match_repo = title
                    break
        except Exception as e:
            logger.error(f"Repository search failed: {str(e)}")
            workflow_report["search_error"] = str(e)

        # Step 3: Compose solution stack blueprint
        logger.info("Executing Step 3: Layered Solution Stack Composition.")
        try:
            solution_stack = self.search_engine.compose_solution_stack(query)
            workflow_report["solution_stack_blueprint"] = solution_stack
            workflow_report["steps_executed"].append("stack_composition")
        except Exception as e:
            logger.error(f"Solution stack composition failed: {str(e)}")
            workflow_report["solution_stack_error"] = str(e)

        # Skip repository-specific analyses if no top repository matches were found
        if not top_match_repo:
            logger.warning("No GitHub repository matched the intent; skipping repo-level telemetry tasks.")
            workflow_report["status"] = "completed_without_repo_telemetry"
            return workflow_report

        # Map mock repos or generic titles to a format suitable for the API calls
        # Real API queries require owner/repo structure. If not present, we can default
        # to a mock fallback or handle it gracefully.
        repo_for_api = top_match_repo
        if "/" not in repo_for_api:
            # Under mock situations, default to an example to avoid raw crashes
            repo_for_api = f"example/{repo_for_api.lower()}"

        # Step 4: Health & Supply Chain Telemetry Audit
        logger.info(f"Executing Step 4: Health Telemetry for {repo_for_api}.")
        try:
            # We call both the public API health analyzer and the local repo_profiler helper
            health_analysis = analyze_repo_health(repo_for_api)
            repo_health_scorecard = self.repo_profiler.get_repo_health(repo_for_api)
            workflow_report["repo_health"] = {
                "scorecard": repo_health_scorecard,
                "analysis": health_analysis
            }
            workflow_report["steps_executed"].append("repo_health_check")
        except Exception as e:
            logger.error(f"Repository health telemetry check failed: {str(e)}")
            workflow_report["repo_health_error"] = str(e)

        # Step 5: Ecosystem Lock-In Profile
        logger.info(f"Executing Step 5: Ecosystem Lock-In Scan for {repo_for_api}.")
        try:
            lockin_profile = run_lockin_profiler(repo_for_api)
            workflow_report["ecosystem_lockin"] = lockin_profile
            workflow_report["steps_executed"].append("lockin_scan")
        except Exception as e:
            logger.error(f"Ecosystem lock-in analysis failed: {str(e)}")
            workflow_report["lockin_error"] = str(e)

        # Step 6: Chronic Bug Profiler
        logger.info(f"Executing Step 6: Chronic Bug Analysis for {repo_for_api}.")
        try:
            bug_profile = run_bug_profiler(repo_for_api)
            workflow_report["bug_profile"] = bug_profile
            workflow_report["steps_executed"].append("bug_profile")
        except Exception as e:
            logger.error(f"Chronic bug analysis failed: {str(e)}")
            workflow_report["bug_profile_error"] = str(e)

        # Step 7: Workspace Compatibility & Architectural Alignment
        logger.info(f"Executing Step 7: Workspace Compatibility Scorecard & Alignment.")
        try:
            compatibility = self.workspace_analyzer.verify_workspace_fit(repo_for_api, workspace_path)
            alignment = self.workspace_analyzer.align_system_architecture(repo_for_api, workspace_path)
            workflow_report["workspace_alignment"] = {
                "compatibility_scorecard": compatibility,
                "alignment_report": alignment
            }
            workflow_report["steps_executed"].append("workspace_fit_and_alignment")
        except Exception as e:
            logger.error(f"Workspace fit/alignment check failed: {str(e)}")
            workflow_report["workspace_alignment_error"] = str(e)

        # Step 8: Edge Hardware Footprint Profiling (if requested)
        if target_hardware:
            logger.info(f"Executing Step 8: Edge Hardware Footprint Profiling on '{target_hardware}'.")
            try:
                hardware_profile = self.repo_profiler.profile_repo_hardware_footprint(
                    repo_for_api,
                    target_hardware,
                    sram_limit_kb,
                    flash_limit_kb
                )
                workflow_report["edge_hardware_profile"] = hardware_profile
                workflow_report["steps_executed"].append("hardware_footprint_profile")
            except Exception as e:
                logger.error(f"Edge hardware profiling failed: {str(e)}")
                workflow_report["hardware_profile_error"] = str(e)

        # Step 9: Write Scaffolding Skeletons (if requested)
        if scaffold_directory:
            logger.info(f"Executing Step 9: Generating Code Scaffold inside '{scaffold_directory}'.")
            try:
                # Prepare synthesis context mock/payload based on matches or user query
                synthesis_payload = {
                    "paradigm_name": f"{top_match_repo} Integration Template",
                    "structural_bridge": f"Decoupled bridge matching the user's intent to build: '{query}'.",
                    "hybrid_mechanics": f"Grafts core features of {top_match_repo} into the local workspace project ecosystem.",
                    "mathematical_grafting_formula": r"f_{integration}(x) = x \times \lambda_{architecture}",
                    "critical_tradeoffs": ["Initial wrapper overhead during database queries."]
                }
                scaffold_results = self.scaffolder.scaffold(
                    synthesis_output={"synthesis_payload": synthesis_payload},
                    project_directory=scaffold_directory
                )
                workflow_report["scaffold_generation"] = scaffold_results
                workflow_report["steps_executed"].append("scaffold_generation")
            except Exception as e:
                logger.error(f"Project scaffolding output generation failed: {str(e)}")
                workflow_report["scaffold_error"] = str(e)

        workflow_report["status"] = "success"
        logger.info("Orchestrated workflow sequence execution finalized.")
        return workflow_report
