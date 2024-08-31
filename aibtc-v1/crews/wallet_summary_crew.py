import requests
import streamlit as st
import time
from crewai import Agent, Crew, Process, Task
from crewai_tools import tool
from textwrap import dedent
from utils.session import crew_step_callback, crew_task_callback
from .tools import StacksWalletTools


####################
# AGENTS
####################


class AIBTC_Agents:

    @staticmethod
    def get_wallet_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="wallet data and transaction retriever",
            goal=dedent(
                """
                Retrieve basic wallet information and summarize transactions for the specified wallet. 
                Focus on providing a detailed analysis of the wallet balance and transaction data, including types, dates, events, and involved parties. 
                Ensure the output is formatted correctly and is ready for use in further analysis or reporting.
                """
            ),
            tools=[
                StacksWalletTools.get_address_balance_detailed,
                StacksWalletTools.get_address_transactions,
            ],
            backstory=dedent(
                """
                You are a blockchain data analyst specializing in wallet activity on the Stacks blockchain. 
                You have access to various tools to retrieve detailed information about wallet addresses balance details and transactions.
                You excel at extracting meaningful insights and ensure accurate transaction details are provided. 
                Focus on the data within transactions, summarizing key details such as transaction types, dates, events, and involved parties.
                """
            ),
            verbose=True,
            **kwargs,
        )

    @staticmethod
    def get_pattern_recognition_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="pattern recognition specialist",
            goal="Identify recurring patterns, unusual activities, and long-term trends in wallet behavior.",
            tools=[],  # Add relevant tools
            backstory=dedent(
                """
                You are an expert in blockchain data analysis with a keen eye for patterns and anomalies.
                Your specialty is in recognizing recurring behaviors, identifying unusual activities, and
                spotting long-term trends in wallet usage on the Stacks blockchain.
            """
            ),
            verbose=True,
            **kwargs,
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
            Retrieve detailed wallet balance information for the specified address.

            **Address:** {address}

            Ensure the output is clear and suitable for use as context.
            """
            ),
            expected_output="The only fields should be returned wallet address, STX balance, NFT holdings, and FT holdings. Simplified for context usage.",
            agent=agent,
        )

    # retrieve_transactions_task
    @staticmethod
    def retrieve_transactions_task(agent, address):
        return Task(
            description=dedent(
                f"""
                Retrieve the last transactions associated with the following address:

                **Address:** {address}

                Ensure your summary is clear and focuses on the actual data within the transactions. Do not describe or summarize the structure of the data itself.
                """
            ),
            expected_output=dedent(
                """
                A summary of each transaction, including:
                - Transaction Status
                - Sender Address
                - Block Time (ISO format)
                - Transaction Type
                - Contract Name (if applicable)
                - Function Name (if applicable)
                - Recipient Address (if applicable)
                - MicroSTX Sent
                - MicroSTX Received

                Focus on content, not structure.
                """
            ),
            agent=agent,
        )

    # analyze_historical_data_task
    @staticmethod
    def analyze_historical_data_task(agent, address):
        return Task(
            description=dedent(
                f"""
                Analyze the historical data for the wallet address: {address}
                
                Your analysis should include:
                1. Trends in transaction frequency and volume over time
                2. Changes in asset holdings (STX, NFTs, FTs) over time
                3. Significant events or turning points in the wallet's history
                
                Provide insights on how the wallet's usage has evolved and any notable patterns observed.
            """
            ),
            expected_output="A comprehensive analysis of historical trends, including transaction patterns, asset holding changes, and significant events in the wallet's history.",
            agent=agent,
        )


####################
# CREW(S)
####################


class AIBTC_Crew:

    @staticmethod
    def create_wallet_summary_crew(address):
        llm = st.session_state.llm

        wallet_agent = AIBTC_Agents.get_wallet_agent(llm)
        pattern_recognizer = AIBTC_Agents.get_pattern_recognition_agent(llm)

        get_wallet_info_task = AIBTC_Tasks.retrieve_wallet_info_task(
            wallet_agent, address
        )
        get_transactions_task = AIBTC_Tasks.retrieve_transactions_task(
            wallet_agent, address
        )
        analyze_historical_data_task = AIBTC_Tasks.analyze_historical_data_task(
            pattern_recognizer, address
        )

        return Crew(
            agents=[
                wallet_agent,
                pattern_recognizer,
            ],
            tasks=[
                get_wallet_info_task,
                get_transactions_task,
                analyze_historical_data_task,
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    @staticmethod
    def render_wallet_summary_crew():
        st.subheader("Wallet Summarizer")
        st.markdown(
            "This tool will analyze a wallet's activity and holdings on the Stacks blockchain."
        )

        with st.form("wallet_summary_form"):
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
