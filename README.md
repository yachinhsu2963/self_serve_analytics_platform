# Self-Service Analytics: Natural Language to SQL + Visualization
A self-service analytics web app that enables business stakeholders to generate SQL queries and visualizations simply by typing natural language. This app uses the Olist e-commerce dataset from Kaggle stored in a MySQL database, The app is powered by a Groq LLM API for query generation, NL4DV for data-to-visual insight mapping, and Streamlit for an intuitive user interface.

## Key Features
- Translate natural language prompts into SQL queries using the Groq API
- Execute SQL queries on a MySQL database (olist_data)
- Automatically visualize results with Altair charts
- Enable non-technical users to explore data without writing code
- Reusable, fast, and no-code interface

## Tech Stack
- Frontend: Streamlit
- Backend: Python, MySQL
- NLP-to-SQL: Groq API
- Natural Language → Visualization Mapping: NL4DV, Stanford CoreNLP
- Visualization: Altair

## Run Locally
### 1. Install dependencies
`pip install -r requirements.txt`

### 2. Setup Stanford NLP Parser
Due to file size limits, JAR files are not included in this repository. Please download the following files manually:
- [stanford-parser-3.9.2-models.jar](https://nlp.stanford.edu/software/lex-parser.shtml)
- [stanford-english-corenlp-2018-10-05-models.jar](https://stanfordnlp.github.io/CoreNLP/)

Place them in the parsers/ folder like this:

### 3. Set up MySQL database
Ensure a MySQL instance is running with the olist_data database and your credentials.

### 4. Configure connection
Copy the example config and fill in your info:
`cp config/db_connect.json.example db_connect.json`

### 5. Run the app
`streamlit run app/main_app.py`

### Team
Yen-Hsi Kuo, Sam Neal, Ruth Hsu, Maggie Wang, Rachel Liang
