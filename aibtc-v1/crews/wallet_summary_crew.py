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
                You are a blockchain data analyst specializing in wallet activity on the Stacks blockchain. 
                You have access to various tools to retrieve detailed information about wallet addresses balance details.
                You excel at extracting meaningful insights and ensure accurate transaction details are provided.
                """
            ),
            verbose=True,
            **kwargs,
        )

    @staticmethod
    def get_wallet_transactions_retriever_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="transaction retriever",
            goal=dedent(
                """
            Retrieve, parse, and summarize transactions for the specified wallet. 
            Focus on providing a detailed analysis of the transaction data, including types, dates, events, and involved parties, without summarizing the structure. 
            Ensure the output is formatted correctly and is ready for use in further analysis or reporting.
            """
            ),
            tools=[StacksWalletTools.get_address_transactions],
            backstory=dedent(
                """
            You are an expert in blockchain transaction analysis with a deep understanding of the Stacks blockchain.
            Your primary task is to efficiently query and filter large datasets to retrieve transaction information.
            You excel at extract meaningful insights and ensure accurate transaction details are provided. 
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

    @staticmethod
    def get_activity_analyzer_agent(llm=None):
        # Modified implementation
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="activity interpreter",
            goal="Interpret wallet activities to provide meaningful insights into the wallet's behavior, purpose, and potential risks or opportunities.",
            tools=[],
            backstory=dedent(
                """
                You are a blockchain behavior analyst specializing in interpreting wallet activities on the Stacks blockchain.
                Your expertise lies in translating raw blockchain data into meaningful insights about wallet behavior,
                potential purposes, associated risks, and opportunities. You excel at contextualizing activities within
                the broader Stacks ecosystem.
            """
            ),
            verbose=True,
            **kwargs,
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
                You are a technical writer with expertise in creating clear and concise reports on complex blockchain topics in the Clarity language on the Stacks blockchain.
                You have access to various tools to gather data and compile it into a comprehensive report.
                """
            ),
            verbose=True,
            allow_delegation=False,
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

            Your response MUST be a `WalletInfo` JSON object that includes the following details:
            - **Wallet Address (`wallet_address`)**
            - **STX Balance (`stx_balance`)**
            - **NFT Holdings (`nft_holdings`)**
            - **FT Holdings (`ft_holdings`)**

            No additional information is required. Ensure the output is clear and suitable for use as context.
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

            Your task is to provide a summary of each transaction. For each transaction, include:
            - **Transaction ID (`tx_id`)**
            - **Type (`tx_type`)**: Indicate if it was a token transfer, smart contract interaction, etc.
            - **Date (`block_time_iso`)**
            - **Amount Sent (`stx_sent`)** and **Amount Received (`stx_received`)**
            - **Parties Involved:** 
              - **Sender (`sender_address`)**
              - **Recipient (`recipient_address` if applicable)**

            **Example Output:**
            - Transaction ID: 0x72bd82e96624c92da8f0ee3eafd355bc1bd1723d73256aba02a50323df95d437
            - Type: Smart Contract
            - Date: 2024-08-30T01:09:46.000Z
            - Amount Sent: 750000 STX
            - Amount Received: 0 STX
            - Parties Involved: Sender: SP2YJ47ZV5KT0XW31Z20YG7W108VECG8CGX8M6PM6

            Ensure your summary is clear and focuses on the actual data within the transactions. Do not describe or summarize the structure of the data itself.
            """
            ),
            expected_output="A summary of each transaction, including transaction ID, type, date, amount sent, amount received, and parties involved. Focus on content, not structure.",
            agent=agent,
        )

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

    @staticmethod
    def identify_patterns_task(agent, address, contexts):
        return Task(
            description=dedent(
                f"""
                Identify patterns and anomalies in the wallet activity for address: {address}
                
                Focus on:
                1. Recurring transaction patterns (e.g., regular transfers, contract interactions)
                2. Unusual or outlier activities
                3. Relationships with other addresses or contracts
                
                Provide a summary of the most significant patterns and any potential explanations for observed behaviors.
            """
            ),
            expected_output="A detailed summary of identified patterns, anomalies, and potential explanations for the wallet's behavior.",
            agent=agent,
            contexts=contexts,
        )

    @staticmethod
    def interpret_activity_task(agent, address, contexts):
        return Task(
            description=dedent(
                f"""
                Interpret the overall activity and purpose of the wallet: {address}
                
                Based on the data and patterns observed, provide insights on:
                1. The likely purpose or use case of this wallet (e.g., personal, business, trading)
                2. The level of activity and engagement with the Stacks ecosystem
                3. Potential risks or opportunities associated with this wallet's behavior
                4. Any notable interactions with known contracts or services on Stacks
                
                Offer a comprehensive interpretation that goes beyond raw data to explain the wallet's role and significance.
            """
            ),
            expected_output="An in-depth interpretation of the wallet's purpose, activity level, associated risks/opportunities, and significant interactions within the Stacks ecosystem.",
            agent=agent,
            contexts=contexts,
        )

    @staticmethod
    def compile_report_task(agent, address, contexts):
        return Task(
            description=dedent(
                f"""
                Compile a comprehensive final report for the wallet address: {address}
                
                The report should include:
                1. Executive Summary: A brief overview of the wallet's activity and key insights
                2. Wallet Info: Current balance, asset holdings, and recent transactions
                3. Historical Analysis: Trends and significant events in the wallet's history
                4. Pattern Recognition: Recurring behaviors and anomalies
                5. Activity Interpretation: Insights on the wallet's purpose, risks, and opportunities
                6. Conclusion: Overall assessment and potential future outlook
                
                Ensure the report is well-structured, easy to read, and provides valuable insights beyond raw data.
                Use markdown formatting for clarity and organization.
            """
            ),
            expected_output="A comprehensive, well-structured markdown report covering all aspects of the wallet analysis, including an executive summary, detailed findings, and concluding insights.",
            agent=agent,
            contexts=contexts,
        )


####################
# CREW(S)
####################


class AIBTC_Crew:

    @staticmethod
    def create_wallet_summary_crew(address):
        llm = st.session_state.llm

        wallet_retriever = AIBTC_Agents.get_wallet_data_retriever_agent(llm)
        transaction_retriever = AIBTC_Agents.get_wallet_transactions_retriever_agent(
            llm
        )
        pattern_recognizer = AIBTC_Agents.get_pattern_recognition_agent(llm)
        activity_analyzer = AIBTC_Agents.get_activity_analyzer_agent(llm)
        report_compiler = AIBTC_Agents.get_report_compiler_agent(llm)

        get_wallet_info_task = AIBTC_Tasks.retrieve_wallet_info_task(
            wallet_retriever, address
        )
        get_transactions_task = AIBTC_Tasks.retrieve_transactions_task(
            transaction_retriever, address
        )
        analyze_historical_data_task = AIBTC_Tasks.analyze_historical_data_task(
            pattern_recognizer, address
        )
        identify_patterns_task = AIBTC_Tasks.identify_patterns_task(
            pattern_recognizer,
            address,
            [get_wallet_info_task, get_transactions_task, analyze_historical_data_task],
        )
        interpret_activity_task = AIBTC_Tasks.interpret_activity_task(
            activity_analyzer,
            address,
            [
                get_wallet_info_task,
                get_transactions_task,
                analyze_historical_data_task,
                identify_patterns_task,
            ],
        )
        compile_report_task = AIBTC_Tasks.compile_report_task(
            report_compiler,
            address,
            [
                get_wallet_info_task,
                get_transactions_task,
                analyze_historical_data_task,
                identify_patterns_task,
                interpret_activity_task,
            ],
        )

        return Crew(
            agents=[
                wallet_retriever,
                transaction_retriever,
                pattern_recognizer,
                activity_analyzer,
                report_compiler,
            ],
            tasks=[
                get_wallet_info_task,
                get_transactions_task,
                analyze_historical_data_task,
                identify_patterns_task,
                interpret_activity_task,
                compile_report_task,
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
