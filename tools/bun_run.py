import subprocess
from langchain.tools import tool


class ScriptRunner:
    working_dir = "scripts/"
    script_dir = "src/"

    @staticmethod
    def bun_run(script_name):
        """Run a typescript script using bun"""
        # command to run
        command = ["bun", "run", f"{ScriptRunner.script_dir}{script_name}"]
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                cwd=ScriptRunner.working_dir,
            )
            return {"output": result.stdout, "error": None, "success": True}
        except subprocess.CalledProcessError as e:
            # If the subprocess call failed, return the error and a failure flag
            return {"output": None, "error": e.stderr, "success": False}

    @tool("Get Wallet Addresses")
    @staticmethod
    def get_wallet_addresses(dummy_arg=None):
        """Get the addresses of the configured wallet."""
        return ScriptRunner.bun_run("get-wallet-addresses.ts")

    @tool("Get Wallet Status")
    @staticmethod
    def get_wallet_status(dummy_arg=None):
        """Get information about the configured wallet."""
        return ScriptRunner.bun_run("get-wallet-status.ts")

    @tool("Pay Invoice")
    @staticmethod
    def pay_invoice(dummy_arg=None):
        """Pay an invoice."""
        return ScriptRunner.bun_run("pay-invoice.ts")
