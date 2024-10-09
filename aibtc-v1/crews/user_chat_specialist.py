import inspect
import os
import streamlit as st
import subprocess
from crewai import Agent, Task
from crewai_tools import tool, Tool
from run_clarinet import ClarinetExecutor
from textwrap import dedent
from utils.crews import AIBTC_Crew, display_token_usage
from utils.scripts import get_timestamp


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
        None
        # TODO: setup tools
        # return AgentTools.get_all_tools()

    def render_crew(self):
        st.text(st.session_state.crew_mapping)
