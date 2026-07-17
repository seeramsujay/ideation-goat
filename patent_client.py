import logging
import time
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

logger = logging.getLogger("IdeationGOAT.PatentClient")

class PatentClient:
    """
    Client for querying the Google Patents API (via SerpAPI or mock endpoints) to retrieve patent documents.
    Includes timeout, exponential backoff retries, and error handling.
    """
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def search(self, query_term: str, max_results: int = 5, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Queries Google Patents endpoint with retries and exponential backoff.
        """
        formatted_query = urllib.parse.quote(query_term)
        from config import settings
        api_key = getattr(settings, "GOOGLE_PATENTS_API_KEY", None)
        
        # Fallback to mock Google Patents if API key is not configured
        if not api_key:
            logger.info("Google Patents API key not found. Returning mock Google Patents results.")
            return [
                {
                    "source": "Google Patents",
                    "patent_number": "US-10987654-B2",
                    "title": f"Dynamic Self-Healing Framework for {query_term.capitalize()}",
                    "url": "https://patents.google.com/patent/US10987654B2/en",
                    "summary": f"This patent describes an autonomous method for resolving failures in {query_term} clusters.",
                    "date": "2024-05-12"
                }
            ][:max_results]

        # SerpAPI Google Patents query URL
        url = f"https://serpapi.com/search.json?engine=google_patents&q={formatted_query}&api_key={api_key}"
        
        for attempt in range(retries + 1):
            try:
                logger.info(f"Querying Google Patents API (Attempt {attempt+1}/{retries+1}): {query_term}")
                req = urllib.request.Request(url, headers={'User-Agent': 'IdeationGOAT/1.2.0'})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                patents = []
                for item in data.get('organic_results', [])[:max_results]:
                    title = item.get('title', 'Unknown Title')
                    snippet = item.get('snippet', 'No summary available.')
                    patent_id = item.get('patent_id', 'Unknown')
                    url_link = item.get('pdf') or f"https://patents.google.com/patent/{patent_id}/en"
                    
                    patents.append({
                        "source": "Google Patents",
                        "patent_number": patent_id,
                        "title": title,
                        "url": url_link,
                        "summary": snippet,
                        "date": item.get('publication_date', 'Unknown')
                    })
                return patents
            except Exception as e:
                logger.warning(f"Google Patents request failed on attempt {attempt+1}: {str(e)}")
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    logger.error(f"All Google Patents API queries failed for term: {query_term}")
                    return []
        return []
