import streamlit as st
from crewai import Crew, Process, Task
from agents import BitcoinCrew

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI

default_llm = ChatOpenAI(
    # model="gpt-4-turbo-preview"
    model="gpt-3.5-turbo-0125"
)


def engage_crew_with_tasks(selected_tasks):
    # define agents
    account_manager_agent = BitcoinCrew.account_manager()
    resource_manager_agent = BitcoinCrew.resource_manager()

    # create a crew
    bitcoin_crew = Crew(
        agents=[account_manager_agent, resource_manager_agent],
        process=Process.sequential,
        tasks=selected_tasks,
        verbose=1,
    )

    # run the crew against all tasks
    bitcoin_crew_result = bitcoin_crew.kickoff()

    return bitcoin_crew_result


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
            expected_output="The wallet address index, address, and nonce.",
        ),
        Task(
            description="What other wallet addresses do you have access to?",
            agent=account_manager_agent,
            expected_output="A list of wallet addresses organized by index.",
        ),
        Task(
            description="What is the aiBTC balance for your currently configured wallet?",
            agent=account_manager_agent,
            expected_output="The balance of aiBTC for the configured wallet.",
        ),
        Task(
            description="Get aiBTC from the faucet",
            agent=account_manager_agent,
            expected_output="The transaction ID for the aiBTC faucet drip.",
        ),
        Task(
            description="Get the transaction status for the aiBTC faucet drip",
            agent=account_manager_agent,
            expected_output="The status of the transaction for the aiBTC faucet drip.",
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
        if st.button("Engage Crew"):
            with st.expander("Running automated crew of AI agents!"):
                import sys
                import re
                import json

                class StreamToExpander:
                    def __init__(self, expander):
                        self.expander = expander
                        self.buffer = []
                        self.current_agent = None

                    def write(self, data):
                        cleaned_data = re.sub(r"\x1B\[[0-9;]*[mK]", "", data)
                        lines = cleaned_data.split("\n")
                        for line in lines:
                            if line.strip():
                                if "Working Agent:" in line:
                                    self.flush()
                                    agent_name = line.split("Working Agent:")[
                                        -1
                                    ].strip()
                                    if agent_name != self.current_agent:
                                        self.current_agent = agent_name
                                        self.expander.markdown(
                                            f"### {self.current_agent}"
                                        )
                                else:
                                    self.buffer.append(line)
                            else:
                                self.buffer.append(line)

                    def flush(self):
                        if self.buffer:
                            json_string = "\n".join(self.buffer)
                            try:
                                json_data = json.loads(json_string)
                                self.expander.json(json_data)
                            except json.JSONDecodeError:
                                self.expander.text(json_string)
                            self.buffer = []

                sys.stdout = StreamToExpander(st)
                with st.spinner("Engaging Crew..."):
                    crew_result = engage_crew_with_tasks(selected_tasks)
                    sys.stdout.flush()  # Flush any remaining output

            st.header("Results:")
            st.markdown("```json\n" + crew_result + "\n```")


if __name__ == "__main__":
    run_bitcoin_crew_app()
