import inspect
import streamlit as st
from crewai import Agent, Task
from crewai_tools import tool, Tool
from textwrap import dedent
from utils.crews import AIBTC_Crew, display_token_usage
from utils.scripts import BunScriptRunner, get_timestamp


class WalletSummaryCrew(AIBTC_Crew):
    def __init__(self, embedder):
        super().__init__(
            "Wallet Summarizer",
            "This crew analyzes a wallet's activity and holdings on the Stacks blockchain.",
            embedder,
        )

    def setup_agents(self, llm):
        wallet_agent = Agent(
            role="Wallet Data and Transaction Retriever",
            goal=dedent(
                """
                Retrieve basic wallet information and summarize transactions for the specified wallet. 
                Focus on providing a detailed analysis of the wallet balance and transaction data, including types, dates, events, and involved parties. 
                Ensure the output is formatted correctly and is ready for use in further analysis or reporting.
                """
            ),
            tools=[
                AgentTools.get_address_balance_detailed,
                AgentTools.get_address_transactions,
                AgentTools.get_bns_address,
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
            llm=llm,
        )
        self.add_agent(wallet_agent)

        pattern_recognizer = Agent(
            role="Pattern Recognition Specialist",
            goal="Identify recurring patterns, unusual activities, and long-term trends in wallet behavior.",
            tools=[],
            backstory=dedent(
                """
                You are an expert in blockchain data analysis with a keen eye for patterns and anomalies.
                Your specialty is in recognizing recurring behaviors, identifying unusual activities, and
                spotting long-term trends in wallet usage on the Stacks blockchain.
                """
            ),
            verbose=True,
            llm=llm,
        )
        self.add_agent(pattern_recognizer)

    def setup_tasks(self, address):
        retrieve_wallet_info_task = Task(
            description=dedent(
                f"""
                Retrieve detailed wallet balance information for the specified address.

                **Address:** {address}

                Ensure the output is clear and suitable for use as context.
                """
            ),
            expected_output="The only fields should be returned wallet address, STX balance, NFT holdings, and FT holdings. Simplified for context usage.",
            agent=self.agents[0],  # wallet_agent
        )
        self.add_task(retrieve_wallet_info_task)

        retrieve_transactions_task = Task(
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
            agent=self.agents[0],  # wallet_agent
        )
        self.add_task(retrieve_transactions_task)

        analyze_historical_data_task = Task(
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
            agent=self.agents[1],  # pattern_recognizer
        )
        self.add_task(analyze_historical_data_task)

    @staticmethod
    def get_task_inputs():
        return ["address"]

    @classmethod
    def get_all_tools(cls):
        return AgentTools.get_all_tools()

    def render_crew(self):
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
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                llm = st.session_state.llm

                wallet_summary_crew_class = WalletSummaryCrew()
                wallet_summary_crew_class.setup_agents(llm)
                wallet_summary_crew_class.setup_tasks(address)
                wallet_summary_crew = wallet_summary_crew_class.create_crew()

                with st.spinner("Analyzing..."):
                    result = wallet_summary_crew.kickoff()

                st.success("Analysis complete!")

                display_token_usage(result.token_usage)

                st.subheader("Analysis Results")

                result_str = str(result.raw)
                st.markdown(result_str)

                timestamp = get_timestamp()

                st.download_button(
                    label="Download Analysis Report (Text)",
                    data=result_str,
                    file_name=f"{timestamp}_wallet_summary_analysis.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please check your inputs and try again.")
        else:
            st.write(
                "Enter Wallet Address, then click 'Analyze Wallet' to see results."
            )


#########################
# Agent Tools
#########################


class AgentTools:

    @staticmethod
    @tool("Get Address Balance Detailed")
    def get_address_balance_detailed(address: str):
        """Get detailed balance information for a given address."""
        # helper if address is sent as json
        if isinstance(address, dict) and "address" in address:
            address = address["address"]
        return BunScriptRunner.bun_run(
            "stacks-wallet", "get-address-balance-detailed.ts", address
        )

    @staticmethod
    @tool("Get Address Transactions")
    def get_address_transactions(address: str):
        """Get 20 most recent transactions for a given address."""
        # helper if address is sent as json
        if isinstance(address, dict) and "address" in address:
            address = address["address"]
        return BunScriptRunner.bun_run(
            "stacks-wallet", "get-transactions-by-address.ts", address
        )

    @staticmethod
    @tool("Translate BNS Name to Address")
    def get_bns_address(name: str):
        """Get the address that is tied to a bns name."""
        return BunScriptRunner.bun_run("stacks-bns", "get-address-by-bns.ts", name)

    @classmethod
    def get_all_tools(cls):
        members = inspect.getmembers(cls)
        tools = [
            member
            for name, member in members
            if isinstance(member, Tool)
            or (hasattr(member, "__wrapped__") and isinstance(member.__wrapped__, Tool))
        ]
        return tools
