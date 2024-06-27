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
    init_session_state,
    update_model_settings,
    remove_model_settings,
    get_llm,
)

# Load configuration
config = load_config()

# Set up Streamlit page
st.set_page_config(
    page_title=config["app_settings"]["page_title"],
    layout=config["app_settings"]["layout"],
)
st.title(config["app_settings"]["page_title"])

# Initialize session state
init_session_state(config)


def update_model():
    model_name = st.session_state.llm_model
    model_settings = config["model_settings"].get(
        model_name, config["model_settings"]["OpenAI"]
    )
    st.session_state.api_base = model_settings["OPENAI_API_BASE"]
    st.session_state.model_name = model_settings["OPENAI_MODEL_NAME"]


# Sidebar Configuration
with st.sidebar:
    st.title("AIBTCdev Settings")

    with st.expander("LLM Settings", expanded=True):
        llm_options = list(config["model_settings"].keys())

        st.selectbox(
            "Select LLM Provider",
            options=llm_options,
            key="llm_model",
            on_change=update_model,
        )

        st.text_input("API Base", value=st.session_state.api_base, key="api_base")
        st.text_input("Model", value=st.session_state.model_name, key="model_name")
        st.text_input(
            "API Key", value=st.session_state.api_key, key="api_key", type="password"
        )

        if st.button("Clear Chat"):
            st.session_state.messages = []

    with st.expander("Manage Model Settings", expanded=False):
        new_provider = st.text_input("New Provider Name")
        new_model_name = st.text_input("New Model Name")
        new_api_base = st.text_input("New API Base")

        if st.button("Add/Update Provider"):
            if new_provider and new_model_name and new_api_base:
                update_model_settings(
                    config, new_provider, new_model_name, new_api_base
                )
                st.success(f"Provider {new_provider} added/updated successfully!")
            else:
                st.error("Please fill in all fields to add/update a provider.")

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
def agents_tab():
    st.header("Configured Agents")

    # Use columns to create a grid layout
    col1, col2 = st.columns(2)

    for i, (agent_name, agent) in enumerate(agents.items()):
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            with st.container():
                # Create a card-like container
                # st.subheader(agent_name)

                # Two-column layout for image and basic info
                img_col, info_col = st.columns([1, 2])

                with img_col:
                    st.image(
                        f"https://bitcoinfaces.xyz/api/get-image?name={agent.role}",
                        use_column_width=True,
                        output_format="auto",
                        caption=agent_name,
                        clamp=True,
                    )

                with info_col:
                    st.markdown(f"**Role:** {agent.role}")
                    st.markdown(f"**Goal:** {agent.goal}")
                    st.markdown(f"**Backstory:** {agent.backstory}")

                # Expandable sections for tools
                with st.expander("Tools"):
                    for tool in agent.tools:
                        st.markdown(f"- {tool.name}")


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
        with st.expander(crew_name):
            st.write("Agents:")
            for agent in crew.agents:
                st.write(f"- {agent.role}")
            st.write("Tasks:")
            for task in crew.tasks:
                st.write(f"- {task.description}")


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


# Main layout with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Agents", "Tools", "Tasks", "Crews", "Execution"]
)

with tab1:
    agents_tab()

with tab2:
    tools_tab()

with tab3:
    tasks_tab()

with tab4:
    crews_tab()

with tab5:
    execution_tab()


# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.markdown("AIBTCdev Interactive Wallet Manager")
