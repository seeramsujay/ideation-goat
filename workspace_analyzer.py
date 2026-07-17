import os
import json
import logging
from pathlib import Path
from typing import Set
from config import settings
from github import Github, Auth

logger = logging.getLogger("IdeationGOAT.WorkspaceAnalyzer")

class WorkspaceAnalyzer:
    """
    Production-grade analyzer for local developer workspaces.
    Handles framework ecosystem detection, licensing checks, and architectural patterns scans.
    Guards against path traversal by validating input directories.
    """
    
    def _validate_workspace_path(self, path_str: str) -> Path:
        """
        Validates that the scanned path resides within the configured workspace root boundary.
        """
        target = Path(path_str).resolve()
        root = settings.WORKSPACE_ROOT.resolve()
        if not str(target).startswith(str(root)):
            raise PermissionError(
                f"Security Violation: Scanned path '{target}' is outside the allowed root '{root}'."
            )
        return target

    def verify_workspace_fit(self, repo_name: str, workspace_path: str = ".") -> str:
        """
        Verify if a target GitHub repository is a good technical and legal fit for the local workspace.
        Checks local files for language/license limits, then compares them against the target repository.
        """
        try:
            validated_path = self._validate_workspace_path(workspace_path)
        except PermissionError as pe:
            logger.error(f"Workspace validation failed: {str(pe)}")
            return f"Error: {str(pe)}"
            
        detected_languages: Set[str] = set()
        detected_licenses: Set[str] = set()
        
        # 1. Scan local workspace directory (up to depth 2)
        try:
            for root, dirs, files in os.walk(validated_path):
                # Prune common environment/node folders to keep searches high-speed
                if '.git' in dirs:
                    dirs.remove('.git')
                if 'node_modules' in dirs:
                    dirs.remove('node_modules')
                if '.venv' in dirs:
                    dirs.remove('.venv')
                if 'venv' in dirs:
                    dirs.remove('venv')
                
                # Check scanning depth
                depth = root[len(str(validated_path)):].count(os.sep)
                if depth > 2:
                    continue
                    
                for file in files:
                    file_lower = file.lower()
                    
                    # Ecosystem Detection
                    if file_lower == 'package.json':
                        detected_languages.add('JavaScript/TypeScript')
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if 'license' in data:
                                    lic = data['license']
                                    if isinstance(lic, dict) and 'type' in lic:
                                        detected_licenses.add(lic['type'])
                                    elif isinstance(lic, str):
                                        detected_licenses.add(lic)
                        except Exception:
                            pass
                    elif file_lower in ['requirements.txt', 'poetry.lock', 'pipfile', 'pyproject.toml']:
                        detected_languages.add('Python')
                    elif file_lower == 'cargo.toml':
                        detected_languages.add('Rust')
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
                    
                    # License File Detections
                    if file_lower in ['license', 'license.txt', 'license.md', 'copying', 'copying.txt']:
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read(500).lower()
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
            return f"Error scanning workspace files: {str(e)}"
            
        # Fallback if no specific language files are detected
        if not detected_languages:
            detected_languages.add('Not specified')
            
        workspace_license = 'Proprietary'
        if detected_licenses:
            workspace_license = list(detected_licenses)[0]
            
        # 2. Get target repo license and language from GitHub API
        token = settings.GITHUB_TOKEN
        g_client = Github(auth=Auth.Token(token)) if token else Github()
        
        try:
            repo = g_client.get_repo(repo_name)
            target_lang = repo.language or "Unknown"
            
            # Fetch target license spdx identifier
            target_license = "Unknown"
            try:
                license_obj = repo.license
                if license_obj:
                    target_license = license_obj.spdx_id or license_obj.key or license_obj.name or "Unknown"
            except Exception:
                pass
        except Exception as e:
            return f"Error fetching GitHub repository metadata: {str(e)}"
            
        # 3. Perform compatibility mapping checks
        lang_match = False
        for wl in detected_languages:
            if wl.lower() == 'not specified':
                lang_match = True
                break
            if wl.lower() in target_lang.lower() or target_lang.lower() in wl.lower():
                lang_match = True
            elif 'javascript' in wl.lower() or 'typescript' in wl.lower():
                if 'javascript' in target_lang.lower() or 'typescript' in target_lang.lower():
                    lang_match = True
                    
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
            
        # 4. Generate scorecard report
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

    def align_system_architecture(self, repo_name: str, workspace_path: str = ".") -> str:
        """
        Analyze local directories, detect structural patterns, and compile design recommendations.
        """
        try:
            validated_path = self._validate_workspace_path(workspace_path)
        except PermissionError as pe:
            logger.error(f"Workspace validation failed: {str(pe)}")
            return f"Error: {str(pe)}"
            
        dirs_found = set()
        try:
            for root, dirs, files in os.walk(validated_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                if 'node_modules' in dirs:
                    dirs.remove('node_modules')
                if '.venv' in dirs:
                    dirs.remove('.venv')
                    
                depth = root[len(str(validated_path)):].count(os.sep)
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
