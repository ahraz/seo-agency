import os
from crewai import LLM
from config.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL
)


def get_llm():
    # Allow runtime override (e.g. from UI Settings page)
    api_key = os.environ.get("OPENAI_API_KEY") or DEEPSEEK_API_KEY
    model = os.environ.get("OPENAI_MODEL") or DEEPSEEK_MODEL

    return LLM(
        model=model,
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.2
    )
