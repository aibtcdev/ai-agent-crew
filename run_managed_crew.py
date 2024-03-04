from crewai import Crew, Process, Task
from agents import BitcoinCrew

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI

manager_llm = ChatOpenAI(model="gpt-4-turbo-preview")

employee_llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

required_tasks = [
    Task(
        description="What information do you know about the currently configured wallet?",
        expected_output="The wallet address index, address, and nonce.",
    ),
    Task(
        description="What other wallet addresses do you have access to?",
        expected_output="A list of wallet addresses organized by index.",
    ),
    Task(
        description="What is the aiBTC balance for your currently configured wallet?",
        expected_output="The balance of aiBTC for the configured wallet.",
    ),
    Task(
        description="Get aiBTC from the faucet",
        expected_output="The transaction ID for the aiBTC faucet drip.",
    ),
    Task(
        description="Get the transaction status for the aiBTC faucet drip",
        expected_output="The status of the transaction for the aiBTC faucet drip.",
    ),
    Task(
        description="Get our configured wallet address and remember to use it in later tasks.",
        expected_output="The wallet address for the configured wallet.",
    ),
    Task(
        description="Get our most recent payment data",
        expected_output="The most recent payment data for the configured wallet.",
    ),
    Task(
        description="Get the available resource data",
        expected_output="The available resources for the configured wallet.",
    ),
    Task(
        description="Get our user data by using the address from wallet status",
        expected_output="The user data for the address from the contract.",
    ),
    Task(
        description="Pay an invoice for a resource",
        expected_output="The transaction ID for the invoice payment.",
    ),
    Task(
        description="Get the transaction status for the invoice payment using the txid.",
        expected_output="The status of the transaction for the invoice payment.",
    ),
]


def engage_crew_with_tasks():
    # define agents
    account_manager_agent = BitcoinCrew.account_manager(llm=employee_llm)
    resource_manager_agent = BitcoinCrew.resource_manager(llm=employee_llm)

    # create a crew
    bitcoin_crew = Crew(
        agents=[account_manager_agent, resource_manager_agent],
        process=Process.hierarchical,
        manager_llm=manager_llm,
        tasks=required_tasks,
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
