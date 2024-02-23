from crewai import Agent
from textwrap import dedent
from tools.bun_run import BunScriptRunner


class BitcoinCrew:
    @staticmethod
    def wallet_agent():
        return Agent(
            role="Wallet Manager",
            goal="Read context and execute tasks using tools to interact with a wallet.",
            memory=True,
            tools=[
                BunScriptRunner.get_wallet_addresses,
                BunScriptRunner.get_wallet_status,
                BunScriptRunner.get_aibtc_balance,
                # BunScriptRunner.pay_invoice,
            ],
            backstory=dedent(
                """\
        You are a wallet agent with the ability to interact with the Bitcoin and Stacks
        blockchain. Your job is to read the context and execute tasks related to
        the wallet.
        """
            ),
            allow_delegation=False,
            verbose=True,
        )
