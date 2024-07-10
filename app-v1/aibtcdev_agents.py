from crewai import Agent
from typing import Optional
from pydantic import Field
from aibtcdev_tools import AIBTCTokenTools, OnchainResourcesTools, WalletTools, WebTools


class WalletAgent(Agent):
    wallet_account_index: int = Field(..., description="Index of the wallet account")
    bitcoin_address: str = Field(..., description="Bitcoin address of the agent")
    stacks_address: str = Field(..., description="Stacks address of the agent")
    bns_name: Optional[str] = Field(
        None, description="BNS name of the agent (optional)"
    )

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def from_agent(
        cls,
        agent: Agent,
        wallet_account_index: int,
        bitcoin_address: str,
        stacks_address: str,
        bns_name: Optional[str] = None,
    ):
        """
        Create a WalletAgent instance from an existing Agent instance.
        """
        wallet_agent_data = agent.model_dump()
        wallet_agent_data.update(
            {
                "wallet_account_index": wallet_account_index,
                "bitcoin_address": bitcoin_address,
                "stacks_address": stacks_address,
                "bns_name": bns_name,
            }
        )
        return cls(**wallet_agent_data)


class MeetingsCrew:
    @staticmethod
    def get_website_scraper(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Website Scraper",
            goal="Gather relevant information from the provided links. Be verbose, provide as much of the content and necessary context as possible.",
            backstory=(
                "You are a skilled website scraper, capable of extracting valuable information from the website code of any given source."
                " Your expertise in web scraping allows you to gather data efficiently and accurately, providing valuable information for further analysis."
                " You always use the correct tool for the job based on the URL provided."
            ),
            verbose=True,
            memory=True,
            allow_delegation=False,
            tools=[
                WebTools.scrape_x_or_twitter_url,
            ],
            **kwargs
        )

    @staticmethod
    def get_meeting_writer(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Professional Writer",
            goal="Summarize the gathered information and always return results in markdown format, adhering strictly to provided examples.",
            backstory=(
                "You have a talent for distilling complex information into clear, concise summaries."
                " You ensure that all summaries adhere to the format provided in good examples, making the information accessible and engaging."
            ),
            verbose=True,
            memory=True,
            tools=[],
            allow_delegation=False,
            **kwargs
        )


class BitcoinCrew:
    @staticmethod
    def get_account_manager(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Account Manager",
            goal="Read context and execute tasks using tools to interact with a configured wallet.",
            memory=True,
            tools=[
                WalletTools.get_wallet_addresses,
                WalletTools.get_wallet_status,
                WalletTools.get_transaction_data,
                WalletTools.get_transaction_status,
                AIBTCTokenTools.get_aibtc_balance,
                AIBTCTokenTools.get_faucet_drip,
            ],
            backstory=(
                "You are an account manager with the ability to interact with the Bitcoin and Stacks blockchain."
                " Your job is to read the context and execute tasks using your tools to interact with the wallet."
                "For any transaction sent, the transaction ID can be used to check the status of the transaction."
            ),
            allow_delegation=False,
            verbose=True,
            **kwargs
        )

    @staticmethod
    def get_resource_manager(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Resource Manager",
            goal="Read context and execute tasks using tools to interact with on-chain resources. Double check that all required arguments are included for the tools.",
            memory=True,
            tools=[
                WalletTools.get_wallet_status,
                OnchainResourcesTools.get_recent_payment_data,
                OnchainResourcesTools.get_resource_data,
                OnchainResourcesTools.get_user_data_by_address,
                OnchainResourcesTools.pay_invoice_for_resource,
                AIBTCTokenTools.get_aibtc_balance,
                AIBTCTokenTools.get_faucet_drip,
            ],
            backstory=(
                "You are a resource manager with the ability to interact with on-chain resources."
                " Your job is to read the context and execute tasks using your tools to interact with on-chain resources."
            ),
            allow_delegation=False,
            verbose=True,
            **kwargs
        )

    @staticmethod
    def get_transaction_manager(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Transaction Manager",
            goal="Manage Bitcoin and Stacks transactions and provide information.",
            backstory="You are an expert in managing transactions and understanding complex on-chain data.",
            tools=[
                WalletTools.get_transaction_data,
                WalletTools.get_transaction_status,
            ],
            verbose=True,
            allow_delegation=False,
            memory=True,
            **kwargs
        )
