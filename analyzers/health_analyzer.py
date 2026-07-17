from datetime import datetime, timezone
import requests
from typing import Dict, Any, List, Optional
from analyzers.github_public_api import make_github_request, parse_owner_repo

def query_osv_vulnerabilities(package_name: str, language: str) -> List[Dict[str, Any]]:
    """
    Query OSV.dev public API for known vulnerabilities for a given package and language ecosystem.
    """
    ecosystem_map = {
        "python": "PyPI",
        "javascript": "npm",
        "typescript": "npm",
        "rust": "crates.io",
        "go": "Go"
    }
    ecosystem = ecosystem_map.get(language.lower())
    if not ecosystem:
        return []

    url = "https://api.osv.dev/v1/query"
    payload = {
        "package": {
            "name": package_name.lower(),
            "ecosystem": ecosystem
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("vulns", [])
    except Exception as e:
        print(f"[DEBUG] OSV query failed for {package_name}: {e}")
    return []

def analyze_repo_health(repo_name_or_url: str) -> Dict[str, Any]:
    """
    Analyze the health and tech debt risk of a GitHub repository.
    Returns composite score, health status (Healthy / Caution / High Risk), metrics, and warning flags.
    """
    owner_repo = parse_owner_repo(repo_name_or_url)
    if not owner_repo:
        return {
            "health_score": 0,
            "status": "High Risk",
            "flags": ["INVALID_REPO: Could not parse repository identifier."],
            "metrics": {}
        }

    # Fetch basic repo metadata
    repo_data = make_github_request(f"/repos/{owner_repo}")
    if not repo_data:
        return {
            "health_score": 50,
            "status": "Caution",
            "flags": ["UNVERIFIED: Could not fetch GitHub repository metadata."],
            "metrics": {"repo": owner_repo}
        }

    archived = repo_data.get("archived", False)
    language = repo_data.get("language") or "Unknown"
    stars = repo_data.get("stargazers_count", 0)
    pushed_at_str = repo_data.get("pushed_at")
    
    # Check contributors count
    contributors = make_github_request(f"/repos/{owner_repo}/contributors", params={"per_page": 10})
    contributors_count = len(contributors) if isinstance(contributors, list) else 1

    # Check recent commit / push date
    months_inactive = 0
    last_commit_date = "Unknown"
    if pushed_at_str:
        try:
            # GitHub format: 2024-05-15T12:34:56Z
            pushed_dt = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_inactive = (now - pushed_dt).days
            months_inactive = days_inactive / 30.44
            last_commit_date = pushed_dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # Query OSV for known vulnerabilities (using repo name or second part of owner/repo)
    package_name = owner_repo.split("/")[-1]
    vulns = query_osv_vulnerabilities(package_name, language)
    cve_count = len(vulns)

    # Calculate composite health score (0 to 100)
    score = 100
    flags = []

    if archived:
        score = 0
        flags.append("ABANDONED: Repository is officially archived by its maintainers.")
    else:
        # Penalize inactivity
        if months_inactive > 18:
            score -= 40
            flags.append(f"STALE: No updates in over 18 months (Last commit: {last_commit_date}).")
        elif months_inactive > 12:
            score -= 25
            flags.append(f"STALE: No updates in over a year (Last commit: {last_commit_date}).")
        elif months_inactive > 6:
            score -= 10
            flags.append(f"INACTIVE: No updates in {int(months_inactive)} months.")

        # Penalize low bus factor / contributor count
        if contributors_count <= 1:
            score -= 15
            flags.append("BUS_FACTOR_RISK: Maintained by a single contributor.")
        elif contributors_count <= 2:
            score -= 5

        # Penalize CVEs
        if cve_count > 0:
            penalty = min(cve_count * 20, 60)
            score -= penalty
            flags.append(f"CVE_CRITICAL: Found {cve_count} known security vulnerability report(s) on OSV.dev.")

    score = max(0, min(100, int(score)))

    # Determine status level
    if score >= 80:
        status = "Healthy"
    elif score >= 50:
        status = "Caution"
    else:
        status = "High Risk"

    return {
        "health_score": score,
        "status": status,
        "flags": flags,
        "metrics": {
            "repo": owner_repo,
            "stars": stars,
            "cve_count": cve_count,
            "last_commit_date": last_commit_date,
            "contributors_count": contributors_count,
            "archived": archived,
            "language": language
        }
    }
