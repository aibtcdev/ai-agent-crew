import inspect
import os
import streamlit as st
import subprocess
from crewai import Agent, Task
from crewai_tools import tool, Tool
from run_clarinet import ClarinetExecutor
from textwrap import dedent
from crews.smart_contract_analyzer_v2 import SmartContractAnalyzerV2
from crews.wallet_summarizer import WalletSummaryCrew
from crews.trading_analyzer import TradingAnalyzerCrew
from crews.clarity_code_generator import ClarityCodeGeneratorCrew
from utils.crews import AIBTC_Crew, display_token_usage
from utils.scripts import get_timestamp


def add_to_chat(speaker: str, message: str):
    st.session_state.messages.append({"role": speaker, "content": message})


def handle_user_input(user_input):
    add_to_chat("bot", f"Let me check that for you, you said:\n\n{user_input}")


class UserChatSpecialistCrew(AIBTC_Crew):
    def __init__(self):
        super().__init__("User Chat Specialist")
        self.description = "This crew is responsible for chat interactions with the user and providing support."

    def setup_agents(self, llm):
        chat_specialist = Agent(
            role="Chat Specialist",
            goal="This agent is responsible for chat interactions with the user and providing support.",
            backstory="This agent is trained to provide support to users through chat interactions and available tools.",
            verbose=True,
            memory=False,
            allow_delegation=True,
            llm=llm,
        )
        self.add_agent(chat_specialist)

    def setup_tasks(self, user_input):
        review_user_input = Task(
            name="Review User Input",
            description=dedent(
                f"""
                Review the user's input and determine the appropriate response.",
                If you are going to run a crew for the user then use one of your tools with the required input(s).",
                User Input:\n{user_input}""",
            ),
            expected_output="The appropriate response to the user's input.",
            agent=self.agents[0],  # chat_specialist
        )
        self.add_task(review_user_input)

    @staticmethod
    def get_task_inputs():
        return ["user_input"]

    @classmethod
    def get_all_tools(cls):
        return AgentTools.get_all_tools()

    def render_crew(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input("What would you like to do?"):
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = (
                f"Echoing back your input:\n\n{user_input}\n\n{self.get_all_tools()}"
            )
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


#########################
# Agent Tools
#########################


class AgentTools:
    @staticmethod
    @tool("Execute Smart Contract Analyzer Crew")
    def execute_smart_contract_analyzer_crew(user_input: str):
        """Execute the Smart Contract Analyzer Crew to give a comprehensive review of a provided smart contract."""
        try:
            smart_contract_analyzer_crew_class = SmartContractAnalyzerV2()
            smart_contract_analyzer_crew_class.setup_agents(st.session_state.llm)
            smart_contract_analyzer_crew_class.setup_tasks(user_input)
            smart_contract_analyzer_crew = (
                smart_contract_analyzer_crew_class.create_crew()
            )
            result = smart_contract_analyzer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Smart Contract Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Wallet Analyzer Crew")
    def execute_wallet_analyzer_crew(user_input: str):
        """Execute the Wallet Analyzer Crew to give a comprehensive review of a provided blockchain wallet."""
        try:
            wallet_summarizer_crew_class = WalletSummaryCrew()
            wallet_summarizer_crew_class.setup_agents(st.session_state.llm)
            wallet_summarizer_crew_class.setup_tasks(user_input)
            wallet_summarizer_crew = wallet_summarizer_crew_class.create_crew()
            result = wallet_summarizer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Wallet Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Trading Analyzer Crew")
    def execute_trading_analyzer_crew(user_input: str):
        """Execute the Trading Analyzer Crew to give a comprehensive review of a provided trading strategy."""
        try:
            trading_analyzer_crew_class = TradingAnalyzerCrew()
            trading_analyzer_crew_class.setup_agents(st.session_state.llm)
            trading_analyzer_crew_class.setup_tasks(user_input)
            trading_analyzer_crew = trading_analyzer_crew_class.create_crew()
            result = trading_analyzer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Trading Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Clarity Code Generator Crew")
    def execute_clarity_code_generator_crew(user_input: str):
        """Execute the Clarity Code Generator Crew to generate Clarity code for a provided smart contract."""
        try:
            clarity_code_generator_crew_class = ClarityCodeGeneratorCrew()
            clarity_code_generator_crew_class.setup_agents(st.session_state.llm)
            clarity_code_generator_crew_class.setup_tasks(user_input)
            clarity_code_generator_crew = (
                clarity_code_generator_crew_class.create_crew()
            )
            result = clarity_code_generator_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Clarity Code Generator Crew: {e}"

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
