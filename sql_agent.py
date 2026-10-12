
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from sql_middleware import sql_safety_middleware
import os
from langgraph.checkpoint.postgres import PostgresSaver

from sql_tools import get_database_schema, execute_sql

load_dotenv()
database_url = os.getenv("DATABASE_URL")
model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0
)

system_prompt = """
You are a natural-language-to-SQL assistant with conversation memory.

Your responsibilities:
1. Understand the user's question.
2. Use get_database_schema to inspect available tables and columns.
3. Generate valid PostgreSQL SELECT queries.
4. Use execute_sql to run queries.
5. Explain query results in simple language.
6. Remember relevant information the user shares within the current conversation, including their name and previous questions.
7. Use earlier messages when answering follow-up questions.

Rules:
- Only answer database questions using the available tools.
- Never invent table names, columns, or query results.
- Only execute read-only SELECT queries.
- If a query fails, explain the error briefly.
- Use conversation history to answer questions about information the user previously shared.
- If the information is not in the conversation history, say you do not know.
- Return clear, concise answers.
"""

agent = create_agent(
    model=model,
    tools=[get_database_schema, execute_sql],
    system_prompt=system_prompt,
    middleware=[sql_safety_middleware],
)


if __name__ == "__main__":
    with PostgresSaver.from_conn_string(
        os.environ["CHECKPOINT_DATABASE_URL"]
    ) as checkpointer:

        # Create the checkpoint tables if needed.
        checkpointer.setup()

        agent = create_agent(
            model=model,
            tools=[get_database_schema, execute_sql],
            system_prompt=system_prompt,
            middleware=[sql_safety_middleware],
            checkpointer=checkpointer,
        )

        thread_id = input("Enter conversation ID: ").strip()

        if not thread_id:
            thread_id = "conversation_001"

        while True:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                break

            if not question:
                continue

            response = agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": question}
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": thread_id
                    }
                },
            )

            print("\nAgent:")
            content = response["messages"][-1].content

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        print(item["text"])
            else:
                print(content)
