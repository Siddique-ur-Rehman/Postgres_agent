# Natural Language SQL Agent

A simple AI-powered SQL agent that lets users interact with a PostgreSQL database using natural language instead of writing SQL queries manually.

The project uses LangChain, LangGraph, Google Gemini, PostgreSQL, and Streamlit to understand questions, generate SQL queries, and display results in a chat interface.

## Features

- Ask database questions in plain English.
- Generate and execute PostgreSQL `SELECT` queries.
- View database schema through tools.
- Use conversation memory for follow-up questions.
- Save conversation history using PostgreSQL checkpoints.
- Start new conversations with unique UUIDs.
- View and resume previous conversations.
- Use SQL safety middleware to block common unsafe queries.
- Access the agent through a Streamlit dashboard or terminal.

## Tech Stack

- **Python** — Main programming language
- **LangChain** — Agent and tool integration
- **LangGraph** — Conversation memory and checkpoints
- **Google Gemini** — Language model
- **PostgreSQL** — Database and conversation storage
- **Streamlit** — Chat interface
- **uv** — Python package and environment management

## Project Structure

```text
agent_lgch/
├── app.py
├── main.py
├── sql_agent.py
├── sql_tools.py
├── sql_middleware.py
├── conversation_store.py
├── tests/
├── README.md
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .python-version
└── .gitignore
```

## Requirements

Before starting, make sure you have:

- Python version compatible with the project configuration
- PostgreSQL
- A Google Gemini API key
- `uv` installed

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/natural-language-sql-agent.git
cd natural-language-sql-agent
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=your_readonly_database_url
CHECKPOINT_DATABASE_URL=your_checkpoint_database_url
```

Replace the example values with your own credentials.

- `GOOGLE_API_KEY` is used to access Google Gemini.
- `DATABASE_URL` connects to the application database using a read-only account.
- `CHECKPOINT_DATABASE_URL` connects to PostgreSQL for LangGraph conversation checkpoints.

**Important:** Never commit your `.env` file or share your API keys and database passwords.

### 4. Set up PostgreSQL

Create a PostgreSQL database and configure the required tables and permissions.

The example project uses a `students` table with these columns:

| Column | Description |
|---|---|
| `id` | Student ID |
| `name` | Student name |
| `age` | Student age |
| `department` | Student department |
| `marks` | Student marks |

The application also uses a conversation table to store conversation IDs and titles. LangGraph manages its own checkpoint tables for conversation history.

Ensure that the database user used by the SQL tools has read-only access to the data being queried.

## Run the Application

### Streamlit dashboard

```bash
uv run streamlit run app.py
```

### Terminal agent

```bash
uv run sql_agent.py
```

Use the interface to ask questions about your database.

## Example Questions

- How many students are in the database?
- Show the top 5 students by marks.
- Calculate the average marks of each department.
- Which student has the highest marks?
- Show students from the Data Science department.
- How many students are older than 21?

## Safety

The agent is designed for read-only database queries. The application includes SQL safety middleware, and the database connection should use a read-only PostgreSQL account.

The middleware is an additional safeguard, not a complete SQL security system. Database permissions are an important layer of protection.

## Future Improvements

- Improve SQL query validation.
- Add more automated tests.
- Improve error handling and result formatting.
- Add database schema selection.
- Improve conversation management in the dashboard.

## License

This project is available for learning and personal development. Add a license file if you want to specify how others may use, modify, and distribute it.
