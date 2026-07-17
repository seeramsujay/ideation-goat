import base64
import json
import re
from typing import Dict, Any, List, Tuple
from analyzers.github_public_api import make_github_request, parse_owner_repo

VENDOR_PATTERNS = [
    (r'^@aws-sdk/.*|^aws-sdk$|^boto3$|^botocore$|^aws-cdk.*|^aws-amplify$|^serverless$', "Amazon Web Services (AWS)", "Direct AWS SDK or serverless cloud adapter."),
    (r'^@vercel/.*|^vercel$|^@edge-runtime/.*', "Vercel Cloud", "Vercel-specific cloud edge or hosting SDK."),
    (r'^@google-cloud/.*|^google-cloud-.*|^firebase$|^firebase-admin$', "Google Cloud Platform / Firebase", "GCP or Firebase proprietary backend adapter."),
    (r'^@azure/.*|^azure-.*', "Microsoft Azure", "Direct Azure cloud SDK or function adapter."),
    (r'^wrangler$|^@cloudflare/.*', "Cloudflare Workers", "Cloudflare Edge/Worker specific runtime dependency."),
    (r'^@supabase/.*|^supabase$', "Supabase Cloud", "Supabase proprietary BaaS client SDK (Self-hostable with effort)."),
]

def _fetch_file_content(owner_repo: str, filepath: str) -> str:
    # Try fetching via API first
    data = make_github_request(f"/repos/{owner_repo}/contents/{filepath}")
    if data and isinstance(data, dict) and "content" in data:
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        except Exception:
            pass
    return ""

def _parse_dependencies(owner_repo: str) -> List[str]:
    deps = set()

    # Check package.json
    pkg_json_content = _fetch_file_content(owner_repo, "package.json")
    if pkg_json_content:
        try:
            parsed = json.loads(pkg_json_content)
            for section in ["dependencies", "peerDependencies", "optionalDependencies"]:
                if section in parsed and isinstance(parsed[section], dict):
                    deps.update(parsed[section].keys())
        except Exception:
            pass

    # Check requirements.txt
    req_txt_content = _fetch_file_content(owner_repo, "requirements.txt")
    if req_txt_content:
        for line in req_txt_content.splitlines():
            clean = line.strip().split("#")[0]
            if clean:
                pkg = re.split(r'[=<>~!]', clean)[0].strip()
                if pkg:
                    deps.add(pkg)

    # Check pyproject.toml
    pyproject_content = _fetch_file_content(owner_repo, "pyproject.toml")
    if pyproject_content:
        # Simple regex extraction of dependency names inside dependencies = [...]
        matches = re.findall(r'["\']([a-zA-Z0-9_-]+)(?:[=<>~!].*?)?["\']', pyproject_content)
        for m in matches:
            if m not in ["python", "poetry", "setuptools", "wheel"]:
                deps.add(m)

    return list(deps)

def check_ecosystem_lockin(repo_name_or_url: str) -> Dict[str, Any]:
    """
    Analyze a repository's dependency tree and files to detect proprietary ecosystem lock-in.
    Returns portability grade (A through F) and detailed warning breakdown.
    """
    owner_repo = parse_owner_repo(repo_name_or_url)
    if not owner_repo:
        return {
            "portability_grade": "Unknown",
            "grade_color": "#A0AEC0",
            "locked_dependencies": [],
            "summary": "Could not parse repository identifier."
        }

    dependencies = _parse_dependencies(owner_repo)
    locked_deps = []

    for dep in dependencies:
        for pattern, vendor, reason in VENDOR_PATTERNS:
            if re.match(pattern, dep, re.IGNORECASE):
                locked_deps.append({
                    "package": dep,
                    "vendor": vendor,
                    "reason": reason
                })
                break

    # Determine Grade
    count = len(locked_deps)
    if count == 0:
        grade = "A"
        color = "#48BB78"  # Green
        summary = "This framework earns a Grade A for portability. It imports no proprietary cloud or serverless adapters, meaning it can run on any Linux, Docker, or self-hosted environment."
    elif count == 1:
        grade = "B"
        color = "#ECC94B"  # Yellow
        summary = f"This framework earns a Grade B for portability. It includes 1 cloud adapter ({locked_deps[0]['package']} for {locked_deps[0]['vendor']}), which is minor and usually replaceable."
    elif count <= 3:
        grade = "C"
        color = "#ED8936"  # Orange
        vendors = ", ".join(set(d["vendor"] for d in locked_deps))
        summary = f"This framework earns a Grade C for portability. It heavily imports proprietary cloud SDKs ({vendors}), meaning migrating to a self-hosted environment later will require architectural refactoring."
    else:
        grade = "D"
        color = "#E53E3E"  # Red
        vendors = ", ".join(set(d["vendor"] for d in locked_deps))
        summary = f"This framework earns a Grade D for portability. It has extensive proprietary cloud dependencies ({count} packages tied to {vendors}). It is deeply locked into this specific cloud ecosystem."

    return {
        "repo": owner_repo,
        "portability_grade": grade,
        "grade_color": color,
        "total_dependencies_checked": len(dependencies),
        "locked_dependencies": locked_deps,
        "summary": summary
    }
