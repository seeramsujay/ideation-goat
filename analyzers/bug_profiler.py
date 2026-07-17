import re
from collections import Counter
from typing import Dict, Any, List
from analyzers.github_public_api import make_github_request, parse_owner_repo

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Common stop words to filter out when extracting labels
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "from",
    "up", "about", "into", "over", "after", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "not", "no", "can", "could", "should", "would",
    "will", "just", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "than", "that", "this", "these", "those", "it", "its",
    "of", "error", "bug", "issue", "fails", "failed", "when", "using", "use", "doesnt", "work",
    "not", "working"
}

HIGH_SEVERITY_KEYWORDS = {
    "crash", "crashes", "crashing", "leak", "memory", "deadlock", "drop", "dropped", "drops",
    "disconnect", "security", "vulnerability", "fatal", "panic", "corrupt", "corruption",
    "freeze", "freezes", "unresponsive", "oom", "segfault"
}

def _clean_title(title: str) -> List[str]:
    # Remove code blocks, brackets, tags like [Bug], (v2.0)
    cleaned = re.sub(r'\[.*?\]|\(.*?\)', ' ', title.lower())
    words = re.findall(r'[a-z0-9_-]+', cleaned)
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS and not w.isdigit()]

def _fallback_keyword_clustering(titles: List[str]) -> List[Dict[str, Any]]:
    """
    Fallback keyword/n-gram clustering when scikit-learn is not available or very few issues exist.
    """
    total = len(titles)
    if total == 0:
        return []

    # Count meaningful keyword occurrences
    keyword_map = Counter()
    title_words_list = []
    for t in titles:
        words = _clean_title(t)
        title_words_list.append((t, words))
        for w in set(words):
            keyword_map[w] += 1

    # Find top 3 dominant keywords/themes
    top_keywords = [k for k, _ in keyword_map.most_common(5)]
    clusters = []
    used_indices = set()

    for kw in top_keywords:
        matching_titles = []
        for idx, (original_title, words) in enumerate(title_words_list):
            if idx not in used_indices and kw in words:
                matching_titles.append(original_title)
                used_indices.add(idx)

        if matching_titles:
            pct = round((len(matching_titles) / total) * 100, 1)
            # Find a second co-occurring word for a better label
            co_words = Counter()
            for t in matching_titles:
                for w in _clean_title(t):
                    if w != kw:
                        co_words[w] += 1
            second_word = f" / {co_words.most_common(1)[0][0]}" if co_words else ""
            label = f"{kw.capitalize()}{second_word} issues"

            is_critical = any(h in kw or h in label.lower() for h in HIGH_SEVERITY_KEYWORDS) or pct >= 20.0

            clusters.append({
                "label": label,
                "percentage": pct,
                "count": len(matching_titles),
                "example_issues": matching_titles[:2],
                "is_critical": is_critical
            })

        if len(clusters) >= 3:
            break

    return sorted(clusters, key=lambda x: x["percentage"], reverse=True)

def _sklearn_kmeans_clustering(titles: List[str], n_clusters: int = 3) -> List[Dict[str, Any]]:
    """
    TF-IDF Vectorization and K-Means clustering of issue titles.
    """
    total = len(titles)
    if total < n_clusters:
        return _fallback_keyword_clustering(titles)

    try:
        vectorizer = TfidfVectorizer(max_features=100, stop_words=list(STOP_WORDS))
        X = vectorizer.fit_transform(titles)
        
        # If vocabulary is too small, fallback
        if X.shape[1] < 3:
            return _fallback_keyword_clustering(titles)

        kmeans = KMeans(n_clusters=min(n_clusters, total), random_state=42, n_init=5)
        labels = kmeans.fit_predict(X)

        terms = vectorizer.get_feature_names_out()
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

        clusters = []
        for i in range(min(n_clusters, total)):
            cluster_indices = [idx for idx, label in enumerate(labels) if label == i]
            count = len(cluster_indices)
            if count == 0:
                continue

            pct = round((count / total) * 100, 1)
            # Get top 2 terms for label
            top_terms = [terms[ind] for ind in order_centroids[i, :2]]
            label_name = " + ".join(w.capitalize() for w in top_terms) + " problems"
            examples = [titles[idx] for idx in cluster_indices[:2]]
            
            is_critical = any(h in label_name.lower() for h in HIGH_SEVERITY_KEYWORDS) or pct >= 20.0

            clusters.append({
                "label": label_name,
                "percentage": pct,
                "count": count,
                "example_issues": examples,
                "is_critical": is_critical
            })

        return sorted(clusters, key=lambda x: x["percentage"], reverse=True)
    except Exception as e:
        print(f"[DEBUG] Sklearn clustering error ({e}), falling back to keyword clustering.")
        return _fallback_keyword_clustering(titles)

def analyze_repo_bugs(repo_name_or_url: str) -> Dict[str, Any]:
    """
    Fetch recent bug reports and run clustering analysis to identify chronic pain points.
    """
    owner_repo = parse_owner_repo(repo_name_or_url)
    if not owner_repo:
        return {
            "total_analyzed_issues": 0,
            "top_pitfalls": [],
            "risk_level": "Unknown",
            "error": "Could not parse repository identifier."
        }

    # Fetch issues with label 'bug' first
    issues = make_github_request(f"/repos/{owner_repo}/issues", params={"state": "all", "labels": "bug", "per_page": 80})
    
    # If few bug-labeled issues, fetch general open/closed issues
    if not issues or len(issues) < 10:
        general_issues = make_github_request(f"/repos/{owner_repo}/issues", params={"state": "open", "per_page": 80})
        if general_issues and isinstance(general_issues, list):
            issues = (issues or []) + general_issues

    if not issues or not isinstance(issues, list) or len(issues) == 0:
        return {
            "total_analyzed_issues": 0,
            "top_pitfalls": [],
            "risk_level": "Low",
            "message": "No recent issues found."
        }

    # Filter out pull requests (GitHub API returns PRs inside issues endpoint)
    clean_issues = [i for i in issues if "pull_request" not in i]
    titles = [i.get("title", "") for i in clean_issues if i.get("title")]

    if len(titles) == 0:
        return {
            "total_analyzed_issues": 0,
            "top_pitfalls": [],
            "risk_level": "Low",
            "message": "No valid issue titles analyzed."
        }

    if HAS_SKLEARN and len(titles) >= 5:
        pitfalls = _sklearn_kmeans_clustering(titles, n_clusters=3)
    else:
        pitfalls = _fallback_keyword_clustering(titles)

    # Determine overall bug risk level
    risk_level = "Low"
    if any(p["is_critical"] and p["percentage"] >= 20.0 for p in pitfalls):
        risk_level = "High"
    elif any(p["percentage"] >= 15.0 for p in pitfalls):
        risk_level = "Moderate"

    return {
        "repo": owner_repo,
        "total_analyzed_issues": len(titles),
        "top_pitfalls": pitfalls,
        "risk_level": risk_level
    }
