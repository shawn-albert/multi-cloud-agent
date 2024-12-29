"""Response models for the multi-cloud agent.

This module defines the Pydantic models used for structuring responses
from both Azure and Google Cloud services.
"""

from typing import Any

from pydantic import BaseModel, Field


class QueryResult(BaseModel):
    """Successful query response model.

    Attributes:
        query: The executed SQL query.
        result: List of query results.
        source: Source of the query (Azure SQL or BigQuery).
        explanation: Human-readable explanation of the query execution.
        execution_time: Time taken to execute the query in seconds.
    """

    query: str = Field(..., description="The executed SQL query")
    result: list[Any] = Field(..., description="Query results")
    source: str = Field(..., description="Source system (Azure SQL or BigQuery)")
    explanation: str = Field(..., description="Human-readable explanation")
    execution_time: float = Field(..., description="Query execution time in seconds")


class QueryError(BaseModel):
    """Error response model.

    Attributes:
        error_message: Description of the error.
        source: Source system where the error occurred.
        query: The query that caused the error (if available).
    """

    error_message: str = Field(..., description="Error description")
    source: str = Field(..., description="Source system where error occurred")
    query: str | None = Field(None, description="Query that caused the error")


QueryResponse = QueryResult | QueryError
