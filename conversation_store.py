
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        os.environ["CHECKPOINT_DATABASE_URL"]
    )


def create_conversations_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                thread_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)


def save_conversation(thread_id, title):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO chat_conversations (thread_id, title)
            VALUES (%s, %s)
            ON CONFLICT (thread_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                updated_at = NOW()
        """, (thread_id, title))


def get_conversations():
    with get_connection() as conn:
        return conn.execute("""
            SELECT thread_id, title, created_at
            FROM chat_conversations
            ORDER BY updated_at DESC
        """).fetchall()


def delete_conversation_record(thread_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM chat_conversations
            WHERE thread_id = %s
        """, (thread_id,))
