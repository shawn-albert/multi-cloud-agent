"""Main application module for the multi-cloud agent with Logfire integration.

This module provides the main entry point and orchestration for the
multi-cloud agent application with comprehensive observability.
"""

import asyncio
import time
from dataclasses import dataclass

import logfire
from logfire import span

from .agents.azure_agent import azure_agent
from .agents.vertex_agent import vertex_agent
from .models.responses import QueryError, QueryResponse
from .utils.logging import logger, with_logging


@dataclass
class MultiCloudQueryResult:
    """Results from multi-cloud query execution.

    Attributes:
        azure_result: Result from Azure SQL query.
        vertex_result: Result from BigQuery query.
        execution_time: Total execution time in seconds.
    """

    azure_result: QueryResponse
    vertex_result: QueryResponse
    execution_time: float


class MultiCloudAgent:
    """Multi-cloud agent orchestrator with Logfire observability."""

    @with_logging
    @span("execute_multi_cloud_query")
    async def execute_query(
        self, query: str, azure_only: bool = False, vertex_only: bool = False
    ) -> MultiCloudQueryResult:
        """Execute query across specified cloud platforms with tracing.

        Args:
            query: SQL query to execute.
            azure_only: Only execute on Azure SQL.
            vertex_only: Only execute on BigQuery.

        Returns:
            MultiCloudQueryResult: Combined results from all executions.

        Raises:
            ValueError: If both azure_only and vertex_only are True.
        """
        if azure_only and vertex_only:
            raise ValueError("Cannot specify both azure_only and vertex_only")

        start_time = time.time()

        with logfire.span("prepare_query_tasks"):
            tasks = []
            if not vertex_only:
                tasks.append(azure_agent.execute_query(query))
            if not azure_only:
                tasks.append(vertex_agent.execute_query(query))

        with logfire.span("execute_queries") as span:
            span.set_attribute("query", query)
            span.set_attribute("azure_enabled", not vertex_only)
            span.set_attribute("vertex_enabled", not azure_only)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        with logfire.span("process_results"):
            azure_result = results[0] if not vertex_only else None
            vertex_result = results[-1] if not azure_only else None

            execution_time = time.time() - start_time

            return MultiCloudQueryResult(
                azure_result=azure_result,
                vertex_result=vertex_result,
                execution_time=execution_time,
            )


multi_cloud_agent = MultiCloudAgent()


@span("main")
async def main():
    """Main application entry point with Logfire tracing."""
    # Example query
    query = """
    SELECT COUNT(*) as record_count
    FROM my_table
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 day'
    """

    try:
        with logfire.span("execute_example_query"):
            result = await multi_cloud_agent.execute_query(query)

        logger.info(
            "Multi-cloud query completed",
            execution_time=result.execution_time,
            azure_status="success"
            if not isinstance(result.azure_result, QueryError)
            else "error",
            vertex_status="success"
            if not isinstance(result.vertex_result, QueryError)
            else "error",
        )
        return result
    except Exception as e:
        logger.error("Multi-cloud query failed", error=e)
        raise


if __name__ == "__main__":
    logfire.configure(
        service_name="multi-cloud-agent",
        service_version="1.0.0",
        environment="production",
    )
    asyncio.run(main())
