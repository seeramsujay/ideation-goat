import logging
import time
import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

logger = logging.getLogger("IdeationGOAT.ScholarClient")

class ScholarClient:
    """
    Client for querying the Semantic Scholar API and Unpaywall API to retrieve academic research papers.
    Includes timeout, exponential backoff retries, and error handling.
    """
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def search(self, query_term: str, max_results: int = 5, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Queries Semantic Scholar search endpoint and enriches open-access PDF links using Unpaywall.
        """
        formatted_query = urllib.parse.quote(query_term)
        from config import settings
        unpaywall_email = getattr(settings, "UNPAYWALL_EMAIL", None) or "support@ideationgoat.org"

        # Base URL for Semantic Scholar Paper Search
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={formatted_query}&limit={max_results}&fields=title,abstract,authors,externalIds,openAccessPdf,citationCount"
        
        headers = {'User-Agent': 'IdeationGOAT/1.2.0'}

        for attempt in range(retries + 1):
            try:
                logger.info(f"Querying Semantic Scholar API (Attempt {attempt+1}/{retries+1}): {query_term}")
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                papers = []
                for item in data.get('data', [])[:max_results]:
                    title = item.get('title', 'Unknown Title')
                    abstract = item.get('abstract') or 'No abstract available.'
                    citation_count = item.get('citationCount', 0)
                    paper_id = item.get('paperId')
                    
                    # Default URL is Semantic Scholar landing page
                    url_link = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
                    
                    external_ids = item.get('externalIds', {})
                    doi = external_ids.get('DOI')
                    
                    pdf_url = None
                    is_open_access = False
                    
                    # 1. Query Unpaywall if DOI is present
                    if doi:
                        unpaywall_url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={urllib.parse.quote(unpaywall_email)}"
                        try:
                            logger.info(f"Querying Unpaywall API for DOI {doi}")
                            req_up = urllib.request.Request(unpaywall_url, headers={'User-Agent': 'IdeationGOAT/1.2.0'})
                            with urllib.request.urlopen(req_up, timeout=self.timeout) as res_up:
                                up_data = json.loads(res_up.read().decode('utf-8'))
                            is_open_access = up_data.get('is_oa', False)
                            if is_open_access:
                                best_loc = up_data.get('best_oa_location') or {}
                                pdf_url = best_loc.get('url_for_pdf')
                        except Exception as e:
                            logger.warning(f"Unpaywall lookup failed for DOI {doi}: {str(e)}")
                    
                    # 2. Fallback to Semantic Scholar openAccessPdf if Unpaywall failed/didn't find a PDF
                    if not pdf_url:
                        oa_pdf = item.get('openAccessPdf') or {}
                        pdf_url = oa_pdf.get('url')
                        if pdf_url:
                            is_open_access = True
                            
                    # If we found an open access PDF, use it as the main URL, otherwise keep the landing page
                    final_url = pdf_url if pdf_url else url_link
                    
                    papers.append({
                        "source": "Semantic Scholar",
                        "title": title,
                        "url": final_url,
                        "summary": abstract,
                        "citations": citation_count,
                        "doi": doi,
                        "is_open_access": is_open_access,
                        "pdf_url": pdf_url
                    })
                return papers
            except Exception as e:
                logger.warning(f"Semantic Scholar request failed on attempt {attempt+1}: {str(e)}")
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    logger.error(f"All Semantic Scholar API queries failed for term: {query_term}")
                    break

        # Fallback to graceful non-mock unavailable message on failure
        logger.info("Returning graceful unavailable status for Semantic Scholar.")
        return [
            {
                "source": "Semantic Scholar",
                "title": "Scholars not available",
                "url": "#",
                "summary": "Academic paper metadata and open-access PDFs are currently not available.",
                "citations": 0,
                "doi": None,
                "is_open_access": False,
                "pdf_url": None
            }
        ]
