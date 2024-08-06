import anthropic
import streamlit as st
from crewai import Crew, Agent, Task, Process
from langchain_openai import ChatOpenAI
from tools.wallet import WalletTools
from tools.aibtc_token import AIBTCTokenTools
from tools.onchain_resources import OnchainResourcesTools
from utils import get_model_settings, save_model_settings, init_session_state


# Set up Streamlit page
st.set_page_config(page_title="AIBTCdev Crews", layout="wide")
st.title("AIBTCdev Crews")

# Get model settings
MODEL_SETTINGS = get_model_settings()

# Initialize session state
init_session_state(MODEL_SETTINGS)


def update_model():
    model_name = st.session_state.llm_model
    model_settings = MODEL_SETTINGS.get(model_name, MODEL_SETTINGS["OpenAi"])
    st.session_state.api_base = model_settings["OPENAI_API_BASE"]
    st.session_state.model_name = model_settings["OPENAI_MODEL_NAME"]


def get_llm():
    if st.session_state.llm_model == "Anthropic":
        return anthropic.Anthropic(api_key=st.session_state.api_key)
    else:
        return ChatOpenAI(
            model=st.session_state.model_name,
            openai_api_key=st.session_state.api_key,
            openai_api_base=st.session_state.api_base,
        )


# Sidebar Configuration
with st.sidebar:
    st.title("AIBTCdev Settings")

    with st.expander("LLM Settings", expanded=True):
        llm_options = list(MODEL_SETTINGS.keys())

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

        st.divider()

        if st.button("Clear Chat"):
            st.session_state.messages = []

    with st.expander("Manage Model Settings", expanded=False):
        new_provider = st.text_input("New Provider Name")
        new_model_name = st.text_input("New Model Name")
        new_api_base = st.text_input("New API Base")

        if st.button("Add/Update Provider"):
            if new_provider and new_model_name and new_api_base:
                MODEL_SETTINGS[new_provider] = {
                    "OPENAI_MODEL_NAME": new_model_name,
                    "OPENAI_API_BASE": new_api_base,
                }
                save_model_settings(MODEL_SETTINGS)
                st.success(f"Provider {new_provider} added/updated successfully!")
            else:
                st.error("Please fill in all fields to add/update a provider.")

        provider_to_remove = st.selectbox(
            "Select Provider to Remove", options=list(MODEL_SETTINGS.keys())
        )
        if st.button("Remove Provider"):
            if provider_to_remove in MODEL_SETTINGS:
                del MODEL_SETTINGS[provider_to_remove]
                save_model_settings(MODEL_SETTINGS)
                st.success(f"Provider {provider_to_remove} removed successfully!")
            else:
                st.error("Selected provider not found.")

# Define agents
try:
    llm = get_llm()

    wallet_manager = Agent(
        role="Wallet Manager",
        goal="Manage Bitcoin wallet operations and provide information",
        backstory="You are an expert in Bitcoin wallet management with deep knowledge of blockchain technology.",
        tools=[
            WalletTools.get_wallet_status,
            WalletTools.get_wallet_addresses,
            WalletTools.get_transaction_data,
            WalletTools.get_transaction_status,
            AIBTCTokenTools.get_aibtc_balance,
            AIBTCTokenTools.get_faucet_drip,
        ],
        verbose=True,
        llm=llm,
    )

    resource_manager = Agent(
        role="Resource Manager",
        goal="Manage on-chain resources and provide relevant information",
        backstory="You are an expert in managing blockchain resources and understanding complex on-chain data.",
        tools=[
            OnchainResourcesTools.get_recent_payment_data,
            OnchainResourcesTools.get_resource_data,
            OnchainResourcesTools.get_user_data_by_address,
            OnchainResourcesTools.pay_invoice_for_resource,
        ],
        verbose=True,
        llm=llm,
    )

    st.session_state.agents["Wallet Manager"] = wallet_manager
    st.session_state.agents["Resource Manager"] = resource_manager

except Exception as e:
    st.error(f"Error initializing language model: {str(e)}")
    st.stop()

# Define tasks
wallet_status_task = Task(
    description="Get the current wallet status and display the information.",
    expected_output="A detailed report of the current wallet status including balance and recent transactions.",
    agent=wallet_manager,
)

aibtc_balance_task = Task(
    description="Retrieve and display the current aiBTC balance.",
    expected_output="The current aiBTC balance as a numerical value with appropriate units.",
    agent=wallet_manager,
)

faucet_drip_task = Task(
    description="Request aiBTC from the faucet and display the transaction ID.",
    expected_output="The transaction ID of the aiBTC faucet drip request.",
    agent=wallet_manager,
)

get_resource_data_task = Task(
    description="Retrieve and display resource data for a given address",
    expected_output="A detailed report of the resource data associated with the provided address.",
    agent=resource_manager,
)

st.session_state.tasks["Get Wallet Status"] = wallet_status_task
st.session_state.tasks["Get aiBTC Balance"] = aibtc_balance_task
st.session_state.tasks["Get aiBTC Faucet Drip"] = faucet_drip_task
st.session_state.tasks["Get Resource Data"] = get_resource_data_task

# Define crews
wallet_crew = Crew(
    agents=[wallet_manager],
    tasks=[wallet_status_task, aibtc_balance_task, faucet_drip_task],
    process=Process.sequential,
    verbose=2,
)

resource_crew = Crew(
    agents=[resource_manager],
    tasks=[get_resource_data_task],
    process=Process.sequential,
    verbose=2,
)

st.session_state.crews["Wallet Crew"] = wallet_crew
st.session_state.crews["Resource Crew"] = resource_crew


# Tab functions
def agents_tab():
    st.header("Configured Agents")
    for agent_name, agent in st.session_state.agents.items():
        with st.expander(agent_name):
            st.write(f"Role: {agent.role}")
            st.write(f"Goal: {agent.goal}")
            st.write(f"Backstory: {agent.backstory}")
            st.write("Tools:")
            for tool in agent.tools:
                st.write(f"- {tool.name}")


def tasks_tab():
    st.header("Configured Tasks")
    for task_name, task in st.session_state.tasks.items():
        with st.expander(task_name):
            st.write(f"Description: {task.description}")
            st.write(f"Agent: {task.agent.role}")


def crews_tab():
    st.header("Configured Crews")
    for crew_name, crew in st.session_state.crews.items():
        with st.expander(crew_name):
            st.write("Agents:")
            for agent in crew.agents:
                st.write(f"- {agent.role}")
            st.write("Tasks:")
            for task in crew.tasks:
                st.write(f"- {task.description}")


def execution_tab():
    st.header("Execution")
    initial_input = st.text_area(
        "Initial Input", "Enter your instructions or query here..."
    )
    selected_crew = st.selectbox(
        "Select Crew", options=list(st.session_state.crews.keys())
    )

    crew = st.session_state.crews[selected_crew]
    available_tasks = [task.description for task in crew.tasks]
    selected_tasks = st.multiselect("Select Tasks", options=available_tasks)

    if st.button("Execute"):
        st.write("Execution Output:")
        # Filter the crew's tasks based on the selected task descriptions
        tasks_to_execute = [
            task for task in crew.tasks if task.description in selected_tasks
        ]

        # Update the crew's tasks
        crew.tasks = tasks_to_execute

        # Execute the crew
        result = crew.kickoff()
        st.write(result)


# Update crew definitions to include all possible tasks
wallet_crew = Crew(
    agents=[wallet_manager],
    tasks=[wallet_status_task, aibtc_balance_task, faucet_drip_task],
    process=Process.sequential,
    verbose=2,
)

resource_crew = Crew(
    agents=[resource_manager],
    tasks=[get_resource_data_task],
    process=Process.sequential,
    verbose=2,
)

st.session_state.crews["Wallet Crew"] = wallet_crew
st.session_state.crews["Resource Crew"] = resource_crew

# Main layout with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Agents", "Tasks", "Crews", "Execution"])

with tab1:
    agents_tab()

with tab2:
    tasks_tab()

with tab3:
    crews_tab()

with tab4:
    execution_tab()

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.markdown("Welcome to AIBTCdev Interactive Wallet Manager!")
