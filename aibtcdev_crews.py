from crewai import Crew, Process


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
