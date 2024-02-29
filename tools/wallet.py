from bun_run import BunScriptRunner
from langchain.tools import tool

class WalletTools:
    @tool("Get Wallet Addresses")
    @staticmethod
    def get_wallet_addresses(dummy_arg=None):
        """Get a list of the available addresses of the configured wallet by index."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-addresses.ts")

    @tool("Get Wallet Status")
    @staticmethod
    def get_wallet_status(dummy_arg=None):
        """Get information about the currently configured wallet address."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-status.ts")
    
    @tool("Get Transaction Data")
    @staticmethod
    def get_transaction_data(transaction_id: str):
        """Get an object that contains information about a given transaction ID."""
        return BunScriptRunner.bun_run("wallet", "get-transaction.ts", transaction_id)
    
    @tool("Get Transaction Status")
    @staticmethod
    def get_transaction_status(transaction_id: str):
        """Get only the status of the transaction, usually pending or complete."""
        return BunScriptRunner.bun_run("wallet", "get-transaction-status.ts", transaction_id)
    
    