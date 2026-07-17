import os
import re
import json
import requests
from typing import Dict, Any, List, Set, Optional

def fetch_osv_vulnerabilities(package_name: str, ecosystem: str) -> List[Dict[str, Any]]:
    """
    Queries OSV.dev API for vulnerabilities in a specific package and ecosystem.
    """
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
            return response.json().get("vulns", [])
    except Exception:
        pass
    return []

def get_vuln_severity(vuln: Dict[str, Any]) -> str:
    """
    Extracts CVSS score or severity label from OSV payload and maps it to a unified tier.
    Tiers: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    """
    # 1. Check for CVSS database metrics
    for severity_item in vuln.get("severity", []):
        type_str = severity_item.get("type", "").upper()
        score_str = severity_item.get("score", "")
        if "CVSS" in type_str:
            try:
                score = float(score_str.split("/")[-1]) if "/" in score_str else float(score_str)
                if score >= 9.0:
                    return "CRITICAL"
                elif score >= 7.0:
                    return "HIGH"
                elif score >= 4.0:
                    return "MEDIUM"
                else:
                    return "LOW"
            except ValueError:
                pass
                
    # 2. Check database specific fields
    db_specific = vuln.get("database_specific", {})
    if db_specific:
        sev = db_specific.get("severity", "").upper()
        if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            return sev
            
    # 3. Default fallback
    return "MEDIUM"

def scan_workspace_security_cves(workspace_path: str, halt_on_severity: str = "high") -> Dict[str, Any]:
    """
    Scans a workspace path for dependency files, checks them on OSV.dev,
    and returns a security report detailing found CVEs and gate trigger status.
    """
    workspace = os.path.abspath(workspace_path)
    report = {
        "workspace_path": workspace,
        "packages_scanned": 0,
        "vulnerabilities_found": [],
        "highest_severity_found": "NONE",
        "gate_triggered": False,
        "halt_on_severity_threshold": halt_on_severity.upper(),
        "status": "PASS"
    }
    
    dependencies: List[Dict[str, str]] = []
    
    # 1. Parse dependencies from requirements.txt
    req_txt = os.path.join(workspace, "requirements.txt")
    if os.path.exists(req_txt):
        try:
            with open(req_txt, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip().split("#")[0]
                    if clean:
                        pkg = re.split(r'[=<>~!]', clean)[0].strip().lower()
                        if pkg:
                            dependencies.append({"name": pkg, "ecosystem": "PyPI"})
        except Exception:
            pass
            
    # 2. Parse dependencies from package.json
    pkg_json = os.path.join(workspace, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                for section in ["dependencies", "devDependencies"]:
                    if section in data and isinstance(data[section], dict):
                        for dep in data[section].keys():
                            dependencies.append({"name": dep.lower(), "ecosystem": "npm"})
        except Exception:
            pass
            
    # Deduplicate dependencies
    seen: Set[str] = set()
    unique_deps = []
    for dep in dependencies:
        key = f"{dep['name']}:{dep['ecosystem']}"
        if key not in seen:
            seen.add(key)
            unique_deps.append(dep)
            
    report["packages_scanned"] = len(unique_deps)
    
    severity_rank = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    threshold_rank = severity_rank.get(halt_on_severity.upper(), 3)  # Default halt on HIGH
    
    highest_rank = 0
    
    # 3. Query OSV.dev for each unique dependency
    for dep in unique_deps:
        vulns = fetch_osv_vulnerabilities(dep["name"], dep["ecosystem"])
        for v in vulns:
            v_id = v.get("id", "Unknown CVE")
            summary = v.get("summary", "No summary provided.")
            details = v.get("details", "")
            sev = get_vuln_severity(v)
            
            # Record vulnerability
            report["vulnerabilities_found"].append({
                "package": dep["name"],
                "ecosystem": dep["ecosystem"],
                "id": v_id,
                "severity": sev,
                "summary": summary,
                "details": details[:200] + "..." if len(details) > 200 else details
            })
            
            # Check highest severity
            rank = severity_rank.get(sev, 2)
            if rank > highest_rank:
                highest_rank = rank
                report["highest_severity_found"] = sev
                
            # Check gate execution halt
            if rank >= threshold_rank:
                report["gate_triggered"] = True
                report["status"] = "BLOCKED"
                
    return report
