import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools import UserActionType
from src.agents import action_identifier
from src.agents import invalid_response_generator
from src.agents import metadata_response_generator
from src.agents import sql_generator
from src.agents import sql_answer
from src.agents import sql_generator_for_segmenation
from src.agents import sql_answer_for_segmenation
from src.agents import sql_generator_for_seasonality
from src.agents import sql_answer_for_seasonality

from src.big_query_runner import BigQueryRunner

# Set-Up Environment
_=load_dotenv()
google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
project_id = os.getenv('PROJECT_ID')
dataset_id = os.getenv('DATASET_ID')
model_name = os.getenv('MODEL_NAME')

# Define Model
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=google_ai_api_key,
    project=project_id,
    vertexai=False,
    temperature=0
)

# BigQuery Runner
runner = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)

# Service
def data_analysis_service(human_message, chat_history=None):
    """
    Main service function for data analysis agent.
    Accepts a human_message and a chat_history (list of dicts with 'role' and 'content').
    Chat history is kept in memory for the session and can be used for context.
    """
    if chat_history is None:
        chat_history = []

    action_results = action_identifier(model, {"query": human_message, "chat_history": chat_history})

    if action_results.action_type == UserActionType.CHAT_INTERACTION:
        response = invalid_response_generator(model, {"query": action_results.action_description, "chat_history": chat_history})
    else:
        schema = {
            'orders': {'description': 'Customer order information', 'schema': runner.get_table_schema('orders')},
            'order_items': {'description': 'Individual items within orders', 'schema': runner.get_table_schema('order_items')},
            'users': {'description': 'Customer demographics and information', 'schema': runner.get_table_schema('users')},
            'products': {'description': 'Product catalog and details', 'schema': runner.get_table_schema('products')},
        }
        for _ in range(1):  # Add fallback loop in case of SQL failure
            try:
                if action_results.action_type == UserActionType.DATABASE_QUERY:
                    sql_generation_results = sql_generator(model, {"question": action_results.action_description, "schema": schema, "chat_history": chat_history})
                    execution = runner.execute_query(sql_query=sql_generation_results.sql_query)
                    response = sql_answer(model, {"question": action_results.action_description, "sql_results": execution, "chat_history": chat_history})
                elif action_results.action_type == UserActionType.SCHEMA_METADATA:
                    response = metadata_response_generator(model, {"query": action_results.action_description, "schema": schema, "chat_history": chat_history})
                elif action_results.action_type == UserActionType.SEGMENTATION:
                    sql_generation_results = sql_generator_for_segmenation(model, {"question": action_results.action_description, "schema": schema, "chat_history": chat_history})
                    execution = runner.execute_query(sql_query=sql_generation_results.sql_query)
                    response = sql_answer_for_segmenation(model, {"question": action_results.action_description, "table": execution, "chat_history": chat_history})
                elif action_results.action_type == UserActionType.SEASONALITY_TRENDS_PATTERNS:
                    sql_generation_results = sql_generator_for_seasonality(model, {"question": action_results.action_description, "schema": schema, "chat_history": chat_history})
                    execution = runner.execute_query(sql_query=sql_generation_results.sql_query)
                    response = sql_answer_for_seasonality(model, {"question": action_results.action_description, "table": execution, "chat_history": chat_history})
            except Exception as e:
                response = """
                    An error occurred while processing your request.
                    Please try again!
                """        

    return response