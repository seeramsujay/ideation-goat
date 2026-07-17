import os
import json
import logging
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from config import settings
from github import Github, Auth

logger = logging.getLogger("IdeationGOAT.RepoProfiler")

class RepoProfiler:
    """
    Production-grade telemetry and resource profiler for GitHub repositories.
    Queries GitHub API, OSV.dev, and estimates RAM/Flash footprint for edge architectures.
    """

    def get_repo_health(self, repo_name: str) -> str:
        """
        Fetch real-time health, activity telemetry, and security vulnerabilities for a target repository.
        Queries the GitHub API and the OSV.dev vulnerability database.
        """
        token = settings.GITHUB_TOKEN
        g_client = Github(auth=Auth.Token(token)) if token else Github()
        
        try:
            repo = g_client.get_repo(repo_name)
            stars = repo.stargazers_count
            forks = repo.forks_count
            open_issues = repo.open_issues_count
            created_at = repo.created_at
            pushed_at = repo.pushed_at
            size = repo.size
            language = repo.language or "Unknown"
            description = repo.description or ""
        except Exception as e:
            return f"Error fetching GitHub repository data for '{repo_name}': {str(e)}"
            
        # Commit activity (last 30 days)
        since_date = datetime.now(timezone.utc) - timedelta(days=30)
        commits_count = 0
        try:
            commits = repo.get_commits(since=since_date)
            for _ in commits:
                commits_count += 1
                if commits_count >= 100:
                    break
        except Exception:
            commits_count = -1
            
        # PR activity
        open_prs = 0
        closed_prs = 0
        try:
            pulls = repo.get_pulls(state='all', sort='updated')
            count_checked = 0
            for pr in pulls:
                if count_checked >= 30:
                    break
                count_checked += 1
                if pr.updated_at >= since_date:
                    if pr.state == 'closed':
                        closed_prs += 1
                    else:
                        open_prs += 1
        except Exception:
            pass
            
        # OSV.dev Vulnerabilities lookup
        latest_sha = None
        vulnerabilities = []
        try:
            latest_sha = repo.get_commits()[0].sha
        except Exception:
            pass
            
        if latest_sha:
            try:
                osv_url = "https://api.osv.dev/v1/query"
                post_data = json.dumps({"commit": latest_sha}).encode("utf-8")
                req = urllib.request.Request(
                    osv_url,
                    data=post_data,
                    headers={"Content-Type": "application/json", "User-Agent": "IdeationGOAT/1.2.0"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    if "vulns" in res_data:
                        for vuln in res_data["vulns"]:
                            vuln_id = vuln.get("id", "Unknown ID")
                            summary = vuln.get("summary", "No summary provided")
                            details = vuln.get("details", "")
                            short_details = details[:120] + "..." if len(details) > 120 else details
                            vulnerabilities.append(f"- **{vuln_id}**: {summary} ({short_details})")
            except Exception as e:
                vulnerabilities.append(f"*(Could not query OSV database: {str(e)})*")
                
        # Vitality score logic (0-100)
        last_push_days = (datetime.now(timezone.utc) - pushed_at).days
        
        # Recency score (max 40)
        if last_push_days <= 7:
            recency_score = 40
        elif last_push_days <= 30:
            recency_score = 30
        elif last_push_days <= 90:
            recency_score = 20
        elif last_push_days <= 180:
            recency_score = 10
        else:
            recency_score = 0
            
        # Frequency score (max 30)
        if commits_count >= 20:
            freq_score = 30
        elif commits_count >= 10:
            freq_score = 25
        elif commits_count >= 5:
            freq_score = 20
        elif commits_count >= 1:
            freq_score = 10
        else:
            freq_score = 0
            
        # Community score (max 30)
        issue_ratio = open_issues / (stars + 1)
        if issue_ratio < 0.02:
            ratio_score = 15
        elif issue_ratio < 0.05:
            ratio_score = 10
        else:
            ratio_score = 5
            
        if closed_prs >= 5:
            pr_score = 15
        elif closed_prs >= 1:
            pr_score = 10
        else:
            pr_score = 5
            
        community_score = ratio_score + pr_score
        vitality_score = recency_score + freq_score + community_score
        
        # Format markdown report
        output = []
        output.append(f"## 🩺 Pulse & Health Telemetry for `{repo_name}`")
        output.append(f"*{description}*")
        output.append("")
        output.append(f"### **Vitality Score**: `{vitality_score}/100`")
        
        filled_bars = int(vitality_score / 10)
        bar_str = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
        output.append(f"{bar_str}")
        output.append("")
        
        output.append("### 📊 Metrics")
        output.append(f"- ⭐ **Stars:** {stars:,}")
        output.append(f"- 🍴 **Forks:** {forks:,}")
        output.append(f"- 🐛 **Open Issues:** {open_issues:,}")
        output.append(f"- 📅 **Created At:** {created_at.strftime('%Y-%m-%d')}")
        output.append(f"- 🚀 **Last Pushed:** {pushed_at.strftime('%Y-%m-%d')} ({last_push_days} days ago)")
        if commits_count >= 0:
            output.append(f"- 📈 **Commits (last 30 days):** {commits_count}")
        else:
            output.append("- 📈 **Commits (last 30 days):** *Failed to fetch*")
        output.append(f"- 🤝 **PR Activity (last 30 days):** {open_prs} Open, {closed_prs} Closed")
        output.append(f"- 💾 **Codebase Size:** {size / 1024:.2f} MB")
        
        output.append("")
        output.append("### 🛡️ Security Vulnerabilities (OSV.dev)")
        if vulnerabilities:
            real_vulns = [v for v in vulnerabilities if not v.startswith("*")]
            if real_vulns:
                output.append(f"⚠️ **Vulnerabilities Found:** The latest commit `{latest_sha[:8] if latest_sha else ''}` matches known vulnerabilities in the OSV database:")
                for v in vulnerabilities:
                    output.append(v)
            else:
                output.append("⚠️ **Network / Details:**")
                for v in vulnerabilities:
                    output.append(v)
        else:
            output.append("✅ No known vulnerabilities found for the latest commit SHA in the OSV database.")
            
        output.append("")
        output.append("### 💡 Verdict")
        if vitality_score >= 80 and not vulnerabilities:
            output.append("🌟 **Excellent:** This repository is highly active, well-maintained, and has no critical vulnerabilities. It is safe for production use.")
        elif vitality_score >= 50:
            output.append("⚠️ **Healthy with Caution:** The repository is moderately active. Ensure the maintenance rate aligns with your project lifecycle.")
        else:
            output.append("❌ **High Risk:** The repository is either abandoned or has extremely low maintenance activity. Consider finding alternatives to avoid technical debt.")
            
        return "\n".join(output)

    def profile_repo_hardware_footprint(
        self,
        repo_name: str,
        target_hardware: str,
        sram_limit_kb: float = 256.0,
        flash_limit_kb: float = 1024.0
    ) -> str:
        """
        Profile the structural and resource footprint of a target repository against edge hardware limits.
        """
        token = settings.GITHUB_TOKEN
        g_client = Github(auth=Auth.Token(token)) if token else Github()
        
        try:
            repo = g_client.get_repo(repo_name)
            root_contents = repo.get_contents("")
            file_names = [f.name.lower() for f in root_contents]
        except Exception as e:
            return f"Error connecting to GitHub repository '{repo_name}': {str(e)}"
            
        mcu_lang = "C/C++"
        has_cargo = "cargo.toml" in file_names
        has_package = "package.json" in file_names
        has_requirements = "requirements.txt" in file_names
        has_cmakelists = "cmakelists.txt" in file_names or "makefile" in file_names
        
        est_sram = 0.0
        est_flash = 0.0
        warnings = []
        
        if has_cargo:
            mcu_lang = "Rust"
            try:
                cargo_file = repo.get_contents("Cargo.toml")
                cargo_content = cargo_file.decoded_content.decode("utf-8").lower()
                if "no_std" in cargo_content or "alloc" in cargo_content:
                    est_sram = 15.0
                    est_flash = 45.0
                    warnings.append("✅ Rust crate appears to support `no_std`. Suitable for bare-metal.")
                else:
                    est_sram = 512.0
                    est_flash = 1024.0
                    warnings.append("⚠️ Rust crate does not explicitly declare `no_std`. Standard library `std` may exceed SRAM limits on thin microcontrollers.")
            except Exception:
                est_sram = 128.0
                est_flash = 256.0
                warnings.append("⚠️ Failed to parse Cargo.toml. Assuming standard Rust std footprint.")
                
        elif has_requirements:
            mcu_lang = "MicroPython / Python"
            est_sram = 120.0
            est_flash = 512.0
            warnings.append("⚠️ Python code detected. Will require MicroPython/CircuitPython interpreter on the microcontroller.")
            warnings.append("⚠️ Python code is dynamically allocated and could cause high heap/SRAM consumption and fragmentation.")
            
        elif has_package:
            mcu_lang = "JavaScript / JerryScript"
            est_sram = 180.0
            est_flash = 600.0
            warnings.append("⚠️ JavaScript code detected. Requires QuickJS or JerryScript engine, which have high overhead on Cortex-M boards.")
            
        elif has_cmakelists or any(f.endswith('.h') or f.endswith('.c') or f.endswith('.cpp') for f in file_names):
            mcu_lang = "C/C++"
            uses_stl = False
            try:
                h_files = [f for f in root_contents if f.name.endswith('.h') or f.name.endswith('.hpp')]
                if h_files:
                    sample_file = repo.get_contents(h_files[0].path)
                    sample_content = sample_file.decoded_content.decode("utf-8")
                    if "std::" in sample_content or "vector" in sample_content or "string" in sample_content:
                        uses_stl = True
            except Exception:
                pass
                
            if uses_stl:
                est_sram = 64.0
                est_flash = 200.0
                warnings.append("⚠️ C++ library uses standard template library (STL) headers (vector/string), which cause heap usage and binary bloat.")
            else:
                est_sram = 20.0
                est_flash = 80.0
                warnings.append("✅ Bare-metal C/C++ codebase with low overhead. Highly compatible with small microcontrollers.")
                
        else:
            mcu_lang = repo.language or "C/C++"
            est_sram = 50.0
            est_flash = 150.0
            warnings.append("⚠️ Unknown framework structure. Footprint estimated based on language.")
            
        if repo.size > 10000:
            est_flash += 300.0
            est_sram += 50.0
            warnings.append(f"⚠️ Large repository size ({repo.size / 1024:.1f}MB). Binary footprint may expand depending on compiled features.")
            
        sram_ok = est_sram <= sram_limit_kb
        flash_ok = est_flash <= flash_limit_kb
        
        score = 100
        if not sram_ok:
            score -= 50
        if not flash_ok:
            score -= 30
            
        output = []
        output.append(f"## 🎛️ Edge-Deploy Footprint Profile for `{repo_name}`")
        output.append(f"**Target Microcontroller/Hardware:** `{target_hardware}`")
        output.append(f"**Core Language Ecosystem:** `{mcu_lang}`")
        output.append("")
        output.append("| Resource Metric | Estimated Footprint | Specified Hardware Limit | Match Status |")
        output.append("| --- | --- | --- | --- |")
        output.append(f"| **SRAM / RAM** | {est_sram:.1f} KB | {sram_limit_kb:.1f} KB | {'✅ Fits' if sram_ok else '❌ Exceeded'} |")
        output.append(f"| **Flash Storage** | {est_flash:.1f} KB | {flash_limit_kb:.1f} KB | {'✅ Fits' if flash_ok else '❌ Exceeded'} |")
        output.append("")
        output.append(f"### **Hardware Fit Score**: `{score}/100`")
        output.append("")
        output.append("### 🔍 Static Analysis Findings:")
        for w in warnings:
            output.append(w)
            
        output.append("")
        output.append("### 💡 Deployment Recommendation:")
        if score == 100:
            output.append(f"🟢 **Deployable:** `{repo_name}` is extremely lightweight and will easily fit on the `{target_hardware}`. Go ahead with integration.")
        elif score >= 50:
            output.append(f"🟡 **Optimizations Required:** You can run this codebase on `{target_hardware}`, but you must optimize memory layouts, compile with optimization flags (e.g. `-Os`), and disable unnecessary library modules.")
        else:
            output.append(f"🔴 **Incompatible / High Risk:** This library is too heavy for the `{target_hardware}` spec. SRAM or Flash requirements will lead to build errors or runtime out-of-memory crashes. Consider a C/Rust bare-metal alternative.")
            
        return "\n".join(output)
