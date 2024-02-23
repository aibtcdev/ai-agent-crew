import subprocess
from langchain.tools import tool


class BunScriptRunner:
    working_dir = "./scripts/"
    script_dir = "src"

    @staticmethod
    def bun_run(contract_name: str, script_name: str):
        """Runs a typescript script using bun"""
        # command to run
        command = ["bun", "run", f"{BunScriptRunner.script_dir}/{contract_name}/{script_name}"]
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                cwd=BunScriptRunner.working_dir,
            )
            return {"output": result.stdout, "error": None, "success": True}
        except subprocess.CalledProcessError as e:
            # If the subprocess call failed, return the error and a failure flag
            return {"output": None, "error": e.stderr, "success": False}

    @tool("Get Wallet Addresses")
    @staticmethod
    def get_wallet_addresses(dummy_arg=None):
        """Get the available addresses of the configured wallet."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-addresses.ts")

    @tool("Get Wallet Status")
    @staticmethod
    def get_wallet_status(dummy_arg=None):
        """Get information about the currently configured wallet."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-status.ts")
    
    @tool("Get aiBTC Balance")
    @staticmethod
    def get_aibtc_balance(dummy_arg=None):
        """Get the aiBTC balance of the currently configured wallet."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-balance.ts")

    @tool("Pay Invoice")
    @staticmethod
    def pay_invoice(dummy_arg=None):
        """Pay an invoice."""
        return BunScriptRunner.bun_run("stacks-m2m-v2", "pay-invoice.ts")
