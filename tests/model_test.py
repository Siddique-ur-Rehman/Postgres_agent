
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0
)

response = model.invoke("Explain what SQL is in two simple sentences.")

print(response.content)
