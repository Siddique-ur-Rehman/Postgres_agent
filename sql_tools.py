
import os
import psycopg
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@tool
def get_database_schema() -> str:
    """Get the available tables and their column names in the database."""

    query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    return str(rows)

@tool
def execute_sql(query: str) -> str:
    """Execute a read-only PostgreSQL SELECT query and return its results."""

    try:
        with psycopg.connect(
            DATABASE_URL,
            options="-c default_transaction_read_only=on"
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SET LOCAL statement_timeout = '5000ms'")
                cur.execute(query)

                rows = cur.fetchmany(100)
                return str(rows)

    except Exception as e:
        return f"SQL execution error: {e}"
