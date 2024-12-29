"""Configuration settings for the multi-cloud agent.

This module contains all configuration settings and environment variable handling
for the multi-cloud agent application.
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings and configuration.

    Attributes:
        azure_openai_deployment_name: Name of the Azure OpenAI deployment.
        azure_openai_api_key: API key for Azure OpenAI.
        azure_openai_endpoint: Endpoint URL for Azure OpenAI.
        azure_sql_connection_string: Connection string for Azure SQL Database.
        google_cloud_project: Google Cloud project ID.
        log_level: Logging level (default: INFO).
    """

    azure_openai_deployment_name: str
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_sql_connection_string: str
    google_cloud_project: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        """Create Settings instance from environment variables.

        Returns:
            Settings: Configured settings instance.

        Raises:
            ValueError: If required environment variables are missing.
        """
        required_vars = [
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_SQL_CONNECTION_STRING",
            "GOOGLE_CLOUD_PROJECT",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return cls(
            azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_sql_connection_string=os.getenv("AZURE_SQL_CONNECTION_STRING"),
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


settings = Settings.from_env()
