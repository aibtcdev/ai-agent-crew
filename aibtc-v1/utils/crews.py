import streamlit as st
from crewai import Agent, Task, Crew, Process
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, create_model
from typing import Dict, List, Type
from utils.callbacks import crew_step_callback, crew_task_callback
from utils.llm import get_llm, load_env_vars


# dynamically create an input model for API endpoints
def create_input_model(class_name: str, fields: List[str]) -> Type[BaseModel]:
    return create_model(f"{class_name}Input", **{field: (str, ...) for field in fields})


# expected API output model
class CrewOutput(BaseModel):
    result: str
    token_usage: Dict[str, int]


# base class that defines the structure of a crew
class AIBTC_Crew:
    def __init__(self, name: str):
        self.name = name
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
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    def render_crew(self):
        pass

    def create_api_endpoint(self) -> APIRouter:
        router = APIRouter()

        CrewInput = create_input_model(self.__class__.__name__, self.get_task_inputs())

        @router.post(
            f"/{self.name.lower().replace(' ', '-')}", response_model=CrewOutput
        )
        async def run_crew(input_data: CrewInput):
            try:
                env_vars = load_env_vars()
                # llm = get_llm(
                #    env_vars.get("LLM_PROVIDER", "OpenAI"),
                #    env_vars.get("OPENAI_API_KEY", ""),
                #    env_vars.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
                #    env_vars.get("OPENAI_MODEL_NAME", "gpt-4o"),
                # )
                # temporary, testing with LiteLLM changes
                llm = "gpt-4o"
                self.setup_agents(llm)
                input_dict = input_data.dict()
                self.setup_tasks(**input_dict)
                crew = self.create_crew()
                result = crew.kickoff()
                return CrewOutput(
                    result=str(result.raw), token_usage=result.token_usage
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        return router


def display_token_usage(token_usage):
    st.subheader("Token Usage")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tokens", token_usage.total_tokens)
        st.metric("Prompt Tokens", token_usage.prompt_tokens)
    with col2:
        st.metric("Completion Tokens", token_usage.completion_tokens)
        st.metric("Successful Requests", token_usage.successful_requests)
