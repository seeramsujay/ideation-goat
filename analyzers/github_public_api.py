import os
import time
import requests
from functools import lru_cache
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Simple TTL / LRU Cache wrapper for GitHub API queries to prevent rate limit exhaustion
_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache duration

def get_github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "NitroForge-Semantic-Matcher"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def make_github_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """
    Make a GET request to GitHub API v3 with caching and rate-limit safety.
    Endpoint format: '/repos/{owner}/{repo}/...' or full URL 'https://api.github.com/...'
    """
    if not endpoint.startswith("http"):
        url = f"https://api.github.com{endpoint if endpoint.startswith('/') else '/' + endpoint}"
    else:
        url = endpoint

    # Create cache key based on URL and sorted params
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
    cache_key = f"{url}?{param_str}"

    now = time.time()
    if cache_key in _CACHE:
        entry = _CACHE[cache_key]
        if now - entry["timestamp"] < CACHE_TTL_SECONDS:
            return entry["data"]

    headers = get_github_headers()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Check rate limit specifically
        if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
            remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            if remaining == 0:
                print(f"[WARN] GitHub API rate limit reached for {url}")
                # Return stale cache if available when rate limited
                if cache_key in _CACHE:
                    return _CACHE[cache_key]["data"]
                return None

        if response.status_code == 200:
            data = response.json()
            _CACHE[cache_key] = {"timestamp": now, "data": data}
            return data
        elif response.status_code == 404:
            # Not found
            _CACHE[cache_key] = {"timestamp": now, "data": None}
            return None
        else:
            print(f"[DEBUG] GitHub API returned {response.status_code} for {url}")
            return None
    except Exception as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        # Return stale cache if available
        if cache_key in _CACHE:
            return _CACHE[cache_key]["data"]
        return None

def parse_owner_repo(repo_full_name_or_url: str) -> Optional[str]:
    """
    Extract 'owner/repo' from 'https://github.com/owner/repo' or return 'owner/repo' directly.
    """
    if not repo_full_name_or_url:
        return None
    clean = repo_full_name_or_url.strip().rstrip("/")
    if "github.com/" in clean:
        parts = clean.split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    elif "/" in clean and not clean.startswith("http"):
        parts = clean.split("/")
        if len(parts) == 2:
            return f"{parts[0]}/{parts[1]}"
    return None
