from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

from utils.text import dedent_and_strip


class Settings(BaseSettings):
    APP_NAME: str = Field(
        "genai-function-calling-api", description="Name of the application."
    )
    EMB_BLOB: str = Field(
        "product_embeddings.json", description="Embeddings JSON file."
    )
    EMB_BUCKET: str = Field(
        "bkt-bu1-d-function-calling-api-embedding",
        description="Bucket for storing embeddings JSON file.",
    )
    EMB_DEPLOYED_INDEX_ID: str = Field(
        "index_01_deploy_1734488317622", description="Vector search index ID."
    )
    EMB_DF_HEAD: int = Field(
        100,
        ge=1,
        description="Take first 100 records only. To avoid quota exceeded error.",
    )
    EMB_DIMENSIONALITY: int = Field(768, ge=1, description="Embeddings dimensionality.")
    EMB_INDEX_ENDPOINT: str = Field(
        "projects/770674777462/locations/us-central1/indexEndpoints/5963364040964046848",
        description="Vector search index endpoint.",
    )
    EMB_MODEL: Literal["text-embedding-004", "text-embedding-005"] = Field(
        "text-embedding-005", description="The embedding Model to use."
    )
    EMB_TOP_K: int = Field(
        3,
        ge=1,
        description="Default top results to retrieve.",
    )
    ENV: Literal["dev", "npr", "prd"] = Field(
        "dev", description="Application environment."
    )
    GOOGLE_CLOUD_PROJECT: str = Field(
        "prj-bu1-d-sample-base-9208", description="The Google Cloud project ID."
    )
    HTTP_CLIENT_BASE_URL: str = Field(
        "https://api.openweathermap.org", description="OpenWeather API base url"
    )
    LLM_CHAT_BUCKET: str = Field(
        "bkt-bu1-d-function-calling-api-chat",
        description="Bucket for storing chat history.",
    )
    LLM_PROMPT_TOKENS_LIMIT: int = Field(
        2500,
        description="Maximum prompt tokens including user input, tools, and system instructions.",
    )
    LLM_QUOTA_BUCKET: str = Field(
        "bkt-bu1-d-function-calling-api-quota",
        description="Bucket for storing llm quota usage.",
    )
    LLM_QUOTA_TOKENS_LIMIT: int = Field(
        12500,
        description="Total LLM token usage allowed per user per day.",
    )
    LLM_MAX_OUTPUT_TOKENS: int = Field(
        100, le=100, description="Maximum output tokens."
    )
    LLM_MODEL: Literal[
        "gemini-1.5-pro-001",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro-002",
        "gemini-1.5-flash-002",
        "gemini-2.0-flash-exp",
        # "gemini-2.0-flash-thinking-exp-1219", # does not support function calling
        # "gemini-1.5-flash-8b", # small model, not available in vertex ai
    ] = Field("gemini-2.0-flash-exp", description="The foundation model to use.")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", description="Logging level."
    )
    OPENWEATHER_API_KEY: str = Field(
        ...,  # Required field (this means it must be provided through env)
        json_schema_extra={"env": "OPENWEATHER_API_KEY"},
        description="OpenWeather API key.",
    )
    REGION: Literal["us-central1"] = Field("us-central1", description="The GCP region.")
    SYSTEM_INSTRUCTION: str = Field(
        dedent_and_strip(
            """
        Ask clarifying questions if not enough information is available.
        """
        ),
        description="System instruction for the Model.",
    )


settings = Settings()  # type: ignore
