"""Azure OpenAI agent implementation.

This module contains the Azure-specific agent implementation with its
configuration and tools.
"""

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from src.config.settings import settings
from src.models.responses import QueryResponse
from src.utils.logging import logger, with_logging


class AzureAgent:
    """Azure OpenAI agent implementation using PydanticAI.

    This class manages the Azure OpenAI model configuration and provides
    methods for executing queries through the Azure OpenAI service.

    Attributes:
        client: Configured Azure OpenAI client
        model: PydanticAI OpenAI model instance
        agent: PydanticAI agent instance
    """

    def __init__(self) -> None:
        """Initialize the Azure agent with OpenAI configuration."""
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-02-01-preview",
            api_key=settings.azure_openai_api_key,
        )

        self.model = OpenAIModel(
            settings.azure_openai_deployment_name, openai_client=self.client
        )

        self.agent = Agent(self.model)
        self._register_system_prompt()

    def _register_system_prompt(self) -> None:
        """Register the system prompt for the Azure agent."""

        @self.agent.system_prompt
        async def system_prompt() -> str:
            return """
            You are a specialized SQL query assistant for Azure SQL Database.
            Your role is to execute queries safely and provide detailed explanations
            of the results. Always validate queries before execution and ensure
            they follow best practices.
            """

    @with_logging
    async def execute_query(self, query: str) -> QueryResponse:
        """Execute a query using the Azure OpenAI agent.

        Args:
            query: SQL query to execute.

        Returns:
            QueryResponse: Result of the query execution.

        Raises:
            Exception: If query execution fails.
        """
        try:
            logger.info("Executing Azure query", query=query)
            result = await self.agent.run(query)
            return result.data
        except Exception as e:
            logger.error("Azure query execution failed", error=e, query=query)
            raise


azure_agent = AzureAgent()
