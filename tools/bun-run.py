import subprocess
from langhchain import tool

script_dir = "scripts/src/"

def bun_run(script_name):
    """Run a typescript script using bun"""
    # command to run
    command = ["bun", "run", f"{script_dir}{script_name}"]
    try:
      result = subprocess.run(command, check=True, text=True, capture_output=True)
      return {"output": result.stdout, "error": None, "success": True}
  except subprocess.CalledProcessError as e:
      # If the subprocess call failed, return the error and a failure flag
      return {"output": None, "error": e.stderr, "success": False}

@tool("Get Wallet Info")
def get_wallet_info(dummy_arg=None):
    """Get information about the configured wallet."""
    return bun_run("get-wallet-info.ts")

@tool("Pay Invoice")
def pay_invoice(resource_name: str):
    """Pay an invoice."""
    return bun_run("pay-invoice.ts")
    