import anthropic
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


def load_env_vars():
    load_dotenv()
    env_vars = {}
    for key, value in os.environ.items():
        env_vars[key] = value
    return env_vars

def get_llm(provider, model, api_key, api_base):
    if provider == "Anthropic":
        return anthropic.Anthropic(api_key=api_key)
    elif provider == "Ollama":
        return ChatOllama(model=model, base_url=api_base)
    else:
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=api_base,
        )