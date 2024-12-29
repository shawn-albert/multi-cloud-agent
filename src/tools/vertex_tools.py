"""Google BigQuery query tools.

This module provides tools for executing queries against Google BigQuery
with proper client management and error handling.
"""

import time

from google.api_core import retry
from google.cloud import bigquery

from src.config.settings import settings
from src.models.responses import QueryError, QueryResponse, QueryResult
from src.utils.logging import logger, with_logging


class BigQueryTools:
    """Tools for interacting with Google BigQuery.

    This class provides methods for executing queries against BigQuery
    with retry logic and error handling.

    Attributes:
        client: BigQuery client instance.
        project_id: Google Cloud project ID.
    """

    def __init__(self) -> None:
        """Initialize BigQuery tools with client configuration."""
        self.client = bigquery.Client(project=settings.google_cloud_project)
        self.project_id = settings.google_cloud_project

    @retry.Retry(predicate=retry.if_transient_error)
    async def _execute_with_retry(self, query: str) -> bigquery.QueryJob:
        """Execute BigQuery query with retry logic.

        Args:
            query: SQL query to execute.

        Returns:
            bigquery.QueryJob: Completed query job.

        Raises:
            Exception: If query execution fails after retries.
        """
        query_job = self.client.query(query)
        return query_job.result()

    @with_logging
    async def execute_query(self, query: str) -> QueryResponse:
        """Execute a query against BigQuery.

        Args:
            query: SQL query to execute.

        Returns:
            QueryResponse: Query result or error information.
        """
        start_time = time.time()

        try:
            results = await self._execute_with_retry(query)

            formatted_results = [dict(row.items()) for row in results]

            execution_time = time.time() - start_time

            return QueryResult(
                query=query,
                result=formatted_results,
                source="BigQuery",
                explanation=f"Successfully executed query returning {len(formatted_results)} rows",
                execution_time=execution_time,
            )

        except Exception as e:
            logger.error("BigQuery query execution failed", error=e, query=query)
            return QueryError(error_message=str(e), source="BigQuery", query=query)


bigquery_tools = BigQueryTools()
