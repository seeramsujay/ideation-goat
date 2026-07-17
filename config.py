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
    
    # Cloud Vector DB & LLM Configurations
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_URL: Optional[str] = os.getenv("PINECONE_INDEX_URL")
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_SCHOLAR_API_KEY: Optional[str] = os.getenv("GOOGLE_SCHOLAR_API_KEY")
    GOOGLE_PATENTS_API_KEY: Optional[str] = os.getenv("GOOGLE_PATENTS_API_KEY")
    
    # Security Boundary: Restricts all scaffolding writes and workspace scans to the workspace folder
    WORKSPACE_ROOT: Path = Path(os.getenv("WORKSPACE_ROOT", str(Path(__file__).parent.resolve()))).resolve()

settings = Settings()

