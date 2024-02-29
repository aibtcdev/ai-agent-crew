from crewai import Agent
from textwrap import dedent
from tools.wallet import WalletTools
from tools.aibtc import aiBTCTools
from tools.resources_v2 import StacksM2MTools


class BitcoinCrew:
    @staticmethod
    def account_manager():
        return Agent(
            role="Account Manager",
            goal="Read context and execute tasks using tools to interact with a configured wallet.",
            memory=True,
            tools=[
                WalletTools.get_wallet_addresses,
                WalletTools.get_wallet_status,
                WalletTools.get_transaction_data,
                WalletTools.get_transaction_status,
                aiBTCTools.get_aibtc_balance,
                aiBTCTools.get_faucet_drip,
            ],
            backstory=dedent(
                """\
        You are an account manager with the ability to interact with the Bitcoin and Stacks blockchain.
        Your job is to read the context and execute tasks using your tools to interact with the wallet.
        If you send a transaction, you can always check it's status or get more info with the transaction ID.
        """
            ),
            allow_delegation=False,
            verbose=True,
        )

    @staticmethod
    def resource_manager():
        return Agent(
            role="Resource Manager",
            goal="Read context and execute tasks using tools to interact with on-chain resources.",
            memory=True,
            tools=[
                StacksM2MTools.get_recent_payment_data,
                StacksM2MTools.get_resource_data,
                StacksM2MTools.get_user_data_by_address,
                StacksM2MTools.pay_invoice_for_resource,
            ],
            backstory=dedent(
                """\
        You are a resource manager with the ability to interact with the Stacks M2M resources.
        These resources are on-chain and you can interact with them using your tools.
        Your job is to read the context and execute tasks using your tools to interact with resources.
        """
            ),
            allow_delegation=False,
            verbose=True,
        )
