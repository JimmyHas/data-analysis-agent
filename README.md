# Data Analysis Agent

A conversational command-line tool for natural language data analysis using Google BigQuery and Gemini (Google Generative AI). This agent interprets user queries, generates SQL, runs analysis, and returns results in plain English.

## Features
- Modular, agent-based architecture
- Google BigQuery integration for scalable analytics
- Natural-language to SQL for general database questions
- Schema & metadata Q&A (tables, columns, relationships, definitions)
- Data segmentation and trend/seasonality analysis
- In-memory chat history for context-aware CLI sessions
- Easily extensible for new data sources or logic

## Requirements
- Python 3.9+
- Google Cloud account with BigQuery access
- Google Cloud service account credentials (for BigQuery)

## Installation
1. **Clone the repository:**
	```sh
	git clone <repo-url>
	```
2. **Create and activate a virtual environment (recommended):**
   ```sh
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/Mac:
   source .venv/bin/activate
   ```
3. **Install dependencies:**
	```sh
	pip install -r requirements.txt
	```
4. **Set up Google Cloud credentials:**
	- Ensure your environment is authenticated to access BigQuery (e.g., set `GOOGLE_APPLICATION_CREDENTIALS` to your service account JSON file).
5. **Configure environment variables:**
	- Edit the `.env` file with your API keys and project info:
	  ```env
	  GOOGLE_AI_API_KEY=your_google_ai_api_key
	  PROJECT_ID=your_gcp_project_id
	  DATASET_ID=your_bigquery_dataset_id
	  MODEL_NAME=your_google_model
	  ```

## Usage
### Interactive Chat Mode
Run the CLI and start chatting:
```sh
python main.py
```
- Type your data analysis question (e.g., "Show Top 20 users with most orders").
- Type `exit` or `quit` to leave.

## Example Queries
- "List all tables in the dataset."
- "Segment customers by frequency and spend."
- "Analyze seasonality in weekly orders for the last 2 years."
- "Get columns and types for orders table."

## How it Works
1. **User Input:** You type a question in natural language.
2. **Action Identification:** The agent classifies your intent (query, segmentation, trends, metadata, etc.).
3. **SQL Generation:** If needed, the agent generates SQL for BigQuery.
4. **Execution:** SQL is run on BigQuery; results are summarized.
5. **Response:** The answer is returned in plain English.