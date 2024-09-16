import os
import subprocess


class ClarinetExecutor:

    @classmethod
    def _find_project_root(cls):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while True:
            if os.path.exists(os.path.join(current_dir, "ai-agent-crew")):
                return os.path.join(current_dir, "ai-agent-crew")
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                raise FileNotFoundError("Could not find project root directory")
            current_dir = parent_dir

    @classmethod
    def _setup_global_config(cls):
        home_dir = os.path.expanduser("~")
        clarinet_config_dir = os.path.join(home_dir, ".clarinet")
        clarinetrc_path = os.path.join(clarinet_config_dir, "clarinetrc.toml")

        os.makedirs(clarinet_config_dir, exist_ok=True)

        if not os.path.exists(clarinetrc_path):
            with open(clarinetrc_path, "w") as f:
                f.write("enable_telemetry = true")

    @classmethod
    def _setup_working_dir(cls):
        cls._setup_paths()
        os.makedirs(cls.CLARINET_WORKING_DIR, exist_ok=True)

    @classmethod
    def _setup_paths(cls):
        project_root = cls._find_project_root()
        cls.CLARINET_SETUP_DIR = os.path.join(project_root, "clarinet")
        cls.CLARINET_BIN_DIR = os.path.join(cls.CLARINET_SETUP_DIR, "bin")
        cls.CLARINET_BIN_PATH = os.path.join(cls.CLARINET_BIN_DIR, "clarinet")
        cls.CLARINET_DEPS_DIR = os.path.join(cls.CLARINET_SETUP_DIR, "glibc-2.34")
        cls.CLARINET_WORKING_DIR = os.path.join(
            project_root, "aibtc-v1", "crews", "working_dir"
        )
        cls.CLARINET_CONFIG_FILE = os.path.join(
            cls.CLARINET_SETUP_DIR, "clarinet-config"
        )

    @classmethod
    def run_clarinet_command(cls, command, cwd=None):
        # setup global config before each run
        cls._setup_global_config()
        # setup working dir before each run
        cls._setup_working_dir()
        # setup paths before each run
        cls._setup_paths()

        # check that the clarinet binary exists
        if not os.path.exists(cls.CLARINET_BIN_PATH):
            raise FileNotFoundError(
                f"Clarinet binary not found at {cls.CLARINET_BIN_PATH}"
            )

        # source the clarinet-config file
        with open(cls.CLARINET_CONFIG_FILE, "r") as config_file:
            for line in config_file:
                if line.startswith("export"):
                    key, value = line.strip().split("=", 1)
                    key = key.split()[-1]  # remove 'export' from the key
                    os.environ[key] = value.strip('"')

        # copy the environment variables
        env = os.environ.copy()

        # run the command
        args = [cls.CLARINET_BIN_PATH] + command
        return subprocess.run(
            args,
            check=True,
            cwd=cwd or cls.CLARINET_WORKING_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
