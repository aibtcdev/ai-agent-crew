from crewai import Crew, Process, Task
from agents import BitcoinCrew
from textwrap import dedent

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI

default_llm = ChatOpenAI(
    # model="gpt-4-turbo-preview"
    model="gpt-3.5-turbo-0125"
)


def engage_crew_with_tasks():
    # define agents
    account_manager_agent = BitcoinCrew.account_manager()
    resource_manager_agent = BitcoinCrew.resource_manager()

    # define the tasks
    account_manger_tasks = [
        Task(
            description="What information do you know about the currently configured wallet?",
            agent=account_manager_agent,
            expected_output="The wallet address index, address, and nonce.",
        ),
        Task(
            description="What other wallet addresses do you have access to?",
            agent=account_manager_agent,
            expected_output="A list of wallet addresses organized by index.",
        ),
        Task(
            description="What is the aiBTC balance for your currently configured wallet?",
            agent=account_manager_agent,
            expected_output="The balance of aiBTC for the configured wallet.",
        ),
        Task(
            description="Get aiBTC from the faucet",
            agent=account_manager_agent,
            expected_output="The transaction ID for the aiBTC faucet drip.",
        ),
        Task(
            description="Get the transaction status for the aiBTC faucet drip",
            agent=account_manager_agent,
            expected_output="The status of the transaction for the aiBTC faucet drip.",
        ),
    ]
    resource_manager_tasks = [
        Task(
            description="Get our configured wallet address and remember to use it in later tasks.",
            agent=resource_manager_agent,
            expected_output="The wallet address for the configured wallet.",
        ),
        Task(
            description="Get our most recent payment data",
            agent=resource_manager_agent,
            expected_output="The most recent payment data for our address.",
        ),
        Task(
            description="Get the available resource data",
            agent=resource_manager_agent,
            expected_output="The available resources in the contract.",
        ),
        Task(
            description="Get our user data by using the address from wallet status",
            agent=resource_manager_agent,
            expected_output="The user data for the address from the contract.",
        ),
        Task(
            description="Pay an invoice for a resource",
            agent=resource_manager_agent,
            expected_output="The transaction ID for the invoice payment.",
        ),
        Task(
            description="Get the transaction status for the invoice payment using the txid.",
            agent=resource_manager_agent,
            expected_output="The status of the transaction for the invoice payment.",
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
