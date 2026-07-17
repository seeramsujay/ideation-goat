import os
import json
import re
from typing import Dict, Any, List, Set

FRAMEWORK_SIGNATURES = {
    # Python
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "streamlit": "Streamlit",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "langchain": "LangChain",
    "chromadb": "ChromaDB",
    # JS / TS
    "express": "Express",
    "fastify": "Fastify",
    "@nestjs/core": "NestJS",
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "svelte": "Svelte",
    "tailwindcss": "Tailwind CSS",
    # Rust
    "actix-web": "Actix-Web",
    "axum": "Axum",
    "tokio": "Tokio",
    "rocket": "Rocket",
    # Go
    "github.com/gin-gonic/gin": "Gin",
    "github.com/gofiber/fiber": "Fiber",
    "github.com/labstack/echo": "Echo",
}

def analyze_workspace(workspace_path: str = None) -> Dict[str, Any]:
    """
    Read-only AST and dependency analysis of a local workspace folder.
    Extracts languages, frameworks, packages, and runtime tools currently used in the project.
    """
    if not workspace_path:
        workspace_path = os.getcwd()

    if not os.path.exists(workspace_path) or not os.path.isdir(workspace_path):
        return {
            "path": str(workspace_path),
            "primary_language": "Unknown",
            "languages_detected": [],
            "frameworks_detected": [],
            "dependencies": [],
            "build_tools": [],
            "error": f"Path '{workspace_path}' does not exist or is not a directory."
        }

    languages: Set[str] = set()
    frameworks: Set[str] = set()
    dependencies: Set[str] = set()
    build_tools: Set[str] = set()

    # 1. Inspect dependency manifests
    pkg_json_path = os.path.join(workspace_path, "package.json")
    if os.path.exists(pkg_json_path):
        build_tools.add("npm/pnpm")
        languages.add("JavaScript")
        if os.path.exists(os.path.join(workspace_path, "tsconfig.json")):
            languages.add("TypeScript")
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for section in ["dependencies", "devDependencies"]:
                    if section in data and isinstance(data[section], dict):
                        for dep in data[section].keys():
                            dependencies.add(dep)
                            if dep in FRAMEWORK_SIGNATURES:
                                frameworks.add(FRAMEWORK_SIGNATURES[dep])
        except Exception:
            pass

    req_txt_path = os.path.join(workspace_path, "requirements.txt")
    if os.path.exists(req_txt_path):
        build_tools.add("pip")
        languages.add("Python")
        try:
            with open(req_txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip().split("#")[0]
                    if clean:
                        pkg = re.split(r'[=<>~!]', clean)[0].strip().lower()
                        if pkg:
                            dependencies.add(pkg)
                            if pkg in FRAMEWORK_SIGNATURES:
                                frameworks.add(FRAMEWORK_SIGNATURES[pkg])
        except Exception:
            pass

    pyproject_path = os.path.join(workspace_path, "pyproject.toml")
    if os.path.exists(pyproject_path):
        build_tools.add("poetry/pip")
        languages.add("Python")
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                for key, name in FRAMEWORK_SIGNATURES.items():
                    if re.search(r'["\']' + re.escape(key) + r'["\']', content, re.IGNORECASE):
                        frameworks.add(name)
                        dependencies.add(key)
        except Exception:
            pass

    cargo_path = os.path.join(workspace_path, "Cargo.toml")
    if os.path.exists(cargo_path):
        build_tools.add("cargo")
        languages.add("Rust")
        try:
            with open(cargo_path, "r", encoding="utf-8") as f:
                content = f.read()
                for key, name in FRAMEWORK_SIGNATURES.items():
                    if re.search(re.escape(key) + r'\s*=', content):
                        frameworks.add(name)
                        dependencies.add(key)
        except Exception:
            pass

    go_mod_path = os.path.join(workspace_path, "go.mod")
    if os.path.exists(go_mod_path):
        build_tools.add("go")
        languages.add("Go")
        try:
            with open(go_mod_path, "r", encoding="utf-8") as f:
                content = f.read()
                for key, name in FRAMEWORK_SIGNATURES.items():
                    if key in content:
                        frameworks.add(name)
                        dependencies.add(key.split("/")[-1])
        except Exception:
            pass

    # 2. AST-lite source code scan (check top source files for imports)
    files_checked = 0
    for root, dirs, files in os.walk(workspace_path):
        # Exclude node_modules, venv, .git, chroma_data
        dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", ".venv", ".git", "__pycache__", "chroma_data", "dist", "build"]]
        if files_checked >= 30:
            dirs[:] = []
            break
        for file in files:
            if files_checked >= 30:
                break
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".ts", ".js", ".jsx", ".tsx", ".go", ".rs"]:
                files_checked += 1
                if ext == ".py":
                    languages.add("Python")
                elif ext in [".ts", ".tsx"]:
                    languages.add("TypeScript")
                elif ext in [".js", ".jsx"]:
                    languages.add("JavaScript")
                elif ext == ".go":
                    languages.add("Go")
                elif ext == ".rs":
                    languages.add("Rust")

                try:
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read(4096) # read first 4KB
                        for key, name in FRAMEWORK_SIGNATURES.items():
                            if name not in frameworks:
                                if ext == ".py" and re.search(r'^\s*(?:import|from)\s+' + re.escape(key), code, re.MULTILINE):
                                    frameworks.add(name)
                                elif ext in [".ts", ".js", ".tsx", ".jsx"] and re.search(r'(?:import|require)\s*\(?["\'].*?' + re.escape(key) + r'.*?["\']\)?', code):
                                    frameworks.add(name)
                except Exception:
                    pass

    # Determine primary language
    primary_language = "Unknown"
    if "Python" in languages:
        primary_language = "Python"
    elif "TypeScript" in languages:
        primary_language = "TypeScript"
    elif "JavaScript" in languages:
        primary_language = "JavaScript"
    elif "Rust" in languages:
        primary_language = "Rust"
    elif "Go" in languages:
        primary_language = "Go"
    elif languages:
        primary_language = list(languages)[0]

    return {
        "path": os.path.abspath(workspace_path),
        "primary_language": primary_language,
        "languages_detected": sorted(list(languages)),
        "frameworks_detected": sorted(list(frameworks)),
        "dependencies": sorted(list(dependencies)),
        "build_tools": sorted(list(build_tools))
    }
