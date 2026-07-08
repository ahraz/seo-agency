import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("OPENAI_API_KEY")

DEEPSEEK_MODEL = os.getenv(
    "OPENAI_MODEL",
    "deepseek-chat"
)

DEEPSEEK_BASE_URL = os.getenv(
    "OPENAI_API_BASE",
    "https://api.deepseek.com"
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
