import io
import contextlib
import re
import time
import threading
import streamlit as st
from crewai import Crew, Process, Task
from crewai.tasks import TaskOutput
from agents import BitcoinCrew

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI


@contextlib.contextmanager
def capture_stdout():
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        yield buffer


default_llm = ChatOpenAI(
    # model="gpt-4-turbo-preview"
    model="gpt-3.5-turbo-0125"
)


# initialize agent messages and avatars
agent_messages = {}
agent_avatars = {
    "Account Manager": "https://bitcoinfaces.xyz/api/get-image?name=account-manager",
    "Resource Manager": "https://bitcoinfaces.xyz/api/get-image?name=resource-manager",
}

# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def task_output_to_string(output: TaskOutput) -> str:
    return f"Description: {output.description}\nSummary: {output.summary}\nResult: {output.result}"


def get_task_description(output: TaskOutput) -> str:
    return f"{output.description}"


def get_task_result(output: TaskOutput) -> str:
    return f"{output.raw_output}"


def format_chat_message(agent_name, message):
    return f"**{agent_name}:**\n{message}"


def display_agent_output(agent, messages, avatar_url, placeholder):
    with placeholder.container():
        for message in messages:
            with st.chat_message(agent, avatar=avatar_url):
                st.write(format_chat_message(agent, message))
                time.sleep(0.1)  # Add a small delay for better visibility
        st.session_state.messages.append(
            {"role": agent, "content": "\n".join(messages)}
        )


file_output = []


def streamlit_callback(output: TaskOutput):
    agent_name = "Account Manager"  # temporary

    if agent_name not in agent_messages:
        agent_messages[agent_name] = []

    output_str = task_output_to_string(output)
    task_description = get_task_description(output)
    task_result = get_task_result(output)
    file_output.append(f"\n**{task_description}**\n\n{task_result}")
    agent_messages[agent_name].append(f"{task_description}\n\n{task_result}")

    # Update Streamlit UI in real-time
    avatar_url = agent_avatars.get(agent_name)
    placeholder = st.empty()  # Create a placeholder for dynamic content
    display_agent_output(
        agent_name, agent_messages[agent_name], avatar_url, placeholder
    )


def engage_crew_with_tasks(selected_tasks):
    print("Engaging crew with tasks:", selected_tasks)
    # Clear the session state before engaging the crew
    st.session_state.messages = []

    # define agents
    account_manager_agent = BitcoinCrew.account_manager()
    resource_manager_agent = BitcoinCrew.resource_manager()

    # Create a crew
    bitcoin_crew = Crew(
        agents=[account_manager_agent, resource_manager_agent],
        process=Process.sequential,
        tasks=selected_tasks,
        verbose=1,
        task_callback=lambda output: streamlit_callback(output),
    )

    print("Kicking off the crew")
    crew_result = bitcoin_crew.kickoff()

    # Create a YYYY-MM-DD-HH-MM timestamp
    from datetime import datetime

    file_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")

    # create generated-meeting-agenda.md file with the result
    with open(f"wallet/{file_timestamp}-completed-tasks.md", "w") as file:
        file.write("# Wallet Crew\n\n")
        file.write("\n".join(file_output))
        file.write("## Final Result\n\n")
        file.write(crew_result)


def run_bitcoin_crew_app():
    st.title("Bitcoin Crew")

    # define agents
    account_manager_agent = BitcoinCrew.account_manager()
    resource_manager_agent = BitcoinCrew.resource_manager()

    # define the tasks
    account_manger_tasks = [
        Task(
            description="What information do you know about the currently configured wallet?",
            agent=account_manager_agent,
            expected_output="A markdown list including the wallet address index, address, and nonce.",
        ),
        Task(
            description="What other wallet addresses do you have access to?",
            agent=account_manager_agent,
            expected_output="A markdown list of wallet addresses organized by index.",
        ),
        Task(
            description="What is the aiBTC balance for your currently configured wallet?",
            agent=account_manager_agent,
            expected_output="The balance of aiBTC for the configured wallet in human readable form.",
        ),
        Task(
            description="Get aiBTC from the faucet",
            agent=account_manager_agent,
            expected_output="The transaction ID for the aiBTC faucet drip in human readable form.",
        ),
        Task(
            description="Get the transaction status for the aiBTC faucet drip",
            agent=account_manager_agent,
            expected_output="The status of the transaction for the aiBTC faucet drip in human readable form.",
        ),
    ]
    resource_manager_tasks = [
        Task(
            description="Get our configured wallet address and remember to use it in later tasks.",
            agent=resource_manager_agent,
            expected_output="The wallet address for the configured wallet.",
        ),
        Task(
            description="Get our most recent payment data",
            agent=resource_manager_agent,
            expected_output="The most recent payment data for our address.",
        ),
        Task(
            description="Get the available resource data",
            agent=resource_manager_agent,
            expected_output="The available resources in the contract.",
        ),
        Task(
            description="Get our user data by using the address from wallet status",
            agent=resource_manager_agent,
            expected_output="The user data for the address from the contract.",
        ),
        Task(
            description="Pay an invoice for a resource",
            agent=resource_manager_agent,
            expected_output="The transaction ID for the invoice payment.",
        ),
        Task(
            description="Get the transaction status for the invoice payment using the txid.",
            agent=resource_manager_agent,
            expected_output="The status of the transaction for the invoice payment.",
        ),
    ]

    tab1, tab2, tab3 = st.tabs(["Agents", "Tasks", "Engage Crew"])

    with tab1:
        st.subheader(f"{account_manager_agent.role}")
        st.markdown(f"**Goal**: {account_manager_agent.goal}")
        st.markdown(f"**Backstory**: {account_manager_agent.backstory}")

        st.subheader(f"{resource_manager_agent.role}")
        st.markdown(f"**Goal**: {resource_manager_agent.goal}")
        st.markdown(f"**Backstory**: {resource_manager_agent.backstory}")

    with tab2:
        st.subheader("Account Manager Tasks")
        selected_account_manager_tasks = []
        for task in account_manger_tasks:
            if st.checkbox(task.description, key=f"account_manager_{task.description}"):
                selected_account_manager_tasks.append(task)

        st.subheader("Resource Manager Tasks")
        selected_resource_manager_tasks = []
        for task in resource_manager_tasks:
            if st.checkbox(
                task.description, key=f"resource_manager_{task.description}"
            ):
                selected_resource_manager_tasks.append(task)

        selected_tasks = (
            selected_account_manager_tasks + selected_resource_manager_tasks
        )

    with tab3:
        st.subheader("Selected Tasks")
        if selected_tasks:
            for task in selected_tasks:
                st.write(f"- {task.description}")
        else:
            st.write("No tasks selected.")

        if st.button("Engage Crew", use_container_width=True):
            print("Engage Crew button clicked")
            with st.spinner("Engaging Crew..."):
                engage_crew_with_tasks(selected_tasks)
            print("Crew execution completed")


if __name__ == "__main__":
    run_bitcoin_crew_app()
