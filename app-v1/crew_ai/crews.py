from crewai import Crew, Process
from .decorators import ui_class, ui_method


@ui_class("Analysis Crew")
class AnalysisCrew:
    @staticmethod
    @ui_method("Get Analysis Crew")
    def get_analysis_crew(agents, tasks):
        return Crew(
            agents=[agents["Data Analyst"], agents["Report Writer"]],
            tasks=[],  # Tasks would need to be added separately
            process=Process.sequential,
            verbose=2,
        )


def get_wallet_crew(agents, tasks):
    return Crew(
        agents=[agents["Wallet Manager"]],
        tasks=[
            tasks["Get Wallet Status"],
            tasks["Get aiBTC Balance"],
            tasks["Get aiBTC Faucet Drip"],
        ],
        process=Process.sequential,
        verbose=2,
    )


def get_resource_crew(agents, tasks):
    return Crew(
        agents=[agents["Resource Manager"]],
        tasks=[tasks["Get Resource Data"]],
        process=Process.sequential,
        verbose=2,
    )
