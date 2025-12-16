from pydantic import BaseModel, Field
from enum import StrEnum


class UserActionType(StrEnum):
    """
    Enumeration of high-level actions the agent can perform.
    """
    CHAT_INTERACTION = "chat_interaction"
    DATABASE_QUERY = "database_query"
    SEGMENTATION = "segmentation"
    SEASONALITY_TRENDS_PATTERNS = "seasonality_trends_patterns"
    SCHEMA_METADATA = "schema_metadata"


class UserAction(BaseModel):
    """
    Defines a structured representation of what the user wants the agent to do.

    This model helps the LLM decide how to handle a user's query and route it to the
    correct capability (metadata lookup, SQL over data, advanced analysis, or refusal).
    """

    action_description: str = Field(
        description = (
            """
            A detailed natural-language summary of the user's request or goal.
            Write it so it can be passed directly to the selected tool.
            Examples: 
            - 'list all tables in the dataset'
            - 'show monthly revenue trend for 2024'
            - 'analyze seasonality and peaks in weekly orders for the last 2 years'
            - 'segment customers by frequency and spend'
            - 'get columns and types for orders table'
            """
        )
    )

    action_type: UserActionType = Field(
        description = (
            """
            The category of user action to perform. Choose one of:
            - 'chat_interaction': off-topic/general chat; respond that the agent is DB-focused.
            - 'schema_metadata': questions about database structure/metadata (tables, columns, types,
            keys, relationships, partitions/clustering, table descriptions).
            - 'database_query': questions that require querying business/data rows (filters, joins,
            aggregations, KPIs, reporting).
            - 'customer_segmentation': advanced analytics/insights such as segmentation, behavior analysis, 
            product performance/recommendations, trends/seasonality, geographic patterns.
            - 'seasonality_trends_patterns': advanced analytics focused on time-based insights such as
            trends, seasonality, cycles, peaks/troughs, and anomalies.
            """
        )
    )

class SQLAction(BaseModel):
    """
    Structured output for SQL generation.
    The agent must output BigQuery Standard SQL (GoogleSQL).
    """
    sql_description: str = Field(
        description=(
            "Brief explanation of what the SQL does, including key tables, joins, and filters."
        )
    )
    sql_query: str = Field(
        description=(
            "A valid BigQuery Standard SQL query (GoogleSQL). Use backticks for identifiers, "
            "prefer fully-qualified tables like `project.dataset.table`, and do not include markdown fences."
        )
    )