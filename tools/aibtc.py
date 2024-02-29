from bun_run import BunScriptRunner
from langchain.tools import tool

class aiBTCTools:
    @tool("Get current aiBTC balance")
    @staticmethod
    def get_aibtc_balance(dummy_arg=None):
        """Get the aiBTC balance of the currently configured wallet."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-balance.ts")

    @tool("Get 10,000 aiBTC from the faucet")
    @staticmethod
    def get_faucet_drip(dummy_arg=None):
        """Transfers 10,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-faucet-drip.ts")
    
    @tool("Get 1,000,000 aiBTC from the faucet")
    @staticmethod
    def get_faucet_drop(dummy_arg=None):
        """Transfers 1,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-faucet-drop.ts")
    
    @tool("Get 100,000,000 aiBTC from the faucet")
    @staticmethod
    def get_faucet_flood(dummy_arg=None):
        """Transfers 100,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-faucet-flood.ts")