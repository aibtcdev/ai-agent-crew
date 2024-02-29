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
            description="Get aiBTC from the faucet",
            agent=account_manager_agent,
        ),
        Task(
            description="Get the transaction status for the aiBTC faucet drip",
            agent=account_manager_agent
        ),
    ]
    resource_manager_tasks = [
        Task(
            description="Get our configured wallet address and remember to use it in later tasks.",
            agent=resource_manager_agent
        ),
        Task(
            description="Get our most recent payment data", agent=resource_manager_agent
        ),
        Task(
            description="Get the available resource data", agent=resource_manager_agent
        ),
        Task(description="Get our user data by using the address from wallet status", agent=resource_manager_agent),
        Task(
            description="Pay an invoice for a resource",
            agent=resource_manager_agent,
        ),
        Task(
            description="Get the transaction status for the invoice payment using the txid.",
            agent=resource_manager_agent
        ),
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
    print("Bitcoin Crew Final Result:")
    print(bitcoin_crew_result)
    print("--------------------------------------------------")


if __name__ == "__main__":
    engage_crew_with_tasks()
