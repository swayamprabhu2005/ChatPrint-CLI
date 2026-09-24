"""Configuration management for AI Conversation CLI."""

from dataclasses import dataclass
from pathlib import Path

import platformdirs

APP_NAME = "ai-conversation"
APP_AUTHOR = "ai_conversation"


@dataclass
class Config:
    """Application runtime configuration."""

    default_output_dir: Path | None = None
    default_provider: str = "auto"
    debug: bool = False
    force_overwrite: bool = False

    @classmethod
    def get_config_dir(cls) -> Path:
        """Return the user configuration directory."""
        return Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))

    @classmethod
    def get_data_dir(cls) -> Path:
        """Return the user data directory."""
        return Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))

    @classmethod
    def get_cache_dir(cls) -> Path:
        """Return the user cache directory."""
        return Path(platformdirs.user_cache_dir(APP_NAME, APP_AUTHOR))
