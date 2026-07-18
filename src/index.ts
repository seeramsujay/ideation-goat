import { ToolDecorator as Tool, z, ExecutionContext, McpApp, Module } from '@nitrostack/core';
import { spawn } from 'child_process';
import * as path from 'path';

/**
 * Executes a tool function against the underlying Python core backend engine.
 * Spawns an asynchronous Python process and retrieves the output.
 */
async function runPythonTool(toolName: string, args: Record<string, any>): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonCode = `
import asyncio
import json
import sys
import os

# Add root directory to path to locate server.py
sys.path.insert(0, os.getcwd())

from server import ${toolName}

async def main():
    try:
        args = json.loads(sys.argv[1])
        res = await ${toolName}(**args)
        print(json.dumps(res))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

asyncio.run(main())
`;
    // Spawn python3 child process
    const child = spawn('python3', ['-c', pythonCode, JSON.stringify(args)], {
      cwd: process.cwd(),
      env: process.env
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data;
    });

    child.stderr.on('data', (data) => {
      stderr += data;
    });

    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}. Stderr: ${stderr}`));
        return;
      }
      try {
        const parsed = JSON.parse(stdout.trim());
        resolve(parsed);
      } catch (err) {
        resolve(stdout.trim());
      }
    });
  });
}

export class IdeationGoatTools {
  
  @Tool({
    name: 'search_knowledge_grid',
    description: 'Advanced multi-domain index query engine. Interrogates codebases, academia, and patents.',
    inputSchema: z.object({
      query: z.string().describe('Deep operational concept or system design goal.'),
      mode: z.enum(['target', 'discovery']).default('target').describe('Search mode determining grid traversal.'),
      cognitive_distance: z.number().min(0.0).max(1.0).default(0.0).describe('Applied cognitive distance factor.')
    })
  })
  async searchKnowledgeGrid(input: { query: string; mode: 'target' | 'discovery'; cognitive_distance: number }, ctx: ExecutionContext) {
    return runPythonTool('search_knowledge_grid', input);
  }

  @Tool({
    name: 'breed_concepts',
    description: 'Synthesizes two distinct conceptual structures into a hybrid architectural blueprint.',
    inputSchema: z.object({
      concept_a: z.object({
        title: z.string(),
        description: z.string(),
        domain_context: z.string()
      }).describe('First conceptual paradigm model.'),
      concept_b: z.object({
        title: z.string(),
        description: z.string(),
        domain_context: z.string()
      }).describe('Second conceptual paradigm model to graft.')
    })
  })
  async breedConcepts(input: { concept_a: any; concept_b: any }, ctx: ExecutionContext) {
    return runPythonTool('breed_concepts', input);
  }

  @Tool({
    name: 'bridge_code_and_theory',
    description: 'Bidirectional Algorithmic Translation tool. Translates code logic into mathematical LaTeX, or latex equations into software code architectures.',
    inputSchema: z.object({
      code_snippet: z.string().optional().describe('Source code logic pattern to analyze.'),
      latex_formula: z.string().optional().describe('LaTeX formula string to map to implementations.')
    })
  })
  async bridgeCodeAndTheory(input: { code_snippet?: string; latex_formula?: string }, ctx: ExecutionContext) {
    return runPythonTool('bridge_code_and_theory', input);
  }

  @Tool({
    name: 'assess_viability',
    description: 'Evaluates a custom design concept against commercial patterns and active patent claims.',
    inputSchema: z.object({
      system_design: z.string().describe('Text describing design components and architecture layout.')
    })
  })
  async assessViability(input: { system_design: string }, ctx: ExecutionContext) {
    return runPythonTool('assess_viability', input);
  }

  @Tool({
    name: 'search_academic_papers',
    description: 'Query both arXiv and Semantic Scholar to return relevant academic research papers.',
    inputSchema: z.object({
      query: z.string().describe('Scientific concept or keyword query.'),
      max_results: z.number().int().default(5).describe('Maximum matches to return per engine.')
    })
  })
  async searchAcademicPapers(input: { query: string; max_results: number }, ctx: ExecutionContext) {
    return runPythonTool('search_academic_papers', input);
  }

  @Tool({
    name: 'write_scaffolding_files',
    description: 'Automated project bootstrapper. Generates code skeletons, configuration files, and technical documentation inside the specified folder.',
    inputSchema: z.object({
      synthesis_output: z.record(z.any()).describe('Architectural paradigm template definitions.'),
      project_directory: z.string().describe('Target workspace directory name.')
    })
  })
  async writeScaffoldingFiles(input: { synthesis_output: any; project_directory: string }, ctx: ExecutionContext) {
    return runPythonTool('write_scaffolding_files', input);
  }

  @Tool({
    name: 'verify_workspace_fit',
    description: 'Verify if a target GitHub repository is a good technical and legal fit for the local workspace.',
    inputSchema: z.object({
      repo_name: z.string().describe('Target github repo coordinates.'),
      workspace_path: z.string().default('.').describe('Workspace root folder.')
    })
  })
  async verifyWorkspaceFit(input: { repo_name: string; workspace_path: string }, ctx: ExecutionContext) {
    return runPythonTool('verify_workspace_fit', input);
  }

  @Tool({
    name: 'compose_solution_stack',
    description: 'Decompose a complex system idea into multiple architectural layers and query the database to compose a cohesive solution stack of open-source frameworks.',
    inputSchema: z.object({
      query: z.string().describe('Product requirements or architectural design ideas.'),
      n_results: z.number().int().default(3).describe('Number of top matches to find per layer.')
    })
  })
  async composeSolutionStack(input: { query: string; n_results: number }, ctx: ExecutionContext) {
    return runPythonTool('compose_solution_stack', input);
  }

  @Tool({
    name: 'get_repo_health',
    description: 'Fetch real-time health, activity telemetry, and security vulnerabilities for a target GitHub repository.',
    inputSchema: z.object({
      repo_name: z.string().describe('Target github repo name (e.g. facebook/react).')
    })
  })
  async getRepoHealth(input: { repo_name: string }, ctx: ExecutionContext) {
    return runPythonTool('get_repo_health', input);
  }

  @Tool({
    name: 'profile_repo_hardware_footprint',
    description: 'Profile the structural and resource footprint of a target repository against edge hardware limits.',
    inputSchema: z.object({
      repo_name: z.string().describe('Target edge firmware repo coordinates.'),
      target_hardware: z.string().describe('Name of edge hardware board target.'),
      sram_limit_kb: z.number().default(256.0).describe('SRAM limits of board in KB.'),
      flash_limit_kb: z.number().default(1024.0).describe('Flash storage limits of board in KB.')
    })
  })
  async profileRepoHardwareFootprint(input: { repo_name: string; target_hardware: string; sram_limit_kb: number; flash_limit_kb: number }, ctx: ExecutionContext) {
    return runPythonTool('profile_repo_hardware_footprint', input);
  }

  @Tool({
    name: 'align_system_architecture',
    description: 'Analyze the local workspace directory structure to detect its design pattern, and output a detailed architectural alignment/integration report for the target repository.',
    inputSchema: z.object({
      repo_name: z.string().describe('Proposed integration repository name.'),
      workspace_path: z.string().default('.').describe('Workspace root directory to check alignment.')
    })
  })
  async alignSystemArchitecture(input: { repo_name: string; workspace_path: string }, ctx: ExecutionContext) {
    return runPythonTool('align_system_architecture', input);
  }

  @Tool({
    name: 'analyze_workspace_ast',
    description: 'Zero-friction local workspace AST & dependency analyzer.',
    inputSchema: z.object({
      workspace_path: z.string().optional().describe('Optional path to local project workspace folder.')
    })
  })
  async analyzeWorkspaceAst(input: { workspace_path?: string }, ctx: ExecutionContext) {
    return runPythonTool('analyze_workspace_ast', input);
  }

  @Tool({
    name: 'check_repo_health',
    description: 'Automated supply-chain risk and maintenance health auditor for any GitHub repository.',
    inputSchema: z.object({
      repository: z.string().describe('Target repository name or clone URL coordinates.')
    })
  })
  async checkRepoHealth(input: { repository: string }, ctx: ExecutionContext) {
    return runPythonTool('check_repo_health', input);
  }

  @Tool({
    name: 'check_ecosystem_lockin',
    description: 'Deep dependency tree scanner that evaluates long-term cloud/ecosystem portability.',
    inputSchema: z.object({
      repository: z.string().describe('Repository coordinates to trace vendor dependencies.')
    })
  })
  async checkEcosystemLockin(input: { repository: string }, ctx: ExecutionContext) {
    return runPythonTool('check_ecosystem_lockin', input);
  }

  @Tool({
    name: 'analyze_repo_bugs',
    description: 'Semantic issue-clustering engine that surfaces chronic structural bugs and known pitfalls.',
    inputSchema: z.object({
      repository: z.string().describe('Target repository name or path to parse issues.')
    })
  })
  async analyzeRepoBugs(input: { repository: string }, ctx: ExecutionContext) {
    return runPythonTool('analyze_repo_bugs', input);
  }

  @Tool({
    name: 'orchestrate_architectural_workflow',
    description: 'Executes a multi-step analytical workflow.',
    inputSchema: z.object({
      query: z.string().describe('Design paradigm or intent description.'),
      workspace_path: z.string().default('.').describe('Root folder of local project.'),
      target_hardware: z.string().optional().describe('Microcontroller board target configuration.'),
      sram_limit_kb: z.number().default(256.0).describe('SRAM limitations in KB.'),
      flash_limit_kb: z.number().default(1024.0).describe('Flash limits in KB.'),
      scaffold_directory: z.string().optional().describe('Workspace subdirectory to write scaffold files.')
    })
  })
  async orchestrateArchitecturalWorkflow(
    input: { query: string; workspace_path: string; target_hardware?: string; sram_limit_kb: number; flash_limit_kb: number; scaffold_directory?: string },
    ctx: ExecutionContext
  ) {
    return runPythonTool('orchestrate_architectural_workflow', input);
  }

  @Tool({
    name: 'forecast_live_costs',
    description: 'Live Cost Forecaster Tool. Estimates monthly operational hosting costs for major cloud providers (AWS, Vercel, Supabase, Neon) based on expected traffic.',
    inputSchema: z.object({
      provider: z.enum(['AWS', 'Vercel', 'Supabase', 'Neon']).describe('Cloud hosting provider name.'),
      estimated_traffic: z.number().int().describe('Estimated monthly request volume.')
    })
  })
  async forecastLiveCosts(input: { provider: 'AWS' | 'Vercel' | 'Supabase' | 'Neon'; estimated_traffic: number }, ctx: ExecutionContext) {
    return runPythonTool('forecast_live_costs', input);
  }

  @Tool({
    name: 'auto_heal_parameters',
    description: 'Autonomous Schema Auto-Healer Tool. Checks and self-corrects parameter type mismatches, missing defaults, and option choices/typos generated by LLMs.',
    inputSchema: z.object({
      raw_arguments: z.record(z.any()).describe('The malformed parameters dictionary.'),
      expected_schema: z.record(z.any()).describe('The expected target schema properties.')
    })
  })
  async autoHealParameters(input: { raw_arguments: any; expected_schema: any }, ctx: ExecutionContext) {
    return runPythonTool('auto_heal_parameters', input);
  }

  @Tool({
    name: 'verify_identity_token',
    description: 'Enterprise Identity Sandbox Tool. Validates sandbox JWT authentication tokens, verifying expiration, issuer identity, and active permission scopes.',
    inputSchema: z.object({
      token: z.string().describe('Signed JWT auth token string.'),
      required_permission: z.string().optional().describe('Optional permission scope required.')
    })
  })
  async verifyIdentityToken(input: { token: string; required_permission?: string }, ctx: ExecutionContext) {
    return runPythonTool('verify_identity_token', input);
  }

  @Tool({
    name: 'profile_dependency_injection',
    description: 'Dependency Injection Profiler Tool. Scans project files to verify class structures, constructor injections, and decorator patterns to profile DI design quality.',
    inputSchema: z.object({
      workspace_path: z.string().default('.').describe('Local project workspace path to analyze.')
    })
  })
  async profileDependencyInjection(input: { workspace_path: string }, ctx: ExecutionContext) {
    return runPythonTool('profile_dependency_injection', input);
  }

  @Tool({
    name: 'generate_docker_scaffolding',
    description: "The 'Works Anywhere' Synthesizer Tool. Generates custom Dockerfile, docker-compose.yml, and .env.example configurations tailored to a language or framework.",
    inputSchema: z.object({
      workspace_path: z.string().describe('Folder where container configurations will be written.'),
      target_framework: z.string().default('python').describe('Target language/framework.')
    })
  })
  async generateDockerScaffolding(input: { workspace_path: string; target_framework: string }, ctx: ExecutionContext) {
    return runPythonTool('generate_docker_scaffolding', input);
  }

  @Tool({
    name: 'scan_local_cves',
    description: 'CVE Security Shield Tool. Scans workspace dependency manifests, queries OSV.dev database for vulnerabilities, and enforces severity-based execution gates.',
    inputSchema: z.object({
      workspace_path: z.string().default('.').describe('Workspace root folder to scan dependency manifests.'),
      halt_on_severity: z.enum(['low', 'medium', 'high', 'critical']).default('high').describe('Gate severity limit.')
    })
  })
  async scanLocalCves(input: { workspace_path: string; halt_on_severity: 'low' | 'medium' | 'high' | 'critical' }, ctx: ExecutionContext) {
    return runPythonTool('scan_local_cves', input);
  }

  @Tool({
    name: 'search_gitlab_repos',
    description: 'Search GitLab projects registry for matching repositories.',
    inputSchema: z.object({
      query: z.string().describe('Search term or keyword to scan GitLab repositories.')
    })
  })
  async searchGitlabRepos(input: { query: string }, ctx: ExecutionContext) {
    return runPythonTool('search_gitlab_repos', input);
  }

  @Tool({
    name: 'audit_hacker_news_trends',
    description: 'Scan Hacker News titles and comments for developer sentiment and mention trends.',
    inputSchema: z.object({
      query: z.string().describe('Keyword or technology term to audit on Hacker News.')
    })
  })
  async auditHackerNewsTrends(input: { query: string }, ctx: ExecutionContext) {
    return runPythonTool('audit_hacker_news_trends', input);
  }
}

// Module configuration
@Module({
  name: 'IdeationGoatModule',
  controllers: [IdeationGoatTools]
})
export class IdeationGoatModule {}

// App bootstrapping
@McpApp({
  module: IdeationGoatModule,
  server: {
    name: 'IdeationGOAT',
    version: '1.0.0'
  }
})
export class IdeationGoatServer {}
