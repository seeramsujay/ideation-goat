import logging
import time
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

logger = logging.getLogger("IdeationGOAT.PatentClient")

class PatentClient:
    """
    Client for querying the Google Patents API via SerpApi to retrieve patent documents.
    Includes timeout, exponential backoff retries, and error handling.
    """
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def search(self, query_term: str, max_results: int = 5, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Queries SerpApi Google Patents endpoint with retries and exponential backoff.
        """
        from config import settings
        google_patents_api_key = getattr(settings, "GOOGLE_PATENTS_API_KEY", None)
        
        # Fallback to mock results if API key is not configured
        if not google_patents_api_key:
            logger.info("GOOGLE_PATENTS_API_KEY not found. Returning mock patent results.")
            return self._get_mock_results(query_term, max_results)

        patents = []

        # Prepare parameters for SerpApi
        params = {
            "engine": "google_patents",
            "q": query_term,
            "api_key": google_patents_api_key,
            "num": max_results
        }
        query_string = urllib.parse.urlencode(params)
        url = f"https://serpapi.com/search?{query_string}"

        for attempt in range(retries + 1):
            try:
                logger.info(f"Querying SerpApi Google Patents API (Attempt {attempt+1}/{retries+1}): {query_term}")
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'IdeationGOAT/1.2.0'
                    }
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                
                # Check for error in response
                error_msg = response_data.get("search_metadata", {}).get("error")
                if error_msg:
                    raise RuntimeError(f"SerpApi Error: {error_msg}")

                organic_results = response_data.get("organic_results", [])
                for item in organic_results:
                    pat_id = item.get('patent_id') or 'Unknown'
                    # Strip 'patent/' prefix if present
                    if pat_id.startswith('patent/'):
                        parts = pat_id.split('/')
                        if len(parts) > 1:
                            pat_id = parts[1]
                    
                    patents.append({
                        "source": "Google Patents",
                        "patent_number": item.get('publication_number') or pat_id,
                        "title": item.get('title', 'Unknown Title'),
                        "url": item.get('patent_link') or f"https://patents.google.com/patent/{item.get('patent_id', '')}",
                        "summary": item.get('snippet', 'No summary available.'),
                        "date": item.get('publication_date', 'Unknown')
                    })
                
                if patents:
                    return patents[:max_results]
                
                logger.info("No organic patent results found.")
                return self._get_mock_results(query_term, max_results)

            except Exception as e:
                logger.warning(f"Patent query attempt {attempt+1} failed: {str(e)}")
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    logger.error(f"All patent API queries failed for term: {query_term}")
                    break
        
        # Fallback to graceful unavailable message on failure
        return self._get_mock_results(query_term, max_results)

    def _get_mock_results(self, query_term: str, max_results: int) -> List[Dict[str, Any]]:
        return [
            {
                "source": "Google Patents",
                "patent_number": "N/A",
                "title": "Patents not available",
                "url": "#",
                "summary": "Patent documents are currently not available.",
                "date": "N/A"
            }
        ]
