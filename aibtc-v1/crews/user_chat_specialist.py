import inspect
import streamlit as st
from crewai import Agent, Task
from crewai.agents.parser import AgentAction
from crewai.tasks.task_output import TaskOutput
from crewai_tools import tool, Tool
from textwrap import dedent
from crews.smart_contract_analyzer_v2 import SmartContractAnalyzerV2
from crews.wallet_summarizer import WalletSummaryCrew
from crews.trading_analyzer import TradingAnalyzerCrew
from crews.clarity_code_generator import ClarityCodeGeneratorCrew
from utils.crews import AIBTC_Crew
from utils.scripts import get_timestamp


def add_to_chat(speaker: str, message: str):
    st.session_state.messages.append({"role": speaker, "content": message})
    avatar = (
        "https://aibtc.dev/logos/aibtcdev-avatar-250px.png"
        if speaker == "assistant"
        else None
    )
    st.chat_message(name=speaker, avatar=avatar).markdown(message)


def chat_tool_callback(action: AgentAction):
    """Callback function to display any tool output from the crew."""
    add_to_chat(
        "assistant",
        f"**Used tool:** {action.tool} with input: {action.tool_input}",
    )
    add_to_chat(
        "assistant",
        f"**Result:** {action.result}",
    )


def chat_task_callback(task: TaskOutput):
    """Callback function to display any task output from the crew."""
    task_description = task.description
    task_name = getattr(
        task, "name", None
    )  # default to None if name attribute is not present
    computed_name = (
        task_name
        if task_name
        else (
            f"{task_description[:100]}..."
            if len(task_description) > 100
            else task_description
        )
    )
    add_to_chat(
        "assistant",
        f"**Completed task:** {computed_name}",
    )


class UserChatSpecialistCrew(AIBTC_Crew):
    def __init__(self):
        super().__init__("User Chat Specialist")
        self.description = "This crew is responsible for chat interactions with the user and providing support."

    def setup_agents(self, llm):
        chat_specialist = Agent(
            role="Chat Specialist",
            goal="You are responsible for interacting with the user and translating their query into an action.",
            backstory="You are trained to understand the user's query and provide the information they need with your tools, then analyzing the connection between the user's input and the result.",
            tools=AgentTools.get_all_tools(),
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
                The user is talking to you in chat format. You are tasked with reviewing the user's input and taking 1 of 2 actions:
                1. If the user's input is a question without a task, do not execute a crew and clearly answer the question.
                2. If the user's input is a task, use the appropriate tool to execute the task and summarize the result.
                ### User Input
                {user_input}
                """
            ),
            expected_output="The appropriate action has been taken.",
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
        initial_instructions = st.empty()
        initial_instructions.markdown(
            dedent(
                """
                Welcome to AIBTC! Some ways to test my abilities:
                - Please analyze SP97M6Z0T8MHKJ6NZE0GS6TRERCG3GW1WVJ4NVGT.aibtcdev-airdrop-1
                - Tell me about the wallet SP97M6Z0T8MHKJ6NZE0GS6TRERCG3GW1WVJ4NVGT
                - Would you kindly analyze the trading strategy for WELSH?
                """
            )
        )
        if user_input := st.chat_input("What would you like to do?"):
            initial_instructions.empty()
            add_to_chat("user", user_input)
            self.setup_agents(st.session_state.llm)
            self.setup_tasks(user_input)
            crew_instance = self.create_crew()
            crew_instance.step_callback = chat_tool_callback
            crew_instance.task_callback = chat_task_callback
            with st.status("Thinking..."):
                result = crew_instance.kickoff()
            add_to_chat("assistant", result)
            add_to_chat("assistant", "Is there anything else I can help you with?")


#########################
# Agent Tools
#########################


class AgentTools:
    @staticmethod
    @tool("Execute Smart Contract Analyzer Crew")
    def execute_smart_contract_analyzer_crew(contract_identifier: str):
        """Execute the Smart Contract Analyzer Crew to give a comprehensive review of a provided smart contract."""
        try:
            if isinstance(contract_identifier, dict):
                contract_identifier = contract_identifier.get("contract_identifier", "")
            smart_contract_analyzer_crew_class = SmartContractAnalyzerV2()
            smart_contract_analyzer_crew_class.setup_agents(st.session_state.llm)
            smart_contract_analyzer_crew_class.setup_tasks(contract_identifier)
            smart_contract_analyzer_crew = (
                smart_contract_analyzer_crew_class.create_crew()
            )
            smart_contract_analyzer_crew.step_callback = chat_tool_callback
            smart_contract_analyzer_crew.task_callback = chat_task_callback
            result = smart_contract_analyzer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Smart Contract Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Wallet Analyzer Crew")
    def execute_wallet_analyzer_crew(address: str):
        """Execute the Wallet Analyzer Crew to give a comprehensive review of a provided wallet address."""
        try:
            # check if address is json param and extract value
            if isinstance(address, dict):
                address = address.get("address", "")
            wallet_summarizer_crew_class = WalletSummaryCrew()
            wallet_summarizer_crew_class.setup_agents(st.session_state.llm)
            wallet_summarizer_crew_class.setup_tasks(address)
            wallet_summarizer_crew = wallet_summarizer_crew_class.create_crew()
            wallet_summarizer_crew.step_callback = chat_tool_callback
            wallet_summarizer_crew.task_callback = chat_task_callback
            result = wallet_summarizer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Wallet Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Trading Analyzer Crew")
    def execute_trading_analyzer_crew(crypto_symbol: str):
        """Execute the Trading Analyzer Crew to give a comprehensive review of a provided trading strategy."""
        try:
            if isinstance(crypto_symbol, dict):
                crypto_symbol = crypto_symbol.get("crypto_symbol", "")
            trading_analyzer_crew_class = TradingAnalyzerCrew()
            trading_analyzer_crew_class.setup_agents(st.session_state.llm)
            trading_analyzer_crew_class.setup_tasks(crypto_symbol)
            trading_analyzer_crew = trading_analyzer_crew_class.create_crew()
            trading_analyzer_crew.step_callback = chat_tool_callback
            trading_analyzer_crew.task_callback = chat_task_callback
            result = trading_analyzer_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Trading Analyzer Crew: {e}"

    @staticmethod
    @tool("Execute Clarity Code Generator Crew")
    def execute_clarity_code_generator_crew(user_input: str):
        """Execute the Clarity Code Generator Crew to generate Clarity code for a provided smart contract."""
        try:
            if isinstance(user_input, dict):
                user_input = user_input.get("user_input", "")
            clarity_code_generator_crew_class = ClarityCodeGeneratorCrew()
            clarity_code_generator_crew_class.setup_agents(st.session_state.llm)
            clarity_code_generator_crew_class.setup_tasks(user_input)
            clarity_code_generator_crew = (
                clarity_code_generator_crew_class.create_crew()
            )
            clarity_code_generator_crew.step_callback = chat_tool_callback
            clarity_code_generator_crew.task_callback = chat_task_callback
            result = clarity_code_generator_crew.kickoff()
            return result
        except Exception as e:
            return f"Error executing Clarity Code Generator Crew: {e}"

    @staticmethod
    @tool("List all past chat messages")
    def get_all_past_messages():
        """Get all past chat messages between you and the user for context."""
        return st.session_state.messages

    @staticmethod
    @tool("List all available agent tools")
    def get_all_available_tools():
        """Get all available tools you have access to in order to assist the user."""
        # make an array of {name: tool_name, description: tool_description}
        tools = []
        for tool in AgentTools.get_all_tools():
            tools.append({"name": tool.name, "description": tool.description})
        return tools

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
