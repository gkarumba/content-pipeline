"""
Config — loads environment variables and validates required keys.
Copy .env.example to .env and fill in your values.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # OpenAI / Claude
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ai_provider: str = "openai"         # "openai" or "anthropic"
    ai_model: str = "gpt-4o-mini"       # or "claude-haiku-4-5-20251001" for Anthropic

    # Serper (Google Search API)
    serper_api_key: str = ""

    # Airtable
    airtable_api_key: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = "Content Pipeline"

    # OpenAI Image Generation (thumbnails)
    enable_image_gen: bool = False       # Set True to generate real DALL-E thumbnails

    # Optional: Buffer for scheduling
    buffer_access_token: str = ""
    buffer_profile_ids: str = ""        # comma-separated Buffer profile IDs

    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")
        self.ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")
        self.airtable_api_key = os.getenv("AIRTABLE_API_KEY", "")
        self.airtable_base_id = os.getenv("AIRTABLE_BASE_ID", "")
        self.airtable_table_name = os.getenv("AIRTABLE_TABLE_NAME", "Content Pipeline")
        self.enable_image_gen = os.getenv("ENABLE_IMAGE_GEN", "false").lower() == "true"
        self.buffer_access_token = os.getenv("BUFFER_ACCESS_TOKEN", "")
        self.buffer_profile_ids = os.getenv("BUFFER_PROFILE_IDS", "")

    def validate(self) -> list[str]:
        """Returns list of missing required config keys."""
        missing = []
        if not self.serper_api_key:
            missing.append("SERPER_API_KEY")
        if not self.airtable_api_key:
            missing.append("AIRTABLE_API_KEY")
        if not self.airtable_base_id:
            missing.append("AIRTABLE_BASE_ID")
        if self.ai_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        return missing