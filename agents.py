from crewai import Agent
from textwrap import dedent
from tools.wallet import WalletTools
from tools.aibtc_token import AIBTCTokenTools
from tools.onchain_resources import OnchainResourcesTools
from tools.web_scraper import WebTools


class MeetingsCrew:
    @staticmethod
    def website_scraper(llm=None):
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
            allow_delegation=True,
            tools=[
                WebTools.scrape_reddit_url,
                WebTools.scrape_x_or_twitter_url,
                WebTools.scrape_generic_url,
            ],
        )

    @staticmethod
    def meeting_writer(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Writer",
            goal="Summarize the gathered information and always return results in markdown format.",
            backstory=(
                "You have a talent for distilling complex information into clear, concise"
                " summaries based on your belief in the future of Bitcoin and AI working together."
                " Your writing is both engaging and informative, making even the most intricate topics accessible to all."
            ),
            verbose=True,
            memory=True,
            tools=[],
            allow_delegation=True,
        )


class BitcoinCrew:

    @staticmethod
    def account_manager(llm=None):
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
            backstory=dedent(
                """\
        You are an account manager with the ability to interact with the Bitcoin and Stacks blockchain.
        Your job is to read the context and execute tasks using your tools to interact with the wallet.
        For any transaction sent, the transaction ID can be used to check the status of the transaction.
        """
            ),
            allow_delegation=False,
            verbose=True,
            **kwargs,
        )

    @staticmethod
    def resource_manager(llm=None):
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
            backstory=dedent(
                """\
        You are a resource manager with the ability to interact with on-chain resources.
        Your job is to read the context and execute tasks using your tools to interact with on-chain resources.
        """
            ),
            allow_delegation=False,
            verbose=True,
            **kwargs,
        )
