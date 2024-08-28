import anthropic
import inspect
import importlib
import os
import requests
import streamlit as st
from aibtc_crews import agents, tasks
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


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

    # sync from related CrewAI files
    sync_agents()
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


def fetch_contract_source(contract_address, contract_name):
    url = f"https://api.hiro.so/v2/contracts/source/{contract_address}/{contract_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("source")
    else:
        return f"Error: {response.status_code} - {response.text}"


def fetch_function(contract_address, contract_name):
    url = (
        f"https://api.hiro.so/v2/contracts/interface/{contract_address}/{contract_name}"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("functions")
    else:
        return f"Error: {response.status_code} - {response.text}"


diagram_llm = ChatOpenAI(model="gpt-4o")


def create_diagram(contract_code):
    prompt_template = """
    You are a visualization expert specializing in creating clear and informative flow diagrams using mermaid. Analyze the following Clarity smart contract code and its functions, then create a simplest mermaid code to visualize the internal control flow of the contract with correct syntax. Ensure the flow diagram code matches strictly with the documentation.

    This diagram should include:

    Nodes: Representing different functions and processes of the contract.
    Edges: Showing how the flow of execution moves between the functions.
    The code should be compatible with streamlit-mermaid version 0.2.0
    Contract Code:

    {contract_code}

    Generate only a simple Mermaid diagram code as text, nothing extra. Use appropriate colors and shapes to represent different elements in diagram. Ensure that the diagrams are clear and simplest.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    diagram_chain = prompt | diagram_llm

    response = diagram_chain.invoke({"contract_code": contract_code})

    diagram_code = response.content
    diagram_code = diagram_code.replace("`", "").replace("mermaid", "")

    return diagram_code
