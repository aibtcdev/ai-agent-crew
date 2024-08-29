from crewai_tools import SeleniumScrapingTool, tool
from utils.scripts import BunScriptRunner

### ALL CLASSES AND FUNCTIONS BELOW ARE AGENT TOOLS ###


class AIBTCResourceTools:
    @staticmethod
    @tool("Get recent payment data for an address")
    def get_recent_payment_data(address: str):
        """Get the recent payment data for a given address."""
        return BunScriptRunner.bun_run(
            "aibtcdev-resources", "get-recent-payment-data-by-address.ts", address
        )

    @staticmethod
    @tool("Get resource data for a resource")
    def get_resource_data(dummy_arg: None):
        """Get the resource data for the resource."""
        return BunScriptRunner.bun_run("aibtcdev-resources", "get-resource-by-name.ts")

    @staticmethod
    @tool("Get user data by address")
    def get_user_data_by_address(address: str):
        """Get the user data for a given address."""
        return BunScriptRunner.bun_run(
            "aibtcdev-resources", "get-user-data-by-address.ts", address
        )

    @staticmethod
    @tool("Pay invoice for resource")
    def pay_invoice_for_resource(dummy_arg: None):
        """Pay the invoice for a given resource."""
        return BunScriptRunner.bun_run("aibtcdev-resources", "pay-invoice.ts")


class AIBTCTokenTools:
    @staticmethod
    @tool("Get current aiBTC balance")
    def get_aibtc_balance(dummy_arg=None):
        """Get the aiBTC balance of the currently configured wallet."""
        return BunScriptRunner.bun_run("aibtcdev-aibtc-token", "get-balance.ts")

    @staticmethod
    @tool("Get 10,000 aiBTC from the faucet")
    def get_faucet_drip(dummy_arg=None):
        """Transfers 10,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("aibtcdev-aibtc-token", "faucet-drip.ts")

    @staticmethod
    @tool("Get 1,000,000 aiBTC from the faucet")
    def get_faucet_drop(dummy_arg=None):
        """Transfers 1,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("aibtcdev-aibtc-token", "faucet-drop.ts")

    @staticmethod
    @tool("Get 100,000,000 aiBTC from the faucet")
    def get_faucet_flood(dummy_arg=None):
        """Transfers 100,000,000 aiBTC from the faucet to your configured address and returns a transaction ID."""
        return BunScriptRunner.bun_run("aibtcdev-aibtc-token", "get-faucet-flood.ts")


class StacksBNSTools:
    @staticmethod
    @tool("Get BNS name for an address")
    def get_bns_name_for_address(address: str):
        """Get the on-chain BNS name for a given Stacks address."""
        return BunScriptRunner.bun_run("stacks-bns", "get-bns-name.ts", address)

    @staticmethod
    @tool("Get address for a BNS name")
    def get_address_for_bns_name(bns_name: str):
        """Get the on-chain Stacks address for a given BNS name."""
        return BunScriptRunner.bun_run(
            "stacks-bns", "get-address-for-bns-name.ts", bns_name
        )

    @staticmethod
    @tool("Check if BNS name is available")
    def check_bns_name_availability(bns_name: str):
        """Check if a given BNS name is available."""
        return BunScriptRunner.bun_run("stacks-bns", "check-available.ts", bns_name)

    @staticmethod
    @tool("Preorder a BNS name (step 1)")
    def preorder_bns_name_step_1(bns_name: str):
        """Preorder a BNS name, step 1 of 2, transaction is required to be successful before registering in step 2."""
        return BunScriptRunner.bun_run("stacks-bns", "preorder.ts", bns_name)

    @staticmethod
    @tool("Register a BNS name (step 2)")
    def register_bns_name_step_2(bns_name: str):
        """Register a BNS name, step 2 of 2, transaction is required to be successful before registering in step 2."""
        return BunScriptRunner.bun_run("stacks-bns", "register.ts", bns_name)


class StacksWalletTools:
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


class WebsiteTools:
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


# for the UI, returns dict of tool groups for display
# automatically includes any function in the class
def get_tool_groups():
    return {
        "AIBTC Resources": AIBTCResourceTools,
        "AIBTC Token": AIBTCTokenTools,
        "Stacks BNS": StacksBNSTools,
        "Stacks Wallet": StacksWalletTools,
        "Website Tools": WebsiteTools,
    }
