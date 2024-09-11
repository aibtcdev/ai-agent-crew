from crewai import Agent, Task, Crew, Process
from typing import List
from utils.callbacks import crew_step_callback, crew_task_callback


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
