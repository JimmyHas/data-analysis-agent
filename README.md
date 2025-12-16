# Data Analysis Agent

A modular Python agent for automated data analysis, segmentation, and querying using Google BigQuery and generative AI. Designed for both interactive CLI and service-based use.

---

## Project Structure

```
data-analysis-agent/
├── main.py                  # Main CLI entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API keys, project info)
├── README.md                # Project documentation
└── src/
	├── big_query_runner.py  # BigQuery integration and execution
   ├── tools.py             # Helper functions and action types
	├── agents.py            # Agent logic and orchestration
	└── service.py           # Service logic for data processing
```

---

## Features

- Modular, agent-based architecture
- Google BigQuery integration for scalable analytics
- Natural-language to SQL for general database questions
- Schema & metadata Q&A (tables, columns, relationships, definitions)
- Data segmentation and trend/seasonality analysis
- In-memory chat history for context-aware CLI sessions
- Easily extensible for new data sources or logic

---

## Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
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

4. **Configure environment variables:**
   - Edit `.env` and set your Google API key, project, dataset, and model name:
     ```env
     GOOGLE_AI_API_KEY=your-key
     PROJECT_ID=your-gcp-project
     DATASET_ID=your-bigquery-dataset
     MODEL_NAME=your-model
     ```

---

## Usage

### 1. Run the CLI Agent

Start an interactive chat session for data analysis:

```sh
python main.py
```

Type your data questions or requests. Type `exit` to quit. Each session maintains its own chat history in memory.

---

### 2. Customization

- Extend BigQuery logic in `src/big_query_runner.py`
- Add or modify agent logic in `src/agents.py`
- Add new tools or action types in `src/tools.py`

---

