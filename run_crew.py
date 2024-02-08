from crewai import Crew, Process, Task
from agents import BitcoinCrew


def engage_crew_with_tasks():
    # define agent
    wallet_agent = BitcoinCrew.wallet_agent()
    # define the tasks
    task_1 = Task(
        description="Get the addresses of the configured wallet.",
        agent=wallet_agent,
    )
    task_2 = Task(
        description="Get information about the configured wallet.",
        agent=wallet_agent,
    )
    # create a crew
    wallet_crew = Crew(
        agents=[wallet_agent],
        process=Process.sequential,
        tasks=[task_1, task_2],
        verbose=True,
    )
    # run the crew
    wallet_result = wallet_crew.kickoff()
    # print the result
    print("--------------------------------------------------")
    print("Wallet Crew Result:")
    print(wallet_result)
    print("--------------------------------------------------")


if __name__ == "__main__":
    engage_crew_with_tasks()
