import subprocess

from crewai_tools import SeleniumScrapingTool, tool


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


class AIBTCTokenTools:
    @staticmethod
    @tool("Get current aiBTC balance")
    def get_aibtc_balance(dummy_arg=None):
        """Get the aiBTC balance of the currently configured wallet."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-balance.ts")

    @staticmethod
    @tool("Get 10,000 aiBTC from the faucet")
    def get_faucet_drip(dummy_arg=None):
        """Transfers 10,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "faucet-drip.ts")

    @staticmethod
    @tool("Get 1,000,000 aiBTC from the faucet")
    def get_faucet_drop(dummy_arg=None):
        """Transfers 1,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "faucet-drop.ts")

    @staticmethod
    @tool("Get 100,000,000 aiBTC from the faucet")
    def get_faucet_flood(dummy_arg=None):
        """Transfers 100,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("stacks-m2m-aibtc", "get-faucet-flood.ts")


class OnchainResourcesTools:
    @staticmethod
    @tool("Get recent payment data for an address")
    def get_recent_payment_data(address: str):
        """Get the recent payment data for a given address."""
        return BunScriptRunner.bun_run(
            "stacks-m2m-v2", "get-recent-payment-data-by-address.ts", address
        )

    @staticmethod
    @tool("Get resource data for a resource")
    def get_resource_data(dummy_arg: None):
        """Get the resource data for the resource."""
        return BunScriptRunner.bun_run("stacks-m2m-v2", "get-resource-by-name.ts")

    @staticmethod
    @tool("Get user data by address")
    def get_user_data_by_address(address: str):
        """Get the user data for a given address."""
        return BunScriptRunner.bun_run(
            "stacks-m2m-v2", "get-user-data-by-address.ts", address
        )

    @staticmethod
    @tool("Pay invoice for resource")
    def pay_invoice_for_resource(dummy_arg: None):
        """Pay the invoice for a given resource."""
        return BunScriptRunner.bun_run("stacks-m2m-v2", "pay-invoice.ts")


class WalletTools:
    @staticmethod
    @tool("Get Wallet Addresses")
    def get_wallet_addresses(dummy_arg=None):
        """Get a list of the available addresses of the configured wallet by index."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-addresses.ts")

    @staticmethod
    @tool("Get Wallet Status")
    def get_wallet_status(dummy_arg=None):
        """Get information about the currently configured wallet address."""
        return BunScriptRunner.bun_run("wallet", "get-wallet-status.ts")

    @staticmethod
    @tool("Get Transaction Data")
    def get_transaction_data(transaction_id: str):
        """Get an object that contains information about a given transaction ID."""
        return BunScriptRunner.bun_run("wallet", "get-transaction.ts", transaction_id)

    @staticmethod
    @tool("Get Transaction Status")
    def get_transaction_status(transaction_id: str):
        """Get only the status of the transaction, usually pending or complete."""
        return BunScriptRunner.bun_run(
            "wallet", "get-transaction-status.ts", transaction_id
        )

    @staticmethod
    @tool("Sign Message")
    def sign_message(dummy_arg=None):
        """Sign a message with the configured wallet address."""
        return BunScriptRunner.bun_run("wallet", "sign-message.ts")


class WebTools:
    @staticmethod
    @tool("Scrape Reddit URL")
    def scrape_reddit_url(website_url: str):
        """Targeted tool to scrape the provided Reddit URL using Selenium."""
        scraping_tool = SeleniumScrapingTool(website_url=website_url, class_name="main")
        return scraping_tool._run()

    @staticmethod
    @tool("Scrape X (formerly Twitter) URL")
    def scrape_x_or_twitter_url(website_url: str):
        """Targeted tool to scrape the provided X (formerly Twitter) URL using Selenium."""
        scraping_tool = SeleniumScrapingTool(
            website_url=website_url, class_name="css-175oi2r"
        )
        return scraping_tool._run()

    @staticmethod
    @tool("Scrape Generic URL")
    def scrape_generic_url(website_url: str):
        """Scrape the provided URL using Selenium if the URL is unrecognized and it does not match any other tool."""
        scraping_tool = SeleniumScrapingTool(website_url=website_url)
        return scraping_tool._run()

def get_tool_groups():
    return {
        "aiBTC Token Operations": AIBTCTokenTools,
        "On-chain Resource Management": OnchainResourcesTools,
        "Wallet Operations": WalletTools,
        "Web Scraping Operations": WebTools,
    }