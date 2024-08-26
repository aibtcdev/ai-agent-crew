from crewai import Task
from textwrap import dedent


class WalletAnalysisTasks:

    def retrieve_wallet_info_task(self, agent, address):
        return Task(
            description=dedent(
                f"""
                Retrieve wallet balance detailed information for the specified address.
                
                Here is the address that I need to retrieve wallet balances for:
                {address}

                Your response should be a WalletInfo json object containing the wallet address, STX balance, NFT holdings, and FT holdings.
                """
            ),
            expected_output="A WalletInfo json object containing the wallet address, STX balance, NFT holdings, and FT holdings.",
            agent=agent,
        )

    def retrieve_transactions_task(self, agent, address):
        return Task(
            description=dedent(
                f"""
                Retrieve the last transactions associated with an address.
                
                Heres the Address that i need to find transactions for
                {address}

                Your response should be a TransactionList object containing up to 20 transactions associated with the wallet, including details like transaction type (tx_type), date (block_time_iso),  events (stx, ft, nft) and involved parties (tx_sender, tx_recipient, tx_contract_caller, tx_contract_address).
                """
            ),
            expected_output="A TransactionList object containing up to 20 transactions associated with the wallet, including only details like transaction type (tx_type), date (block_time_iso), events (stx, ft, nft) and involved parties (tx_sender, tx_recipient, tx_contract_caller, tx_contract_address). I do not need any other information. I need it to be simplified so it can be passed on as context.",
            agent=agent,
        )

    def analyze_activity_task(self, agent, address):
        return Task(
            description=dedent(
                f"""
                The wallet being analyzed is:
                {address}
                Analyze the wallet’s activity patterns, such as frequency of transactions, types of transactions, and interactions with smart contracts.
                Your response should be a WalletActivityAnalysis object containing insights into the wallet’s activity, including active periods, most common transaction types, and overall engagement in the blockchain ecosystem.
                """
            ),
            expected_output="A WalletActivityAnalysis object containing insights into the wallet’s activity, including active periods, most common transaction types, and overall engagement in the blockchain ecosystem.",
            agent=agent,
            tools=[],
        )

    def compile_report_task(self, agent, address):
        return Task(
            description=dedent(
                f"""
                Compile all analyses into a comprehensive final report for address {address}.
                Use the following information from the crew's shared memory to create a detailed report:
                1. Wallet Info 
                2. Transactions 
                3. Activity Analysis
                """
            ),
            # expected_output="A WalletReport object containing all the information gathered from previous tasks, formatted in a clear and organized manner.",
            expected_output="A clear summary of the wallet's activity and holdings, formatted in markdown. Do not display any json.",
            agent=agent,
            tools=[],
            async_execution=False,
        )
