import anthropic
import inspect
import importlib
import os
import streamlit as st
from crews import agents, tasks
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from typing import Optional, List
from crews.smart_contract_auditor import SmartContractAuditCrew
from crews.wallet_summarizer import WalletSummaryCrew
from crews.clarity_code_generator import ClarityCodeGeneratorCrew


def load_env_vars():
    load_dotenv()
    env_vars = {}
    for key, value in os.environ.items():
        env_vars[key] = value
    return env_vars


def sync_agents():
    importlib.reload(agents)
    st.session_state.agents = {}
    for name, func in inspect.getmembers(agents, inspect.isfunction):
        if name.startswith("get_"):
            agent_name = name[4:].replace("_", " ").title()
            st.session_state.agents[agent_name] = func


def sync_tasks():
    importlib.reload(tasks)
    st.session_state.tasks = {}
    for name, func in inspect.getmembers(tasks, inspect.isfunction):
        if name.startswith("get_"):
            task_name = name.replace("_", " ").title()
            st.session_state.tasks[task_name] = func


def init_session_state():
    env_vars = load_env_vars()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agents" not in st.session_state:
        st.session_state.agents = {}

    if "tasks" not in st.session_state:
        st.session_state.tasks = {}

    if "tasks_search_term" not in st.session_state:
        st.session_state.tasks_search_term = ""

    if "crew_mapping" not in st.session_state:
        st.session_state.crew_mapping = {
            "Smart Contract Auditor": {
                "class": SmartContractAuditCrew,
                "task_inputs": SmartContractAuditCrew.get_task_inputs,
            },
            "Wallet Summarizer": {
                "class": WalletSummaryCrew,
                "task_inputs": WalletSummaryCrew.get_task_inputs,
            },
            "Clarity Code Generator": {
                "class": ClarityCodeGeneratorCrew,
                "task_inputs": ClarityCodeGeneratorCrew.get_task_inputs,
            },
        }

    # Initialize other session state variables
    defaults = {
        "provider": env_vars.get("LLM_PROVIDER", "OpenAI"),
        "api_key": env_vars.get("OPENAI_API_KEY", ""),
        "api_base": env_vars.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "model": env_vars.get("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize the LLM
    if "llm" not in st.session_state:
        st.session_state.llm = get_llm(
            st.session_state.provider,
            st.session_state.model,
            st.session_state.api_key,
            st.session_state.api_base,
        )


def update_session_state(key, value):
    st.session_state[key] = value


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


def get_crew_class(crew_name: str) -> Optional[type]:
    crew_info = st.session_state.crew_mapping.get(crew_name)
    return crew_info["class"] if crew_info else None


def get_crew_inputs(crew_name: str):
    crew_info = st.session_state.crew_mapping.get(crew_name)
    if crew_info and "task_inputs" in crew_info:
        return crew_info["task_inputs"]()
    return []
