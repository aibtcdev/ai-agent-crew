import os
import subprocess
import shutil


class ClarinetInterface:
    def __init__(self):
        self.env = os.environ.copy()
        self.clarinet_binary = None
        self.project_dir = None
        self.working_dir = None

    def initialize_clarinet(self):
        # Find project root
        project_root = self.find_project_root()
        if project_root is None:
            raise FileNotFoundError("Could not find project root directory")

        # Setup working directory
        self.working_dir = os.path.join(
            project_root, "ai-agent-crew", "aibtc-v1", "crews", "working_dir"
        )
        os.makedirs(self.working_dir, exist_ok=True)

        # Attempt to find Clarinet binary
        self.clarinet_binary = shutil.which("clarinet")

        if self.clarinet_binary:
            # Clarinet is installed globally
            print(f"Using global Clarinet binary at {self.clarinet_binary}")
        else:
            # Clarinet is not installed globally, check for local installation
            self.setup_paths(project_root)
            self.clarinet_binary = self.CLARINET_BIN_PATH
            if not os.path.exists(self.clarinet_binary):
                raise FileNotFoundError(
                    f"Clarinet binary not found at {self.clarinet_binary}. Please install Clarinet."
                )
            print(f"Using local Clarinet binary at {self.clarinet_binary}")

            # If we're on Replit, set LD_LIBRARY_PATH
            if os.environ.get("REPL_ID"):
                print(
                    "Detected Replit environment. Setting LD_LIBRARY_PATH for patched Clarinet."
                )
                self.update_environment()
                # Update os.environ so that subprocess and shutil.which can find the dependencies
                os.environ.update(
                    {
                        "PATH": self.env["PATH"],
                        "LD_LIBRARY_PATH": self.env["LD_LIBRARY_PATH"],
                    }
                )
            else:
                # Not on Replit, LD_LIBRARY_PATH is not needed
                print(
                    "Not running on Replit. LD_LIBRARY_PATH is not required for local Clarinet."
                )

    def find_project_root(self):
        current_dir = os.getcwd()
        while True:
            print("Checking", current_dir)
            if os.path.exists(os.path.join(current_dir, "ai-agent-crew")):
                print("Found project root at", current_dir)
                return current_dir  # Found the project root
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                # Reached the root directory without finding the project root
                print("Could not find project root directory", current_dir)
                return None
            current_dir = parent_dir

    def setup_paths(self, project_root):
        self.CLARINET_SETUP_DIR = os.path.join(
            project_root, "ai-agent-crew", "clarinet"
        )
        self.CLARINET_BIN_DIR = os.path.join(self.CLARINET_SETUP_DIR, "bin")
        self.CLARINET_BIN_PATH = os.path.join(self.CLARINET_BIN_DIR, "clarinet")
        self.CLARINET_DEPS_DIR = os.path.join(self.CLARINET_SETUP_DIR, "glibc-2.34")

    def update_environment(self):
        # Update PATH and LD_LIBRARY_PATH for the local Clarinet binary
        path = self.env.get("PATH", "")
        ld_library_path = self.env.get("LD_LIBRARY_PATH", "")
        self.env["PATH"] = f"{self.CLARINET_BIN_DIR}:{path}"
        self.env["LD_LIBRARY_PATH"] = (
            f"{self.CLARINET_DEPS_DIR}:/usr/lib/x86_64-linux-gnu:{ld_library_path}"
        )

    def create_project(self, project_name):
        # Set the project directory
        self.project_dir = os.path.join(self.working_dir, project_name)
        # Ensure the working directory exists
        os.makedirs(self.working_dir, exist_ok=True)
        # Create the project
        cmd = [self.clarinet_binary, "new", project_name]
        return self.run_command(cmd, cwd=self.working_dir)

    def run_command(self, command, cwd=None):
        result = subprocess.run(
            command,
            cwd=cwd or self.project_dir,
            env=self.env,
            capture_output=True,
            text=True,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def add_contract(self, contract_name):
        cmd = [self.clarinet_binary, "contract", "new", contract_name]
        return self.run_command(cmd)

    def update_contract(self, contract_name, contract_code):
        contract_file_path = os.path.join(
            self.project_dir, "contracts", f"{contract_name}.clar"
        )

        # Write the contract code to the file (overwrite if exists)
        try:
            with open(contract_file_path, "w") as f:
                f.write(contract_code)
            return {
                "stdout": f"Contract '{contract_name}' updated successfully.",
                "stderr": "",
                "returncode": 0,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Error writing contract code for contract name {contract_name}: {e}",
                "returncode": 1,
            }

    def remove_contract(self, contract_name):
        cmd = [self.clarinet_binary, "contract", "rm", contract_name]
        return self.run_command(cmd)

    def check_all_contracts(self):
        cmd = [self.clarinet_binary, "check"]
        return self.run_command(cmd)

    def check_contract(self, contract_name):
        cmd = [self.clarinet_binary, "check", contract_name]
        return self.run_command(cmd)

    def add_requirement(self, contract_id):
        cmd = [self.clarinet_binary, "requirements", "add", contract_id]
        return self.run_command(cmd)
