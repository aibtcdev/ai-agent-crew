import inspect
import streamlit as st
from crewai import Agent, Task
from crewai_tools import tool, Tool
from textwrap import dedent
from utils.crews import AIBTC_Crew, display_token_usage
import requests


# Custom Crew Class for Cryptocurrency Trading
class TradingAnalyzerCrew(AIBTC_Crew):
    def __init__(self):
        super().__init__("Trading Analyzer")

    def setup_agents(self, llm):
        # Agent for pulling market data
        market_data_agent = Agent(
            role="Market Data Retriever",
            goal="Collect historical and real-time price data for the specified cryptocurrency, broken down by Stacks block intervals. Ensure accuracy by retrieving prices from multiple DEXs and identifying anomalies.",
            tools=[
                AgentTools.get_crypto_price_history,
                AgentTools.get_all_swaps,
                AgentTools.get_pool_volume,
            ],
            backstory=(
                "You are a specialized market data retriever with access to various decentralized exchanges (DEXs). "
                "Your primary responsibility is to gather accurate historical and real-time price data, format it into structured datasets, "
                "and provide granular data at the Stacks block level to support trading strategy analysis."
            ),
            verbose=True,
            llm=llm,
        )
        self.add_agent(market_data_agent)

        # Agent for analyzing trading strategies
        strategy_analyzer_agent = Agent(
            role="Trading Strategy Analyzer",
            goal="Examine recent price trends and perform statistical analysis on historical data to identify optimal trading opportunities. "
            "Determine whether to hold, buy, or sell the given token based on moving averages, momentum indicators, and other predefined strategies.",
            tools=[],
            backstory=(
                "You are an expert in quantitative trading strategies, leveraging various models and indicators to interpret price movements. "
                "Your expertise lies in identifying patterns, calculating risk-reward ratios, and issuing trading recommendations based on a thorough analysis "
                "of the last 100 or more price points for the target cryptocurrency."
            ),
            verbose=True,
            llm=llm,
        )
        self.add_agent(strategy_analyzer_agent)

    def setup_tasks(self, crypto_symbol):
        # Task to retrieve historical price data
        retrieve_price_history_task = Task(
            description=f"Collect historical price data for {crypto_symbol} at a per-block level on the Stacks blockchain. "
            f"Data should include prices from at least one primary DEX (e.g., ALEX) and should cover the last 100 blocks.",
            expected_output=(
                "A structured dataset containing price history, including fields like block height, price and volume. The dataset should be free of gaps and anomalies, ensuring completeness for accurate analysis."
            ),
            agent=self.agents[0],  # market_data_agent
        )
        self.add_task(retrieve_price_history_task)

        # Task to analyze the price data with a trading strategy
        analyze_strategy_task = Task(
            description=f"Analyze the price history of {crypto_symbol} over the last 100 blocks to identify trading signals using predefined strategies. "
            f"Consider factors like price volatility, moving averages (e.g., 50-period and 100-period), and any unusual spikes or dips.",
            expected_output=(
                "A simple response saying buy, sell or hold. you can give a reason why."
            ),
            agent=self.agents[1],  # strategy_analyzer_agent
        )
        self.add_task(analyze_strategy_task)

    @staticmethod
    def get_task_inputs():
        return ["crypto_symbol"]

    @classmethod
    def get_all_tools(cls):
        return AgentTools.get_all_tools()

    def render_crew(self):
        st.subheader("Crypto Trading Analysis")
        st.markdown(
            "This tool will analyze cryptocurrency price history and provide trading signals."
        )

        with st.form("crypto_trading_form"):
            crypto_symbol = st.text_input(
                "Cryptocurrency Symbol",
                help="Enter the symbol of the cryptocurrency (e.g., BTC, ETH)",
            )
            submitted = st.form_submit_button("Analyze")

        if submitted and crypto_symbol:
            st.subheader("Analysis Progress")

            try:
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                llm = st.session_state.llm

                trading_class = TradingAnalyzerCrew()
                trading_class.setup_agents(llm)
                trading_class.setup_tasks(crypto_symbol)
                crypto_trading_crew = trading_class.create_crew()

                with st.spinner("Analyzing..."):
                    result = crypto_trading_crew.kickoff()

                st.success("Analysis complete!")

                # display_token_usage(result.token_usage)

                st.subheader("Analysis Results")

                # Display results
                result_str = str(result.raw)
                st.markdown(result_str)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please check your inputs and try again.")
        else:
            st.write(
                "Enter Cryptocurrency Symbol, then click 'Analyze' to see results."
            )


# Agent Tools
class AgentTools:
    @staticmethod
    @tool("Get Crypto Price History")
    def get_crypto_price_history(token_address: str):
        """Retrieve historical price data for a specified cryptocurrency symbol."""
        url = f"https://api.alexgo.io/v1/price_history/{token_address}?limit=100"
        headers = {
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            raise Exception(
                f"Failed to get token price history: {response.status_text}"
            )

        data = response.json()

        price_history = data.get("prices", [])
        formatted_history = "\n".join(
            f"Block Height: {price['block_height']}, Price: {price['avg_price_usd']}"
            for price in price_history
        )

        return f"Token: {data['token']}\n{formatted_history}"

    @staticmethod
    @tool("Get All Token Swaps and Token Info")
    def get_all_swaps():
        """Retrieve all swap data from the Alex API and return a formatted string."""
        url = "https://api.alexgo.io/v1/allswaps"
        headers = {
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            raise Exception(f"Failed to get all swaps: {response.status_text}")

        data = response.json()

        formatted_swaps = "\n---\n".join(
            dedent(
                f"""
            pool_id: {swap['id']}
            quote: {swap['quote']}
            symbol: {swap['quoteSymbol']}
            token_address: {swap['quoteId']}
            """
            ).strip()
            for swap in data
        )

        return formatted_swaps

    @staticmethod
    @tool("Get Token Pool Volume")
    def get_pool_volume(pool_token_id: str):
        """Retrieve pool volume data for a specified pool token ID."""
        url = f"https://api.alexgo.io/v1/pool_volume/{pool_token_id}?limit=100"
        headers = {
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            raise Exception(f"Failed to get pool volume: {response.status_text}")

        data = response.json()

        volume_values = data.get("volume_values", [])
        formatted_volume = "\n".join(
            f"Block Height: {volume['block_height']}, Volume: {volume['volume_24h']}"
            for volume in volume_values
        )

        return f"Token: {data['token']}\n{formatted_volume}"
