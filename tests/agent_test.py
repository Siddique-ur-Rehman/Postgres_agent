
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

load_dotenv()

model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0
)

agent = create_agent(
    model=model,
    system_prompt="You are a helpful assistant who explains SQL concepts simply."
)

response = agent.invoke({
    "messages": [
        {"role": "user", "content": "What is a SQL JOIN?"}
    ]
})

print(response["messages"][-1].content)
