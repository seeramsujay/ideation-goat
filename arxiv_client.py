import logging
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from config import settings

logger = logging.getLogger("IdeationGOAT.ArXivClient")

class ArXivClient:
    """
    Production-grade client for querying the arXiv API.
    Includes timeouts, exponential backoff retries, and robust XML parsing.
    """
    
    def __init__(self, timeout: int = settings.ARXIV_TIMEOUT):
        self.timeout = timeout
        self.ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

    def search(self, query_term: str, max_results: int = settings.ARXIV_MAX_RESULTS, retries: int = 2) -> List[Dict[str, Any]]:
        """
        Executes a keyword search on the arXiv API with retries and exponential backoff.
        """
        formatted_query = urllib.parse.quote(query_term)
        url = f"http://export.arxiv.org/api/query?search_query=all:{formatted_query}&max_results={max_results}"
        
        for attempt in range(retries + 1):
            try:
                logger.info(f"Querying arXiv API (Attempt {attempt+1}/{retries+1}): {query_term}")
                req = urllib.request.Request(url, headers={'User-Agent': 'IdeationGOAT/1.2.0'})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    xml_data = response.read()
                return self._parse_xml(xml_data)
            except Exception as e:
                logger.warning(f"arXiv request failed on attempt {attempt+1}: {str(e)}")
                if attempt < retries:
                    sleep_time = 1.5 * (attempt + 1)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All arXiv API query attempts failed for term: {query_term}")
                    return []
        return []

    def _parse_xml(self, xml_data: bytes) -> List[Dict[str, Any]]:
        """
        Parses the Atom XML returned by arXiv.
        """
        try:
            root = ET.fromstring(xml_data)
            papers = []
            for entry in root.findall('atom:entry', self.ns):
                title_elem = entry.find('atom:title', self.ns)
                summary_elem = entry.find('atom:summary', self.ns)
                id_elem = entry.find('atom:id', self.ns)
                primary_cat_elem = entry.find('arxiv:primary_category', self.ns)
                
                title = title_elem.text.strip() if title_elem is not None else "Unknown Title"
                summary = summary_elem.text.strip() if summary_elem is not None else "No abstract available."
                summary = " ".join(summary.split())
                paper_id = id_elem.text.strip() if id_elem is not None else "#"
                
                category = ""
                if primary_cat_elem is not None:
                    category = primary_cat_elem.get('term', '')
                else:
                    cat_elem = entry.find('atom:category', self.ns)
                    if cat_elem is not None:
                        category = cat_elem.get('term', '')
                
                papers.append({
                    "source": "arXiv",
                    "title": title,
                    "url": paper_id,
                    "summary": summary,
                    "category": category
                })
            return papers
        except ET.ParseError as pe:
            logger.error(f"Failed to parse XML response from arXiv: {str(pe)}")
            return []
