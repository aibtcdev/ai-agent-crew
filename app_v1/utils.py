import anthropic
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from components.agents_tab import sync_agents
from components.tasks_tab import sync_tasks


def load_env_vars():
    load_dotenv()
    env_vars = {}
    for key, value in os.environ.items():
        env_vars[key] = value
    return env_vars


def init_session_state():
    env_vars = load_env_vars()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agents" not in st.session_state:
        st.session_state.agents = {}

    if "tasks" not in st.session_state:
        st.session_state.tasks = {}

    # Initialize other session state variables
    defaults = {
        "llm_model": "OpenAI",
        "api_key": env_vars.get("OPENAI_API_KEY", ""),
        "api_base": env_vars.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "model_name": env_vars.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize the LLM
    if "llm" not in st.session_state:
        st.session_state.llm = get_llm(
            st.session_state.llm_model,
            st.session_state.api_key,
            st.session_state.api_base,
        )

    # Sync agents
    sync_agents()

    # Sync tasks
    sync_tasks()


def update_session_state(key, value):
    st.session_state[key] = value


def get_llm(model, api_key, api_base):
    if model == "Anthropic":
        return anthropic.Anthropic(api_key=api_key)
    else:
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=api_base,
        )
