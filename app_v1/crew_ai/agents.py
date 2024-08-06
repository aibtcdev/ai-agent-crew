from crewai import Agent
from crew_ai.tools import (
    AIBTCTokenTools,
    AIBTCResourceTools,
    StacksWalletTools,
    WebTools,
)


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
        tools=[WebTools.scrape_x_or_twitter_url],
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
    )


def get_transaction_manager(llm=None):
    kwargs = {}
    if llm is not None:
        kwargs["llm"] = llm

    return Agent(
        role="Transaction Manager",
        goal="Manage Bitcoin and Stacks transactions and provide information.",
        backstory="You are an expert in managing transactions and understanding complex on-chain data.",
        tools=[
            StacksWalletTools.get_transaction_data,
            StacksWalletTools.get_transaction_status,
        ],
        verbose=True,
        allow_delegation=False,
        memory=True,
    )
