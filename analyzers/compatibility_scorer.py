from typing import Dict, Any, List

# Common framework conflict pairs and migration hints
FRAMEWORK_CONFLICTS = [
    ("Express", "Fastify", "Your workspace is using Express, while this target repository is built around Fastify.", "You can use 'fastify-express' plugin adapter to run Express middleware inside Fastify without rewriting routes."),
    ("Fastify", "Express", "Your workspace uses Fastify, while this target repository is designed for Express.", "Wrap Express handlers inside a standard Node.js request listener or migrate routing middleware."),
    ("Flask", "FastAPI", "Your workspace uses Flask (WSGI synchronous), while this target relies on FastAPI (ASGI asynchronous).", "Use 'a2wsgi' or 'WSGIMiddleware' from 'starlette.middleware.wsgi' to mount your existing Flask app inside FastAPI."),
    ("FastAPI", "Flask", "Your workspace uses async FastAPI, while this target repository is structured for Flask.", "Consider keeping FastAPI as primary and calling Flask routes via WSGI adapter if necessary."),
    ("React", "Vue", "Your workspace uses React, whereas this repository/UI toolkit targets Vue.js.", "Look for the React equivalent wrapper of this library or use Web Components / Micro-frontend bridges."),
    ("Vue", "React", "Your workspace uses Vue.js, whereas this repository targets React.", "Use 'veaury' or a Vue-to-React component wrapper if embedding is required."),
]

def score_compatibility(workspace_profile: Dict[str, Any], target_repo_name: str, target_repo_lang: str, matched_context: str = "") -> Dict[str, Any]:
    """
    Cross-reference local workspace AST profile against target repository metadata.
    Returns compatibility score (0-100), level, identified conflicts, and actionable migration snippets/hints.
    """
    if not workspace_profile or workspace_profile.get("primary_language") == "Unknown" or not target_repo_lang:
        return {
            "score": 85,
            "level": "Unverified / Generic",
            "color": "#A0AEC0",
            "conflicts": [],
            "migration_hints": ["No specific workspace AST loaded or unknown target language. Standard installation recommended."],
            "summary": "Workspace profile unverified. Proceed with standard package installation."
        }

    user_lang = workspace_profile.get("primary_language", "Unknown")
    user_langs = set(workspace_profile.get("languages_detected", []))
    user_frameworks = set(workspace_profile.get("frameworks_detected", []))
    user_deps = set(workspace_profile.get("dependencies", []))

    score = 100
    conflicts = []
    hints = []

    # Check if target repo is already in dependencies
    target_clean = target_repo_name.split("/")[-1].lower() if "/" in target_repo_name else target_repo_name.lower()
    if target_clean in user_deps or any(target_clean in f.lower() for f in user_frameworks):
        return {
            "score": 100,
            "level": "Exact Fit (Already Installed)",
            "color": "#48BB78",  # Green
            "conflicts": [],
            "migration_hints": [f"`{target_clean}` is already listed in your workspace dependencies!"],
            "summary": f"Exact Fit: Your local workspace (`{workspace_profile['path']}`) already includes or supports this framework."
        }

    # Language Compatibility check
    lang_compatible = False
    if user_lang.lower() == target_repo_lang.lower():
        lang_compatible = True
    elif user_lang in ["JavaScript", "TypeScript"] and target_repo_lang in ["JavaScript", "TypeScript"]:
        lang_compatible = True
    elif target_repo_lang in user_langs:
        lang_compatible = True

    if not lang_compatible and target_repo_lang != "Unknown" and target_repo_lang != "All":
        score -= 40
        conflicts.append(f"Language Mismatch: Your local project is primarily written in **{user_lang}**, whereas `{target_repo_name}` is a **{target_repo_lang}** repository.")
        hints.append(f"Check if `{target_repo_name}` offers a client SDK / REST API or can be run as a standalone Docker microservice alongside your {user_lang} application.")

    # Framework Conflict check
    for user_fw, target_fw, conflict_msg, hint_msg in FRAMEWORK_CONFLICTS:
        if user_fw in user_frameworks:
            # Check if target repo name or matched context mentions the target framework strongly
            if target_fw.lower() in target_clean or (matched_context and target_fw.lower() in matched_context.lower() and user_fw.lower() not in matched_context.lower()):
                score -= 25
                conflicts.append(conflict_msg)
                hints.append(hint_msg)
                break

    score = max(0, min(100, int(score)))

    if score >= 85:
        level = "Exact Fit"
        color = "#48BB78"  # Green
        if not hints:
            hints.append(f"Direct integration: Install via your workspace package manager (`{' '.join(workspace_profile.get('build_tools', ['pip/npm']))}`).")
    elif score >= 55:
        level = "Adapter Needed"
        color = "#ECC94B"  # Yellow
    else:
        level = "Stack Mismatch"
        color = "#E53E3E"  # Red

    if not conflicts:
        summary = f"Good compatibility ({score}% score). Compatible with your {user_lang} stack."
    else:
        summary = f"Compatibility score {score}% ({level}). Identified {len(conflicts)} architectural consideration(s)."

    return {
        "score": score,
        "level": level,
        "color": color,
        "conflicts": conflicts,
        "migration_hints": hints,
        "summary": summary
    }
