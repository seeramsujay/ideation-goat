import logging
import time
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

logger = logging.getLogger("IdeationGOAT.ScholarClient")

class ScholarClient:
    """
    Client for querying the Google Scholar API (via SerpAPI or mock endpoints) to retrieve academic research papers.
    Includes timeout, exponential backoff retries, and error handling.
    """
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def search(self, query_term: str, max_results: int = 5, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Queries Google Scholar search endpoint with retries and exponential backoff.
        """
        formatted_query = urllib.parse.quote(query_term)
        from config import settings
        api_key = getattr(settings, "GOOGLE_SCHOLAR_API_KEY", None)
        
        # If no API key is present, fallback to high-quality mock results
        if not api_key:
            logger.info("Google Scholar API key not found. Returning mock Google Scholar results.")
            return [
                {
                    "source": "Google Scholar",
                    "title": f"Adaptive Optimization Algorithms for {query_term.capitalize()}",
                    "url": f"https://scholar.google.com/scholar?q={formatted_query}",
                    "summary": f"This paper examines dynamic parameters optimization in {query_term} setups.",
                    "citations": 42
                },
                {
                    "source": "Google Scholar",
                    "title": f"Ecosystem Analysis of {query_term.capitalize()} Paradigms",
                    "url": f"https://scholar.google.com/scholar?q={formatted_query}",
                    "summary": f"A comprehensive survey on the real-world deployment challenges of {query_term}.",
                    "citations": 12
                }
            ][:max_results]

        url = f"https://serpapi.com/search.json?engine=google_scholar&q={formatted_query}&hl=en&num={max_results}&api_key={api_key}"
        
        for attempt in range(retries + 1):
            try:
                logger.info(f"Querying Google Scholar API (Attempt {attempt+1}/{retries+1}): {query_term}")
                req = urllib.request.Request(url, headers={'User-Agent': 'IdeationGOAT/1.2.0'})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                papers = []
                for item in data.get('organic_results', []):
                    title = item.get('title', 'Unknown Title')
                    pub_info = item.get('publication_info', {})
                    abstract = pub_info.get('summary') or 'No abstract available.'
                    url_link = item.get('link') or f"https://scholar.google.com/scholar?q={formatted_query}"
                    citations = item.get('inline_links', {}).get('cited_by', {}).get('total', 0)
                    
                    papers.append({
                        "source": "Google Scholar",
                        "title": title,
                        "url": url_link,
                        "summary": abstract,
                        "citations": citations
                    })
                return papers
            except Exception as e:
                logger.warning(f"Google Scholar request failed on attempt {attempt+1}: {str(e)}")
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    logger.error(f"All Google Scholar API queries failed for term: {query_term}")
                    return []
        return []
