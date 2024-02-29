from crewai import Crew, Process, Task
from agents import BitcoinCrew
from textwrap import dedent

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)


def engage_crew_with_tasks():
    # define agents
    account_manager_agent = BitcoinCrew.account_manager()
    resource_manager_agent = BitcoinCrew.resource_manager()

    # define the tasks
    summary_task_desc = dedent(
        """\
        Summarize all tasks completed using a numbered list.
        This format is important. Each numbered list item will include:
        - the name of the agent that completed the task
        - a summary of the task and answer
        """
    )
    account_manger_tasks = [
        Task(
            description="What information do you know about the currently configured wallet?",
            agent=account_manager_agent,
        ),
        Task(
            description="What other wallet addresses do you have access to?",
            agent=account_manager_agent,
        ),
        Task(
            description="What is the aiBTC balance for your currently configured wallet?",
            agent=account_manager_agent,
        ),
        Task(
            description="Get aiBTC from the faucet and confirm the transaction status",
            agent=account_manager_agent,
        ),
        Task(description=summary_task_desc, agent=account_manager_agent),
    ]
    resource_manager_tasks = [
        Task(
            description="Get our most recent payment data", agent=resource_manager_agent
        ),
        Task(
            description="Get the available resource data", agent=resource_manager_agent
        ),
        Task(description="Get our user data by address", agent=resource_manager_agent),
        Task(
            description="Pay an invoice for a resource and confirm the transaction status",
            agent=resource_manager_agent,
        ),
        Task(description=summary_task_desc, agent=resource_manager_agent),
    ]

    # create a crew
    bitcoin_crew = Crew(
        agents=[account_manager_agent, resource_manager_agent],
        process=Process.sequential,
        tasks=account_manger_tasks + resource_manager_tasks,
        verbose=2,
    )

    # run the crew against all tasks
    bitcoin_crew_result = bitcoin_crew.kickoff()

    # print the result
    print("--------------------------------------------------")
    print("Bitcoin Crew Result:")
    print(bitcoin_crew_result)
    print("--------------------------------------------------")


if __name__ == "__main__":
    engage_crew_with_tasks()
