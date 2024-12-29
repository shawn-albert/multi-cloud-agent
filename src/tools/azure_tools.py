"""Azure SQL Database query tools.

This module provides tools for executing queries against Azure SQL Database
with proper connection management and error handling.
"""

import time
from contextlib import asynccontextmanager

import pyodbc

from src.config.settings import settings
from src.models.responses import QueryError, QueryResponse, QueryResult
from src.utils.logging import logger, with_logging


class AzureSQLTools:
    """Tools for interacting with Azure SQL Database.

    This class provides methods for executing queries against Azure SQL Database
    with connection pooling and error handling.

    Attributes:
        connection_string: Azure SQL Database connection string.
        connection_pool: Optional connection pool for query execution.
    """

    def __init__(self) -> None:
        """Initialize Azure SQL tools with connection settings."""
        self.connection_string = settings.azure_sql_connection_string
        self.connection_pool: list[pyodbc.Connection] | None = None

    @asynccontextmanager
    async def get_connection(self):
        """Async context manager for database connections.

        Yields:
            pyodbc.Connection: Database connection from the pool.

        Raises:
            Exception: If connection cannot be established.
        """
        connection = None
        try:
            connection = pyodbc.connect(self.connection_string)
            yield connection
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    logger.error("Error closing Azure SQL connection", error=e)

    @with_logging
    async def execute_query(self, query: str) -> QueryResponse:
        """Execute a query against Azure SQL Database.

        Args:
            query: SQL query to execute.

        Returns:
            QueryResponse: Query result or error information.
        """
        start_time = time.time()

        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                results = cursor.fetchall()
                columns = [column[0] for column in cursor.description]

                formatted_results = [
                    dict(zip(columns, row, strict=False)) for row in results
                ]

                execution_time = time.time() - start_time

                return QueryResult(
                    query=query,
                    result=formatted_results,
                    source="Azure SQL",
                    explanation=f"Successfully executed query returning {len(formatted_results)} rows",
                    execution_time=execution_time,
                )

        except Exception as e:
            logger.error("Azure SQL query execution failed", error=e, query=query)
            return QueryError(error_message=str(e), source="Azure SQL", query=query)


azure_sql_tools = AzureSQLTools()
