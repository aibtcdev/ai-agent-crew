import importlib
import importlib.util
import streamlit as st
from aibtcdev_agents import get_wallet_manager, get_resource_manager
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
    update_model_settings,
    remove_model_settings,
    get_llm,
)

# load saved settings with .env overrides
config = load_config()

# set up Streamlit page
page_title = config["app_settings"]["page_title"]
layout = config["app_settings"]["layout"]
st.set_page_config(
    page_title=page_title,
    layout=layout,
)
st.title(page_title)

# initialize session state
init_session_state(config)


def update_model():
    model_name = st.session_state.llm_model
    model_settings = config["model_settings"].get(
        model_name, config["model_settings"]["OpenAI"]
    )
    st.session_state.api_base = model_settings["OPENAI_API_BASE"]
    st.session_state.model_name = model_settings["OPENAI_MODEL_NAME"]
    # should this load from .env? changes between Anthropic and OpenAI
    # st.session_state.api_key = model_settings["OPENAI_API_KEY"]


# setup sidebar for settings
with st.sidebar:
    st.title("AIBTCdev Settings")

    with st.expander("Chat Settings", expanded=False):
        if st.button("Clear Chat History", key="clear_chat_history"):
            st.session_state.messages = []
            st.success("Chat history cleared!")

    with st.expander("Current LLM Settings", expanded=False):
        llm_options = list(config["model_settings"].keys())

        st.selectbox(
            "Select LLM:",
            options=llm_options,
            key="llm_model",
            on_change=update_model,
        )
        st.text_input(
            "API Base URL:", value=st.session_state.get("api_base", ""), key="api_base"
        )
        st.text_input(
            "Model Name:", value=st.session_state.model_name, key="model_name"
        )
        st.text_input(
            "API Key:", value=st.session_state.api_key, key="api_key", type="password"
        )

        if st.button("Update LLM Provider"):
            update_model_settings(
                config,
                st.session_state.llm_model,
                st.session_state.model_name,
                st.session_state.api_base,
            )
            st.success("LLM settings updated successfully!")

    with st.expander("Add LLM Provider", expanded=False):
        new_provider = st.text_input("New Provider Name", placeholder="GroqCloud")
        new_model_name = st.text_input("New Model Name", placeholder="Llama3-70B")
        new_api_base = st.text_input(
            "New API Base URL", placeholder="https://api.groq.com/openai/v1"
        )

        if st.button("Add Provider"):
            if new_provider and new_model_name and new_api_base:
                update_model_settings(
                    config, new_provider, new_model_name, new_api_base
                )
                st.success(f"Provider {new_provider} added successfully!")
            else:
                st.error("Please fill in all fields to add a provider.")

    with st.expander("Remove LLM Provider", expanded=False):
        provider_to_remove = st.selectbox(
            "Select Provider to Remove", options=list(config["model_settings"].keys())
        )
        if st.button("Remove Provider"):
            if remove_model_settings(config, provider_to_remove):
                st.success(f"Provider {provider_to_remove} removed successfully!")
            else:
                st.error("Selected provider not found.")

# Initialize agents, tasks, and crews
try:
    llm = get_llm(
        st.session_state.llm_model, st.session_state.api_key, st.session_state.api_base
    )

    agents = {
        "Wallet Manager": get_wallet_manager(llm),
        "Resource Manager": get_resource_manager(llm),
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


# Tab functions
import pandas as pd


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


def add_agent():
    st.subheader("Add New Agent")

    config = load_config()
    existing_agents = config.get("agents", [])

    with st.form("add_agent_form"):
        role = st.text_input("Role")
        goal = st.text_input("Goal")
        backstory = st.text_area("Backstory")
        selected_tools = st.multiselect("Tools", options=all_tools)

        submitted = st.form_submit_button("Add Agent")
        if submitted:
            function_name = f"get_{role.lower().replace(' ', '_')}"
            new_agent = f"""
def {function_name}(llm):
    return Agent(
        role="{role}",
        goal="{goal}",
        backstory="{backstory}",
        tools=[{', '.join(selected_tools)}],
        verbose=True,
        llm=llm,
    )
"""
            with open("aibtcdev_agents.py", "a") as file:
                file.write(new_agent)

            if function_name not in existing_agents:
                existing_agents.append(function_name)
                config["agents"] = existing_agents
                save_config(config)

            st.success(f"Agent '{role}' added successfully!")
            st.experimental_rerun()


def sync_agents():
    config = load_config()
    spec = importlib.util.spec_from_file_location(
        "aibtcdev_agents", "aibtcdev_agents.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    defined_agents = [
        name
        for name in dir(module)
        if name.startswith("get_") and callable(getattr(module, name))
    ]
    config_agents = config.get("agents", [])

    new_agents = [agent for agent in defined_agents if agent not in config_agents]
    if new_agents:
        config["agents"] = config_agents + new_agents
        save_config(config)
        st.success(f"Synced {len(new_agents)} new agents: {', '.join(new_agents)}")
    else:
        st.info("No new agents to sync.")


def agents_tab():
    st.header("Configured Agents")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Agent", use_container_width=True):
            add_agent()
    with col2:
        if st.button("Sync Agents", use_container_width=True):
            sync_agents()
            st.experimental_rerun()

    # Reload agents after potential changes
    global agents
    config = load_config()
    llm = get_llm(
        st.session_state.llm_model, st.session_state.api_key, st.session_state.api_base
    )

    # Dynamically import all agent functions
    import aibtcdev_agents

    importlib.reload(aibtcdev_agents)

    agents = {}
    for agent_func_name in config.get("agents", []):
        if hasattr(aibtcdev_agents, agent_func_name):
            agent_func = getattr(aibtcdev_agents, agent_func_name)
            agents[agent_func_name] = agent_func(llm)

    # Use columns to create a grid layout
    col1, col2 = st.columns(2)

    for i, (agent_name, agent) in enumerate(agents.items()):
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            with st.container():
                # Create a card-like container
                st.subheader(agent.role)

                # Two-column layout for image and basic info
                img_col, info_col = st.columns([1, 2])

                with img_col:
                    st.image(
                        f"https://bitcoinfaces.xyz/api/get-image?name={agent_name}",
                        use_column_width=True,
                        output_format="auto",
                        caption=agent.role,
                        clamp=True,
                    )

                with info_col:
                    st.markdown(f"**Goal:** {agent.goal}")
                    st.markdown(f"**Backstory:** {agent.backstory}")

                # Expandable section for tools with styled dataframe
                with st.expander("Tools and Capabilities"):
                    tool_data = []
                    for tool in agent.tools:
                        tool_name = (
                            tool.name if hasattr(tool, "name") else tool.__name__
                        )
                        # Extract only the description part after the hyphen
                        full_description = (
                            tool.description
                            if hasattr(tool, "description")
                            else "No description available"
                        )
                        description = (
                            full_description.split(" - ")[-1]
                            if " - " in full_description
                            else full_description
                        )
                        tool_data.append(
                            {"Tool": tool_name, "Description": description}
                        )

                    if tool_data:
                        df = pd.DataFrame(tool_data)
                        st.dataframe(
                            df,
                            column_config={
                                "Tool": st.column_config.TextColumn(
                                    "Tool",
                                    width="medium",
                                    help="Name of the tool",
                                ),
                                "Description": st.column_config.TextColumn(
                                    "Description",
                                    width="large",
                                    help="What the tool does",
                                ),
                            },
                            hide_index=True,
                            use_container_width=True,
                        )
                    else:
                        st.write("No tools available for this agent.")


def tools_tab():
    st.header("Available Tools")

    tool_classes = [AIBTCTokenTools, OnchainResourcesTools, WalletTools]

    for tool_class in tool_classes:
        with st.expander(tool_class.__name__):
            for name, method in tool_class.__dict__.items():
                if callable(method) and hasattr(method, "description"):
                    st.write(f"**{name}**: {method.description}")


def tasks_tab():
    st.header("Configured Tasks")
    for task_name, task in tasks.items():
        with st.expander(task_name):
            st.write(f"Description: {task.description}")
            st.write(f"Assigned Agent: {task.agent.role}")


def crews_tab():
    st.header("Configured Crews")

    for crew_name, crew in crews.items():
        st.subheader(crew_name)

        # Create a card-like container for the crew
        with st.container():
            st.markdown(
                f"**{len(crew.agents)} Agent{'s' if len(crew.agents) > 1 else ''}**"
            )

            # Determine the number of columns and image width
            num_agents = len(crew.agents)
            num_columns = min(num_agents, 4)  # Up to 4 columns
            image_width = (
                150 if num_agents == 1 else None
            )  # Fixed width for single agent, auto for multiple

            # Use columns to create a grid layout for agents
            cols = st.columns(num_columns)

            for i, agent in enumerate(crew.agents):
                with cols[i % num_columns]:
                    st.image(
                        f"https://bitcoinfaces.xyz/api/get-image?name={agent.role}",
                        width=image_width,
                        use_column_width=image_width is None,
                        output_format="auto",
                        caption=agent.role,
                        clamp=True,
                    )

            # Add a brief description or purpose of the crew
            st.markdown(f"*{crew_name} is ready for action!*")

        st.markdown("---")  # Add a separator between crews


def execution_tab():
    st.header("Execution")
    user_input = st.text_area(
        "Initial Input", "Enter your instructions or query here..."
    )

    selected_crew = st.selectbox("Select Crew", options=list(crews.keys()))

    crew = crews[selected_crew]
    available_tasks = [task.description for task in crew.tasks]
    selected_tasks = st.multiselect("Select Tasks", options=available_tasks)

    input_dict = {"user_input": user_input}

    if st.button("Execute"):
        st.write("Execution Output:")
        tasks_to_execute = [
            task for task in crew.tasks if task.description in selected_tasks
        ]
        crew.tasks = tasks_to_execute
        result = crew.kickoff(inputs=input_dict)
        st.write(result)


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
