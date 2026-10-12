
import os
import uuid
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver

from sql_tools import get_database_schema, execute_sql
from conversation_store import (
    create_conversations_table,
    save_conversation,
    get_conversations,
    delete_conversation_record,
)
from sql_middleware import sql_safety_middleware

load_dotenv()
create_conversations_table()
import streamlit as st

st.set_page_config(
    page_title="SQL Agent",
    page_icon="🗄️",
    layout="wide"
)

system_prompt = """
You are a natural-language-to-SQL assistant with conversation memory.

Your responsibilities:
1. Understand the user's question.
2. Use get_database_schema to inspect available tables and columns.
3. Generate valid PostgreSQL SELECT queries.
4. Use execute_sql to run queries.
5. Explain results in simple language.
6. Remember relevant information shared in the current conversation.
7. Use earlier messages to answer follow-up questions.

Rules:
- Answer database questions using the available tools.
- Never invent table names, columns, or query results.
- Only execute read-only SELECT queries.
- If a query fails, explain the error briefly.
- Use conversation history when answering follow-up questions.
- If information is unavailable, say you do not know.
- Return clear, concise answers.
"""

model = init_chat_model(
    model="gemini-3.5-flash-lite",
    model_provider='google_genai',
    temperature=0
)

@st.cache_resource
def get_sql_agent():
    checkpointer_context = PostgresSaver.from_conn_string(
        os.environ["CHECKPOINT_DATABASE_URL"]
    )
    checkpointer = checkpointer_context.__enter__()
    checkpointer.setup()

    agent = create_agent(
        model=model,
        tools=[get_database_schema, execute_sql],
        system_prompt=system_prompt,
        middleware=[sql_safety_middleware],
        checkpointer=checkpointer,
    )

    return agent, checkpointer_context


agent, checkpointer_context = get_sql_agent()

def load_conversation_messages(thread_id):
    state = agent.get_state(
        {"configurable": {"thread_id": thread_id}}
    )

    messages = []

    if not state or not state.values:
        return messages

    for msg in state.values.get("messages", []):
        role = getattr(msg, "type", "")

        if role not in ("human", "ai"):
            continue

        content = msg.content

        if isinstance(content, list):
            content = "\n".join(
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        if not content:
            continue

        messages.append({
            "role": "user" if role == "human" else "assistant",
            "content": str(content),
        })

    return messages


if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []
st.title("🗄️ Natural Language SQL Agent")
st.caption("Ask questions about your PostgreSQL database in plain English.")

# Sidebar

# Sidebar
with st.sidebar:
    st.header("Conversations")

    if st.button("＋ New Conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Fetch saved conversations from PostgreSQL
    conversations = get_conversations()

    if not conversations:
        st.caption("No previous conversations found.")
    else:
        for thread_id, title, created_at in conversations:
            col1, col2 = st.columns([4, 1])

            with col1:
                
                if st.button(
                    title,
                    key=f"open_{thread_id}",
                use_container_width=True,
                    ):
                    st.session_state.thread_id = thread_id
                    st.session_state.messages = load_conversation_messages(thread_id)
                    st.rerun()


            with col2:
                if st.button("🗑️", key=f"delete_{thread_id}"):
                    delete_conversation_record(thread_id)

                    if st.session_state.thread_id == thread_id:
                        st.session_state.thread_id = str(uuid.uuid4())
                        st.session_state.messages = []

                    st.rerun()


# Current conversation messages
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your database..."):

    # Save a new conversation using its UUID
    if not st.session_state.messages:
        save_conversation(
            st.session_state.thread_id,
            prompt[:60]
        )
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

  
    with st.spinner("Thinking..."):
        response = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            config={
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            },
        )

        content = response["messages"][-1].content

        if isinstance(content, list):
            answer = "\n".join(
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )
        else:
            answer = str(content)

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

