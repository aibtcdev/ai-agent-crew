import streamlit as st
from crewai import Agent, Task, Crew, Process
from typing import List
from utils.callbacks import crew_step_callback, crew_task_callback


class AIBTC_Crew:
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.agents: List[Agent] = []
        self.tasks: List[Task] = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def create_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder=st.session_state.embedder,
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    def render_crew(self):
        pass


def display_token_usage(token_usage):
    st.subheader("Token Usage")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tokens", token_usage.total_tokens)
        st.metric("Prompt Tokens", token_usage.prompt_tokens)
    with col2:
        st.metric("Completion Tokens", token_usage.completion_tokens)
        st.metric("Successful Requests", token_usage.successful_requests)
