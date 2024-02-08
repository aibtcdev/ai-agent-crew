from crewai import Agent
from textwrap import dedent
from tools.bun_run import ScriptRunner


class BitcoinCrew:
    @staticmethod
    def wallet_agent():
        return Agent(
            role="Wallet",
            goal="Read context and execute tasks using tools to interact with a wallet.",
            memory=True,
            tools=[
                ScriptRunner.get_wallet_addresses,
                ScriptRunner.get_wallet_status,
                # ScriptRunner.pay_invoice,
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
