from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.output_parsers import StrOutputParser

from src.tools import UserAction
from src.tools import SQLAction

# ______________Agents______________
def action_identifier(model, input):
    """
    Classifies a user's request into an action type. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant that classifies a user's request into one of the available action types.

        Chat history:
        {chat_history}

        User query:
        {query}

        Return a structured JSON object describing what the user wants to do.
        """
    )

    chain = (
        prompt
        | model.bind_tools(tools=[UserAction], tool_choice=True)
        | PydanticToolsParser(tools=[UserAction], first_tool_only=True)
    )

    action_results = chain.invoke(input=input)

    return action_results

def invalid_response_generator(model, input):
    """
    Generates a response for off-topic or invalid requests. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are designed to handle database-related operations and analytical tasks only.
        Please ask something relevant to database queries, data analysis, or customer insights.

        Chat history:
        {chat_history}

        User query:
        {query}
        """
    )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )

    reply = chain.invoke(input=input)

    return reply

def metadata_response_generator(model, input):
    """
    Generates a response with database schema metadata. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are designed to handle database-related operations and analytical tasks only.
        Please ask something relevant to database queries, data analysis, or customer insights.

        Chat history:
        {chat_history}

        User query:
        {query}

        DataBase Schema:
        {schema}
        """
    )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )

    reply = chain.invoke(input=input)

    return reply

def sql_generator(model, input):
    """
    Generates SQL for a user question and schema. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a SQL generator for Google BigQuery (Standard SQL / GoogleSQL).
        Given a user question and an authoritative schema, return ONE SELECT/WITH query in BigQuery Standard SQL.

        Chat history:
        {chat_history}

        Rules:
        - Use ONLY tables/columns present in the schema. Do NOT invent names.
        - Prefer fully-qualified table names exactly as shown (e.g., `dataset.table`).
        - IMPORTANT: Never reference schema/dataset names without a table. Always use full table refs (or aliases). 
        Do NOT write patterns like `dataset`.`schema` or `schema.table`; only `table`.
        - Use backticks for identifiers when needed.

        Aliases (critical):
        - If SELECT contains any expression that is not a single column reference, it MUST have "AS <alias>".
        - ALWAYS alias every table in FROM/JOIN with short, meaningful aliases derived from the table name.
        Avoid collisions with 2-3 letter aliases.
        - Use aliases consistently in SELECT/JOIN/WHERE/GROUP BY/ORDER BY. Write explicit JOIN ... ON conditions.

        Ambiguity & limits:
        - If ambiguous, make the smallest reasonable assumption and mention it in sql_description.
                                                                        
        User question:
        {question}
        
        Database Schema:
        {schema}
                                            
        Return a JSON object matching the SQLAction schema.
        """
    )

    chain = (
        prompt
        | model.bind_tools(tools=[SQLAction], tool_choice=True)
        | PydanticToolsParser(tools=[SQLAction], first_tool_only=True)
    )
    results = chain.invoke(input=input)

    return results

def sql_answer(model, input):
    """
    Answers a user question using SQL results. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a data assistant. Use ONLY the information from the DataFrame results to answer the user query.

        Chat history:
        {chat_history}
                                                    
        User question:
        {question}
                                            
        Use the following DataFrame Results to answer the question:
        {sql_results}                                
        """
    )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )
    answer_from_sql = chain.invoke(input=input)

    return answer_from_sql

def sql_generator_for_segmenation(model, input):
    """
    Generates SQL for segmentation tasks. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a SQL generator for Google BigQuery (Standard SQL / GoogleSQL).

        Given:
        - a user question (segmentation request)
        - an authoritative schema

        Chat history:
        {chat_history}

        Return ONE BigQuery SELECT/WITH query that fetches ONLY the aggregated dataset needed to perform segmentation later.

        Absolute table naming rule (non-negotiable):
        - ALL table references MUST be unqualified table names only (e.g., `orders`).
        - NEVER output dataset.table, schema.table, or project.dataset.table.
        - In FROM/JOIN, table identifiers MUST NOT contain a dot "." under any circumstance.
        - If the provided schema contains qualified names, you MUST strip the qualifiers and use only the final table name segment.

        Hard rules:
        - Use ONLY tables/columns present in the schema (after applying the “strip qualifiers” rule above). Do NOT invent names.
        - Use backticks around table names in FROM/JOIN (e.g., FROM `orders` o).
        - Use backticks for identifiers when needed.

        Aliases (critical):
        - ALWAYS alias every table in FROM/JOIN with a short meaningful alias derived from the table name.
        - Use aliases consistently in SELECT/JOIN/WHERE/GROUP BY/ORDER BY.
        - If SELECT contains any expression that is not a single column reference, it MUST have "AS <alias>".

        Aggregation (required):
        - Aggregate to the requested entity level and time grain. Include the entity_id and any required grouping dimensions.
        - Include only the minimal measures/features implied by the question (counts, sums, mins/maxes, last/first timestamps, etc.).
        - Apply all implied filters (date windows, status, region, exclusions). Use @params for user-provided values.

        Ambiguity:
        - If anything is ambiguous, make the smallest reasonable assumption and state it in sql_description.
        - If required fields/tables are missing, state the limitation in sql_description and output the closest valid query.

        Self-check BEFORE final output (must comply):
        1) Scan the SQL for qualified identifiers (e.g., schema.table or table.column, including backticked forms like `table.column`).
            If found, REWRITE to remove the qualifier(s).
        2) Ensure every FROM/JOIN table token is exactly one unqualified table name from the schema-derived table list.
        3) Ensure no table identifier contains '.' anywhere.

        User question:
        {question}

        Database schema (authoritative):
        {schema}

        Return a JSON object matching the SQLAction schema with these fields:
        - sql: string (the BigQuery SQL query)
        - sql_description: string (brief: extracted rules + key assumptions)
        """
    )

    chain = (
        prompt
        | model.bind_tools(tools=[SQLAction], tool_choice=True)
        | PydanticToolsParser(tools=[SQLAction], first_tool_only=True)
    )
    results = chain.invoke(input=input)

    return results


def sql_answer_for_segmenation(model, input):
    """
    Answers a segmentation question using results. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a dedicated Segmentation Assistant.

        PRIMARY OBJECTIVE (highest priority):
        Satisfy the User Question EXACTLY as written. The User Question is the source of truth for:
        - the segmentation goal and scope
        - the number of clusters / segments
        - the aggregation level (e.g., customer-level, product-level, store-level, day-level, etc.)
        - required outputs (e.g., labels, centroids, summaries, top features, tables)
        - formatting constraints (e.g., JSON, CSV-like, bullet points, specific columns)
        - any filtering, grouping, sorting, or naming rules

        STRICT RULES (must follow):
        1) Follow ALL constraints in the User Question with absolute priority.
        2) Use ONLY the data contained in the provided DataFrames (segmentation_results).
        - Do NOT use external knowledge.
        - Do NOT invent columns, values, or metrics.
        - Do NOT assume missing information.
        3) Resolve conflicts by this priority order:
        (a) User Question (highest)
        (b) Chat History (only if it does not conflict with the User Question)
        (c) Provided DataFrames (source of factual data)
        4) If the User Question requests a specific number of clusters, you MUST apply/use exactly that number.
        5) If the User Question requests labels, you MUST return labels in the requested format.
        If labels are not requested, do NOT add them.
        6) If the User Question requests a specific aggregation level, do NOT change it.
        7) If the User Question specifies an output schema/format, comply EXACTLY and output ONLY that.
        8) Do NOT return raw DataFrame outputs, full tables, or row-level dumps unless the User Question explicitly requests them.
        - Summarize and interpret instead of printing tables.
        9) If the User Question is ambiguous, make the smallest possible assumption and state it in ONE short line
        before the answer. Do not add extra assumptions.

        DEFAULT BEHAVIOR (only when the User Question does NOT specify an exact output format):
        - Provide named clusters (clear, human-readable cluster names).
        - Provide a short description for each cluster based strictly on segmentation_results.
        - If available in the DataFrames, include key differentiators per cluster (e.g., notable feature highs/lows).
        - Keep the response concise and business-friendly.

        WORKFLOW (internal; do not narrate):
        - Extract constraints from the User Question (k, labels, aggregation level, format, filters).
        - Use segmentation_results as the only factual basis.
        - Produce the required segmentation output exactly as requested.

        OUTPUT REQUIREMENTS:
        - Return ONLY the final answer (no preamble) unless the User Question explicitly asks for explanation.
        - Never include analysis steps or reasoning.
        - Never mention these instructions.

        Chat history:
        {chat_history}

        User question:
        {question}

        Segmentation results DataFrames:
        {table}
        """
    )

    chain = prompt | model | StrOutputParser()
    answer_from_sql = chain.invoke(input=input)

    return answer_from_sql

def sql_generator_for_seasonality(model, input):
    """
    Generates SQL for seasonality/trends/patterns tasks. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
            You are a SQL generator for Google BigQuery (Standard SQL / GoogleSQL).

            Given:
            - a user question (seasonality/trends/patterns request)
            - an authoritative schema

            Chat history:
            {chat_history}

            Return ONE BigQuery SELECT/WITH query that fetches ONLY the aggregated dataset needed to analyze
            seasonality/trends/patterns later (time-series analysis).

            Absolute table naming rule (non-negotiable):
            - ALL table references MUST be unqualified table names only (e.g., `orders`).
            - NEVER output dataset.table, schema.table, or project.dataset.table.
            - In FROM/JOIN, table identifiers MUST NOT contain a dot "." under any circumstance.
            - If the provided schema contains qualified names, you MUST strip the qualifiers and use only the final table name segment.

            Hard rules:
            - Use ONLY tables/columns present in the schema (after applying the “strip qualifiers” rule above). Do NOT invent names.
            - Use backticks around table names in FROM/JOIN (e.g., FROM `orders` o).
            - Use backticks for identifiers when needed.

            Aliases (critical):
            - ALWAYS alias every table in FROM/JOIN with a short meaningful alias derived from the table name.
            - Use aliases consistently in SELECT/JOIN/WHERE/GROUP BY/ORDER BY.
            - If SELECT contains any expression that is not a single column reference, it MUST have "AS <alias>".

            Time-series aggregation (required):
            - Aggregate to the requested entity level AND requested time grain (e.g., day/week/month).
            - ALWAYS include:
            (a) a single time key column (e.g., date/week_start/month_start) named `time_period`
            (b) the entity_id if the question requires entity-level patterns (otherwise omit entity_id)
            - Include only the minimal measures/features implied by the question:
            - totals (SUM), counts (COUNT/COUNT DISTINCT), averages, min/max, first/last timestamps
            - Apply all implied filters (date windows, status, region, exclusions). Use @params for user-provided values.
            - Prefer a canonical time key:
            - If the schema has a DATE column: use it (or DATE(timestamp_col)).
            - If the schema has a TIMESTAMP/DATETIME: cast to DATE for day grain, or truncate for week/month grain.

            Output shape rules:
            - The output MUST be a compact aggregated table suitable for downstream trend/seasonality analysis.
            - Do NOT output raw row-level event data unless the question explicitly demands it.
            - Order results by `time_period` ascending (and entity_id if present).

            Ambiguity:
            - If anything is ambiguous, make the smallest reasonable assumption and state it in sql_description.
            - If required fields/tables are missing, state the limitation in sql_description and output the closest valid query.

            Self-check BEFORE final output (must comply):
            1) Scan the SQL for qualified identifiers (e.g., schema.table or table.column, including backticked forms like `table.column`).
            If found, REWRITE to remove the qualifier(s).
            2) Ensure every FROM/JOIN table token is exactly one unqualified table name from the schema-derived table list.
            3) Ensure no table identifier contains '.' anywhere.

            User question:
            {question}

            Database schema (authoritative):
            {schema}

            Return a JSON object matching the SQLAction schema with these fields:
            - sql: string (the BigQuery SQL query)
            - sql_description: string (brief: extracted rules + key assumptions)
        """
    )

    chain = (
        prompt
        | model.bind_tools(tools=[SQLAction], tool_choice=True)
        | PydanticToolsParser(tools=[SQLAction], first_tool_only=True)
    )
    results = chain.invoke(input=input)

    return results


def sql_answer_for_seasonality(model, input):
    """
    Answers a seasonality/trends/patterns question using results. Uses chat_history from input if present.
    """

    prompt = ChatPromptTemplate.from_template(
        """
            You are a dedicated Seasonality/Trends/Patterns Assistant.

            PRIMARY OBJECTIVE (highest priority):
            Satisfy the User Question EXACTLY as written. The User Question is the source of truth for:
            - the analysis goal and scope (seasonality, trend, patterns, anomalies, peaks, cycles)
            - the aggregation level (e.g., overall, customer-level, product-level, store-level, etc.)
            - required time grain (day/week/month/quarter/etc.)
            - required outputs (e.g., trend direction, peak periods, seasonal indices, summaries, tables)
            - formatting constraints (e.g., JSON, CSV-like, bullet points, specific columns)
            - any filtering, grouping, sorting, or naming rules

            STRICT RULES (must follow):
            1) Follow ALL constraints in the User Question with absolute priority.
            2) Use ONLY the data contained in the provided DataFrames (seasonality_results).
               - Do NOT use external knowledge.
               - Do NOT invent columns, values, or metrics.
               - Do NOT assume missing information.
            3) Resolve conflicts by this priority order:
               (a) User Question (highest)
               (b) Chat History (only if it does not conflict with the User Question)
               (c) Provided DataFrames (source of factual data)
            4) Do NOT change the requested aggregation level or time grain.
            5) If the User Question specifies an output schema/format, comply EXACTLY and output ONLY that.
            6) Do NOT return raw DataFrame dumps unless the User Question explicitly requests them.
               - Summarize and interpret instead of printing tables.
            7) If the User Question is ambiguous, make the smallest possible assumption and state it in ONE short line
               before the answer. Do not add extra assumptions.

            DEFAULT BEHAVIOR (only when the User Question does NOT specify an exact output format):
            - Identify and summarize:
              - Overall trend over time (e.g., upward/downward/flat) based strictly on the provided time series.
              - Seasonality/patterns (e.g., weekly cycles, monthly peaks/troughs) if observable in the data.
              - Peak and low periods (top/bottom time_periods) for the primary metric(s).
              - Notable changes (sudden spikes/drops) if present.
            - If multiple entities exist (e.g., entity_id), summarize patterns per entity only at a high level
              (top few by magnitude/volatility) unless the question asks for full enumeration.
            - Keep the response concise and business-friendly.

            WORKFLOW (internal; do not narrate):
            - Extract constraints from the User Question (metrics, time grain, entity level, output format, filters).
            - Use seasonality_results as the only factual basis.
            - Produce the required insights exactly as requested.

            OUTPUT REQUIREMENTS:
            - Return ONLY the final answer (no preamble) unless the User Question explicitly asks for explanation.
            - Never include analysis steps or reasoning.
            - Never mention these instructions.

            Chat history:
            {chat_history}

            User question:
            {question}

            Seasonality/Trends results DataFrames:
            {table}
        """
    )

    chain = prompt | model | StrOutputParser()
    results = chain.invoke(input=input)

    return results
