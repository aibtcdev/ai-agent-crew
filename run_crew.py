from crewai import Crew, Process, Task
from agents import BitcoinCrew

# set global vars
from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(True)


def engage_crew_with_tasks():
    # define agent
    wallet_agent = BitcoinCrew.wallet_agent()
    # define the tasks
    task_1 = Task(
        description="What wallet addresses do you have access to?",
        agent=wallet_agent,
    )
    task_2 = Task(
        description="What is the fourth address you have access to?",
        agent=wallet_agent,
    )
    task_3 = Task(
        description="What information do you know about the currently configured wallet?",
        agent=wallet_agent,
    )
    task_4 = Task(
        description="What is the aiBTC balance for your currently configured wallet?",
        agent=wallet_agent,
    )
    task_5 = Task(
        description="Summarize all tasks completed using a numbered list. This format is important. Each number should correspond to a summary of the task and result.",
        agent=wallet_agent,
    )
    # create a crew
    wallet_crew = Crew(
        agents=[wallet_agent],
        process=Process.sequential,
        tasks=[task_1, task_2, task_3, task_4, task_5],
        verbose=2,
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
