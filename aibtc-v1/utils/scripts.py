import subprocess
from datetime import datetime


def get_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def get_pretty_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# generic runner for Bun.js scripts
class BunScriptRunner:
    working_dir = "./agent-tools-ts/"
    script_dir = "src"

    @staticmethod
    def bun_run(contract_name: str, script_name: str, arg: str = None):
        """Runs a TypeScript script using bun with an optional positional argument."""
        command = [
            "bun",
            "run",
            f"{BunScriptRunner.script_dir}/{contract_name}/{script_name}",
        ]

        # Append the optional argument if provided
        if arg is not None:
            command.append(arg)

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
            return {"output": None, "error": e.stderr, "success": False}
