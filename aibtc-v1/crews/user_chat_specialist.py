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
from crews.clarity_code_generator_v2 import ClarityCodeGeneratorCrewV2
from utils.crews import AIBTC_Crew
from utils.scripts import get_pretty_timestamp


def truncate_text(text: str, max_length: int = 80):
    return text if len(text) <= max_length else f"{text[:max_length]}..."


def add_to_chat(speaker: str, message: str, subtask=False):
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({"role": speaker, "content": message})
    avatar = (
        "https://aibtc.dev/logos/aibtcdev-avatar-250px.png"
        if speaker == "assistant"
        else None
    )

    if subtask:
        with st.session_state.status_container:
            with st.chat_message(name=speaker, avatar=avatar):
                for line in message.split("\n"):
                    st.markdown(line)
    else:
        with st.session_state.chat_container:
            with st.chat_message(name=speaker, avatar=avatar):
                for line in message.split("\n"):
                    st.markdown(line)


def update_status(label: str, state: str = "running"):
    # state can be "running", "complete", "error"
    st.session_state.status_container.update(label=label)


def set_active_crew(crew_name: str):
    st.session_state.active_crew = crew_name


def chat_tool_callback(action: AgentAction):
    """Callback function to display any tool output from the crew."""
    update_status(
        f"[{st.session_state.active_crew}] Used tool: {action.tool}...", "running"
    )
    add_to_chat(
        "assistant",
        f"[{st.session_state.active_crew}]\n**Used tool:** {action.tool}\n**Tool input:**\n{action.tool_input}\n**Tool output:** *(truncated)*\n{truncate_text(action.result, 300)}",
        True,
    )


def chat_task_callback(task: TaskOutput):
    """Callback function to display any task output from the crew."""
    task_description = task.description
    task_name = getattr(
        task, "name", None
    )  # default to None if name attribute is not present
    computed_name = task_name if task_name else (truncate_text(task_description))
    update_status(
        f"[{st.session_state.active_crew}] Completed task: {computed_name}...",
        "running",
    )
    add_to_chat(
        "assistant",
        f"[{st.session_state.active_crew}]\n**Completed task:** {computed_name}",
        True,
    )


class UserChatSpecialistCrew(AIBTC_Crew):
    def __init__(self, embedder):
        super().__init__(
            "User Chat Specialist",
            "This crew is responsible for chat interactions with the user and providing support.",
            embedder,
        )

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


def render_crew():
    # setup and display initial instructions
    initial_instructions = st.empty()
    initial_instructions.markdown(
        dedent(
            """
            Welcome to AIBTC! Some ways to test my abilities:
            - Please analyze SP97M6Z0T8MHKJ6NZE0GS6TRERCG3GW1WVJ4NVGT.aibtcdev-airdrop-1
            - Tell me about the wallet SP97M6Z0T8MHKJ6NZE0GS6TRERCG3GW1WVJ4NVGT
            - Would you kindly analyze the trading strategy for WELSH?
            - Create a Clarity function that sums a list of three uints
            """
        )
    )

    # initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # intialize main chat container to hold chat messages and status messages
    st.session_state.full_chat_container = st.container()

    # create text input field for user at the bottom
    if user_input := st.chat_input("What would you like to do?"):

        # clear initial instructions
        initial_instructions.empty()
        # initialize chat and status container for updates
        with st.session_state.full_chat_container:
            st.session_state.chat_container = st.empty()
            st.session_state.chat_container = st.container()
            st.session_state.status_container = st.empty()
            st.session_state.status_container = st.status(label="Ready to assist!")

        # add user input to chat
        add_to_chat("user", user_input)
        # update status container
        update_status("Creating a plan and finding the right crew...", "running")

        # initialize the crew
        crew_class = UserChatSpecialistCrew(st.session_state.embedder)
        crew_class.setup_agents(st.session_state.llm)
        crew_class.setup_tasks(user_input)
        crew = crew_class.create_crew()
        crew.step_callback = chat_tool_callback
        crew.task_callback = chat_task_callback
        crew.planning = True

        # set active agent in state
        set_active_crew(crew_class.name)

        # kick off the crew (long-running)
        with st.session_state.status_container:
            result = crew.kickoff()

        # add crew's result to chat
        add_to_chat("assistant", result.raw)
        add_to_chat("assistant", "Is there anything else I can help you with?")

        # store chat history from messages in state
        st.session_state.chat_history.append(
            {"timestamp": get_pretty_timestamp(), "messages": st.session_state.messages}
        )
        # clear messages in state
        st.session_state.messages = []

    # show chat history in popover
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for chat in st.session_state.chat_history:
            with st.popover(f"Chat from {chat['timestamp']}"):
                # download chat as text file
                st.download_button(
                    label="Download Chat",
                    data="\n".join(
                        [
                            f"{message['role']}: {message['content']}"
                            for message in chat["messages"]
                        ]
                    ),
                    file_name=f"chat_{chat['timestamp']}-AIBTC.txt",
                    mime="text/plain",
                )
                # display chat messages
                for message in chat["messages"]:
                    role = message["role"]
                    content = message["content"]
                    avatar = (
                        "https://aibtc.dev/logos/aibtcdev-avatar-250px.png"
                        if role == "assistant"
                        else None
                    )
                    with st.chat_message(name=role, avatar=avatar):
                        for line in content.split("\n"):
                            st.markdown(line)


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
            crew_class = SmartContractAnalyzerV2(st.session_state.embedder)
            crew_class.setup_agents(st.session_state.llm)
            crew_class.setup_tasks(contract_identifier)
            crew = crew_class.create_crew()
            crew.step_callback = chat_tool_callback
            crew.task_callback = chat_task_callback
            crew.planning = True
            set_active_crew(crew_class.name)
            update_status(f"Executing {crew_class.name}...", "running")
            result = crew.kickoff()
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
            crew_class = WalletSummaryCrew(st.session_state.embedder)
            crew_class.setup_agents(st.session_state.llm)
            crew_class.setup_tasks(address)
            crew = crew_class.create_crew()
            crew.step_callback = chat_tool_callback
            crew.task_callback = chat_task_callback
            crew.planning = True
            set_active_crew(crew_class.name)
            update_status(f"Executing {crew_class.name}...", "running")
            result = crew.kickoff()
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
            crew_class = TradingAnalyzerCrew(st.session_state.embedder)
            crew_class.setup_agents(st.session_state.llm)
            crew_class.setup_tasks(crypto_symbol)
            crew = crew_class.create_crew()
            crew.step_callback = chat_tool_callback
            crew.task_callback = chat_task_callback
            crew.planning = True
            set_active_crew(crew_class.name)
            update_status(f"Executing {crew_class.name}...", "running")
            result = crew.kickoff()
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
            crew_class = ClarityCodeGeneratorCrewV2(st.session_state.embedder)
            crew_class.setup_agents(st.session_state.llm)
            crew_class.setup_tasks(user_input)
            crew = crew_class.create_crew()
            crew.step_callback = chat_tool_callback
            crew.task_callback = chat_task_callback
            crew.planning = True
            set_active_crew(crew_class.name)
            update_status(f"Executing {crew_class.name}...", "running")
            result = crew.kickoff()
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
