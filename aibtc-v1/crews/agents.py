from crewai import Agent
import subprocess
import os
from crews.tools import (
    AIBTCTokenTools,
    AIBTCResourceTools,
    StacksWalletTools,
    WebsiteTools,
)
# project_name="clarinet-project"


def createClarinetProject(project_name: str):
    try:
        # Create a new Clarinet project
        subprocess.run(["clarinet", "new", project_name], check=True)
        print(f"Successfully created project: {project_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating project '{project_name}': {e}")


def add_contract(project_name, contract_name, contract_code) -> str:
    """
    Add a new contract to the specified Clarinet project and write code into it.

    This tool allows users to create a new smart contract within a specified
    Clarinet project. It changes the current working directory to the project folder,
    creates a new contract file using the `clarinet contract new` command,
    and writes the provided contract code into that file.

    Args:
        project_name (str): The name of the Clarinet project folder.
        contract_name (str): The name of the contract to be created.
        contract_code (str): The code to be written into the new contract file.

    Returns:
        str: A message indicating the success or failure of the contract addition operation.
    """
    try:
        # Change directory to the project folder
        os.chdir(project_name)

        # Create a new contract
        subprocess.run(["clarinet", "contract", "new",
                       contract_name], check=True)
        print(f"Successfully added contract: {contract_name}")

        # Write the contract code to the contract file
        contract_file_path = os.path.join("contracts", f"{contract_name}.clar")
        with open(contract_file_path, "w") as contract_file:
            contract_file.write(contract_code)
        print(f"Successfully wrote code to contract: {contract_name}")

    except subprocess.CalledProcessError as e:
        print(f"Error adding contract '{contract_name}': {e}")
    finally:
        # Change back to the original directory
        os.chdir("..")


def check_contracts(project_name, contract_name=None):
    """Check the syntax of contracts in the specified Clarinet project."""
    try:
        # Change directory to the project folder
        os.chdir(project_name)

        if contract_name:
            # Check a specific contract
            subprocess.run(["clarinet", "check", contract_name], check=True)
            print(f"Successfully checked contract: {contract_name}")
        else:
            # Check all contracts
            subprocess.run(["clarinet", "check"], check=True)
            print("Successfully checked all contracts.")

    except subprocess.CalledProcessError as e:
        print(f"Error checking contracts: {e}")
    finally:
        # Change back to the original directory
        os.chdir("..")


@tool("Clarinet")
def runClarinet(contract_name: str, contract_code: str):
    project_name = "clarinet-project"
    createClarinetProject()
    add_contract(project_name, contract_name, contract_code)
    check_contracts(project_name)


def get_website_scraper(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Website Scraper",
        goal="Gather relevant information from the provided links. Be verbose, provide as much of the content and necessary context as possible.",
        backstory="You are a skilled website scraper, capable of extracting valuable information from the website code of any given source. Your expertise in web scraping allows you to gather data efficiently and accurately, providing valuable information for further analysis. You always use the correct tool for the job based on the URL provided.",
        verbose=True,
        memory=True,
        allow_delegation=False,
        tools=[WebsiteTools.scrape_x_or_twitter_url],
        **kwargs
    )


def get_meeting_writer(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Meeting Writer",
        goal="Summarize the gathered information and always return results in markdown format, adhering strictly to provided examples.",
        backstory="You have a talent for distilling complex information into clear, concise summaries. You ensure that all summaries adhere to the format provided in good examples, making the information accessible and engaging.",
        verbose=True,
        memory=True,
        allow_delegation=False,
        tools=[],
        **kwargs
    )


def get_wallet_account_manager(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Account Manager",
        goal="Read context and execute tasks using tools to interact with a configured wallet.",
        backstory="You are an account manager with the ability to interact with the Bitcoin and Stacks blockchain. Your job is to read the context and execute tasks using your tools to interact with the wallet. For any transaction sent, the transaction ID can be used to check the status of the transaction.",
        memory=True,
        tools=[
            StacksWalletTools.get_wallet_addresses,
            StacksWalletTools.get_wallet_status,
            StacksWalletTools.get_transaction_data,
            StacksWalletTools.get_transaction_status,
            AIBTCTokenTools.get_aibtc_balance,
            AIBTCTokenTools.get_faucet_drip,
        ],
        allow_delegation=False,
        verbose=True,
        **kwargs
    )


def get_onchain_resource_manager(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Resource Manager",
        goal="Read context and execute tasks using tools to interact with on-chain resources. Double check that all required arguments are included for the tools.",
        backstory="You are an expert in managing on-chain resources. You are able to read the context and execute tasks using your tools to interact with on-chain resources.",
        memory=True,
        tools=[
            AIBTCResourceTools.get_recent_payment_data,
            AIBTCResourceTools.get_resource_data,
            AIBTCResourceTools.get_user_data_by_address,
            AIBTCResourceTools.pay_invoice_for_resource,
        ],
        verbose=True,
        allow_delegation=False,
        **kwargs
    )


def get_transaction_manager(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Transaction Manager",
        goal="Manage Bitcoin and Stacks transactions and provide information.",
        backstory="You are an expert in managing transactions and understanding complex on-chain data.",
        memory=True,
        tools=[
            StacksWalletTools.get_transaction_data,
            StacksWalletTools.get_transaction_status,
        ],
        verbose=True,
        allow_delegation=False,
        **kwargs
    )
