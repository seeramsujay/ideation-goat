import os
from pathlib import Path
from typing import Optional

class Settings:
    """
    System configuration settings loaded from environment variables with safe defaults.
    """
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_data")
    CHROMADB_COLLECTION: str = os.getenv("CHROMADB_COLLECTION", "github_repos")
    ARXIV_TIMEOUT: int = int(os.getenv("ARXIV_TIMEOUT", "8"))
    ARXIV_MAX_RESULTS: int = int(os.getenv("ARXIV_MAX_RESULTS", "10"))
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Security Boundary: Restricts all scaffolding writes and workspace scans to the workspace folder
    WORKSPACE_ROOT: Path = Path(os.getenv("WORKSPACE_ROOT", str(Path(__file__).parent.resolve()))).resolve()

settings = Settings()
