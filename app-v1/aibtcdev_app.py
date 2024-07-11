import importlib.util
import streamlit as st
from components.sidebar import render_sidebar
from components.agents_tab import render_agents_tab
from components.crews_tab import render_crews_tab
from components.execution_tab import render_execution_tab
from components.tasks_tab import render_tasks_tab
from components.tools_tab import render_tools_tab
from aibtcdev_agents import BitcoinCrew
from aibtcdev_tools import AIBTCTokenTools, OnchainResourcesTools, WalletTools
from aibtcdev_tasks import (
    get_wallet_status_task,
    get_aibtc_balance_task,
    get_faucet_drip_task,
    get_resource_data_task,
)
from aibtcdev_crews import get_wallet_crew, get_resource_crew
from aibtcdev_utils import (
    load_config,
    save_config,
    init_session_state,
    get_llm,
)

# load saved settings with .env overrides
app_config = load_config()

# set up Streamlit page
page_title = app_config["app_settings"]["page_title"]
layout = app_config["app_settings"]["layout"]
st.set_page_config(
    page_title=page_title,
    layout=layout,
)
st.title(page_title)

# initialize session state
init_session_state(app_config)

# setup sidebar for settings
render_sidebar(app_config)

# Initialize agents, tasks, and crews
try:
    llm = get_llm(
        st.session_state.llm_model, st.session_state.api_key, st.session_state.api_base
    )

    agents = {
        "Wallet Manager": BitcoinCrew.get_account_manager(llm),
        "Resource Manager": BitcoinCrew.get_resource_manager(llm),
        "Transaction Manager": BitcoinCrew.get_transaction_manager(llm),
    }

    tasks = {
        "Get Wallet Status": get_wallet_status_task(agents["Wallet Manager"]),
        "Get aiBTC Balance": get_aibtc_balance_task(agents["Wallet Manager"]),
        "Get aiBTC Faucet Drip": get_faucet_drip_task(agents["Wallet Manager"]),
        "Get Resource Data": get_resource_data_task(agents["Resource Manager"]),
    }

    crews = {
        "Wallet Crew": get_wallet_crew(agents, tasks),
        "Resource Crew": get_resource_crew(agents, tasks),
    }

except Exception as e:
    st.error(f"Error initializing language model: {str(e)}")
    st.stop()


# Assume all_tools is a list of all available tools
def is_tool(name, obj):
    return callable(obj) and not name.startswith("__") and hasattr(obj, "description")


all_tools = (
    [
        tool
        for tool in dir(AIBTCTokenTools)
        if is_tool(tool, getattr(AIBTCTokenTools, tool))
    ]
    + [
        tool
        for tool in dir(OnchainResourcesTools)
        if is_tool(tool, getattr(OnchainResourcesTools, tool))
    ]
    + [tool for tool in dir(WalletTools) if is_tool(tool, getattr(WalletTools, tool))]
)


def crews_tab():
    render_crews_tab(crews=crews)


def agents_tab():
    render_agents_tab(llm=llm, all_tools=all_tools)


def tools_tab():
    render_tools_tab()


def tasks_tab():
    render_tasks_tab(tasks)


def execution_tab():
    render_execution_tab(crews)


# Tab styling
tab_style = """
<style>
button[data-baseweb="tab"] {
    margin: 0;
    width: 100%;
}
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 18px !important;
}
</style>
"""
st.write(tab_style, unsafe_allow_html=True)

# Main layout with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Crews", "Agents", "Tools", "Tasks", "Execution"]
)

with tab1:
    crews_tab()

with tab2:
    agents_tab()

with tab3:
    tools_tab()

with tab4:
    tasks_tab()

with tab5:
    execution_tab()


# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.markdown("AIBTCdev Interactive Wallet Manager")
