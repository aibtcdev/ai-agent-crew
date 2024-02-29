import subprocess


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
