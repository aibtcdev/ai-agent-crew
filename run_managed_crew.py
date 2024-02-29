from crewai import Crew, Process, Task
from agents import BitcoinCrew
from textwrap import dedent

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI

manager_llm = ChatOpenAI(
    model="gpt-4-turbo-preview"
)

employee_llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125"
)

required_tasks = [
    Task(
          description="What information do you know about the currently configured wallet?",
      ),
      Task(
          description="What other wallet addresses do you have access to?",
      ),
      Task(
          description="What is the aiBTC balance for your currently configured wallet?",
      ),
      Task(
          description="Get aiBTC from the faucet",
      ),
      Task(
          description="Get the transaction status for the aiBTC faucet drip",
      ),
      Task(
          description="Get our configured wallet address and remember to use it in later tasks.",
      ),
      Task(
          description="Get our most recent payment data",
      ),
      Task(
          description="Get the available resource data",
      ),
      Task(description="Get our user data by using the address from wallet status"),
      Task(
          description="Pay an invoice for a resource",
      ),
      Task(
          description="Get the transaction status for the invoice payment using the txid.",
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
