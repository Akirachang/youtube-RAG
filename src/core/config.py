"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # YouTube API
    youtube_api_key: str = Field(..., description="YouTube Data API v3 key")

    # OpenAI
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")

    # Anthropic
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")

    # Vector Database
    chroma_db_path: Path = Field(
        default=Path("./data/chroma_db"),
        description="Path to ChromaDB storage",
    )

    # Application Settings
    should_local_embed: bool = Field(
        default=False,
        description="Whether to use local embedding model",
    )
    chunk_size: int = Field(default=1000, description="Text chunk size for splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model for generating embeddings",
    )

    llm_model: str = Field(default="gpt-4", description="LLM model name")
    llm_provider: str = Field(
        default="openai",
        description="LLM provider to use",
    )

    retrieval_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
