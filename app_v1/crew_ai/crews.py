from crewai import Crew, Process
from .decorators import ui_class, ui_method


def get_agent(agents, role):
    return agents.get(role, None)


def get_task(tasks, task_name):
    return tasks.get(task_name, None)


@ui_class("Analysis Crew")
class AnalysisCrew:
    @staticmethod
    @ui_method("Get Analysis Crew")
    def get_analysis_crew(agents, tasks):
        required_agents = ["Data Analyst", "Report Writer"]
        crew_agents = [get_agent(agents, role) for role in required_agents]

        if None in crew_agents:
            missing_agents = [
                role
                for role, agent in zip(required_agents, crew_agents)
                if agent is None
            ]
            raise ValueError(
                f"Missing required agents for Analysis Crew: {', '.join(missing_agents)}"
            )

        return Crew(
            agents=crew_agents,
            tasks=[],  # Tasks would need to be added separately
            process=Process.sequential,
            verbose=2,
        )


@ui_class("Stacks Wallet Crew")
class StacksWalletCrew:
    @staticmethod
    @ui_method("Get Wallet Crew")
    def get_wallet_crew(agents, tasks):
        wallet_manager = get_agent(agents, "Wallet Manager")
        if wallet_manager is None:
            raise ValueError("Missing required agent for Wallet Crew: Wallet Manager")

        required_tasks = [
            "Get Wallet Status",
            "Get aiBTC Balance",
            "Get aiBTC Faucet Drip",
        ]
        crew_tasks = [get_task(tasks, task_name) for task_name in required_tasks]

        if None in crew_tasks:
            missing_tasks = [
                task for task, t in zip(required_tasks, crew_tasks) if t is None
            ]
            raise ValueError(
                f"Missing required tasks for Wallet Crew: {', '.join(missing_tasks)}"
            )

        return Crew(
            agents=[wallet_manager],
            tasks=crew_tasks,
            process=Process.sequential,
            verbose=2,
        )

    @staticmethod
    @ui_method("Get Resource Crew")
    def get_resource_crew(agents, tasks):
        resource_manager = get_agent(agents, "Resource Manager")
        if resource_manager is None:
            raise ValueError(
                "Missing required agent for Resource Crew: Resource Manager"
            )

        get_resource_data_task = get_task(tasks, "Get Resource Data")
        if get_resource_data_task is None:
            raise ValueError(
                "Missing required task for Resource Crew: Get Resource Data"
            )

        return Crew(
            agents=[resource_manager],
            tasks=[get_resource_data_task],
            process=Process.sequential,
            verbose=2,
        )
