import requests
import streamlit as st
import time
from crewai import Agent, Crew, Process, Task
from crewai_tools import tool
from langchain_ollama import ChatOllama
from textwrap import dedent
from utils.session import crew_step_callback, crew_task_callback
from .tools import StacksWalletTools


####################
# AGENTS
####################


class AIBTC_Agents:

    @staticmethod
    def get_wallet_data_retriever_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="wallet data retriever",
            goal="Retrieve basic wallet information from a single tool call.",
            tools=[StacksWalletTools.get_address_balance_detailed],
            backstory=dedent(
                """
                You are a blockchain data analyst specializing in wallet activity on the Stacks blockchain."""
            ),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def get_wallet_transactions_retriever_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="transaction retriever",
            goal="Retrieve the last 20 transactions for the specified wallet, if available.",
            tools=[StacksWalletTools.get_address_transactions],
            backstory=dedent(
                """
               You are an expert in blockchain transaction analysis, capable of efficiently querying and filtering large data sets. Your are an expert in JSON parsing."""
            ),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def get_activity_analyzer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="activity analyzer",
            goal="Analyze the retrieved data to determine the type of activity the wallet is usually involved in, such as frequent transactions, holding patterns, and interaction with contracts.",
            tools=[],
            backstory=dedent(
                """
               You are a blockchain activity analyst with expertise in behavioral analysis on the Stacks blockchain. """
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def get_report_compiler_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="report compiler",
            goal="Compile all output into a final report.",
            tools=[],
            backstory=dedent(
                """
               You are a technical writer with expertise in creating clear and concise reports on complex blockchain topics in the Clarity language on the Stacks blockchain."""
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )


####################
# TASKS
####################


class AIBTC_Tasks:

    # retrieve_wallet_info_task
    @staticmethod
    def retrieve_wallet_info_task(agent, address):
        return Task(
            description=dedent(
                f"""
                Retrieve wallet balance detailed information for the specified address.
                
                Here is the address that I need to retrieve wallet balances for:
                {address}

                Your response should be a WalletInfo json object containing the wallet address, STX balance, NFT holdings, and FT holdings.
                """
            ),
            expected_output="A WalletInfo json object containing the wallet address, STX balance, NFT holdings, and FT holdings.",
            agent=agent,
        )

    # retrieve_transactions_task
    @staticmethod
    def retrieve_transactions_task(agent, address):
        return Task(
            description=dedent(
                f"""
                Retrieve the last transactions associated with an address.
                
                Heres the Address that i need to find transactions for
                {address}

                Your response should be a TransactionList object containing up to 20 transactions associated with the wallet, including details like transaction type (tx_type), date (block_time_iso),  events (stx, ft, nft) and involved parties (tx_sender, tx_recipient, tx_contract_caller, tx_contract_address).
                """
            ),
            expected_output="A TransactionList object containing up to 20 transactions associated with the wallet, including only details like transaction type (tx_type), date (block_time_iso), events (stx, ft, nft) and involved parties (tx_sender, tx_recipient, tx_contract_caller, tx_contract_address). I do not need any other information. I need it to be simplified so it can be passed on as context.",
            agent=agent,
        )

    # analyze_activity_task
    @staticmethod
    def analyze_activity_task(agent, address):
        return Task(
            description=dedent(
                f"""
                The wallet being analyzed is:
                {address}
                Analyze the wallet’s activity patterns, such as frequency of transactions, types of transactions, and interactions with smart contracts.
                Your response should be a WalletActivityAnalysis object containing insights into the wallet’s activity, including active periods, most common transaction types, and overall engagement in the blockchain ecosystem.
                """
            ),
            expected_output="A WalletActivityAnalysis object containing insights into the wallet’s activity, including active periods, most common transaction types, and overall engagement in the blockchain ecosystem.",
            agent=agent,
            tools=[],
        )

    # compile_report_task
    @staticmethod
    def compile_report_task(agent, address):
        return Task(
            description=dedent(
                f"""
                Compile all analyses into a comprehensive final report for address {address}.
                Use the following information from the crew's shared memory to create a detailed report:
                1. Wallet Info 
                2. Transactions 
                3. Activity Analysis
                """
            ),
            # expected_output="A WalletReport object containing all the information gathered from previous tasks, formatted in a clear and organized manner.",
            expected_output="A clear summary of the wallet's activity and holdings, formatted in markdown. Do not display any json.",
            agent=agent,
            tools=[],
            async_execution=False,
        )


####################
# CREW(S)
####################


class AIBTC_Crew:

    @staticmethod
    def create_wallet_summary_crew(address):
        llm = ChatOllama(model="gemma2", base_url="http://localhost:11434")

        wallet_retriever = AIBTC_Agents.get_wallet_data_retriever_agent(llm)
        transaction_retriever = AIBTC_Agents.get_wallet_transactions_retriever_agent(
            llm
        )
        activity_analyzer = AIBTC_Agents.get_activity_analyzer_agent(llm)
        report_compiler = AIBTC_Agents.get_report_compiler_agent(llm)

        assigned_tasks = [
            AIBTC_Tasks.retrieve_wallet_info_task(wallet_retriever, address),
            AIBTC_Tasks.retrieve_transactions_task(transaction_retriever, address),
            AIBTC_Tasks.analyze_activity_task(activity_analyzer, address),
            AIBTC_Tasks.compile_report_task(report_compiler, address),
        ]

        return Crew(
            agents=[
                wallet_retriever,
                transaction_retriever,
                activity_analyzer,
                report_compiler,
            ],
            tasks=assigned_tasks,
            process=Process.sequential,
            memory=False,
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    @staticmethod
    def render_wallet_summary_crew():
        st.subheader("Wallet Summarizer")
        st.markdown(
            "This tool will analyze a wallet's activity and holdings on the Stacks blockchain."
        )

        with st.form("analysis_form"):
            address = st.text_input("Address", help="Enter the wallet address")
            submitted = st.form_submit_button("Analyze Wallet")

        if submitted and address:
            st.subheader("Analysis Progress")
            try:
                # TODO: refactor into same container, different formats
                # - step needs a title (AgentAction or return_values)
                # - task is the final output, where to get name? compare indices?

                # create containers for real-time updates
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                # reset callback lists
                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                crew = AIBTC_Crew.create_wallet_summary_crew(address)

                with st.spinner("Analyzing..."):
                    result = crew.kickoff()

                st.success("Analysis complete!")

                st.subheader("Analysis Results")

                result_str = str(result)
                st.markdown(result_str)

                st.download_button(
                    label="Download Analysis Report (Text)",
                    data=result_str,
                    file_name="smart_contract_analysis.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your inputs and try again.")
        else:
            st.info("Enter Wallet Address, then click 'Analyze Wallet' to see results.")
