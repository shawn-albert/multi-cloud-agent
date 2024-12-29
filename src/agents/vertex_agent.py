"""Vertex AI agent implementation.

This module contains the Google Cloud Vertex AI-specific agent implementation
with its configuration and tools.
"""

from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

from src.config.settings import settings
from src.models.responses import QueryResponse
from src.utils.logging import logger, with_logging


class VertexAgent:
    """Vertex AI agent implementation.

    This class manages the Vertex AI model configuration and provides
    methods for executing queries through the Vertex agent.

    Attributes:
        model: Configured Vertex AI model.
        agent: PydanticAI agent instance.
    """

    def __init__(self) -> None:
        """Initialize the Vertex agent with configuration from settings."""
        self.model = VertexAIModel(
            model="gemini-1.5-flash",
            project_id=settings.google_cloud_project,
            region="us-central1",
        )

        self.agent = Agent(self.model, result_type=QueryResponse)

        self._register_system_prompt()

    def _register_system_prompt(self) -> None:
        """Register the system prompt for the Vertex agent."""

        @self.agent.system_prompt
        async def system_prompt() -> str:
            return """
            You are a specialized SQL query assistant for Google BigQuery.
            Your role is to execute queries efficiently and provide detailed
            explanations of the results. Always validate queries before execution
            and ensure they follow BigQuery best practices.
            """

    @with_logging
    async def execute_query(self, query: str) -> QueryResponse:
        """Execute a query using the Vertex agent.

        Args:
            query: SQL query to execute.

        Returns:
            QueryResponse: Result of the query execution.

        Raises:
            Exception: If query execution fails.
        """
        try:
            logger.info("Executing Vertex query", query=query)
            result = await self.agent.run(query)
            return result.data
        except Exception as e:
            logger.error("Vertex query execution failed", error=e, query=query)
            raise


vertex_agent = VertexAgent()
