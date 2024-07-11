from .bun_runner import BunScriptRunner
from langchain.tools import tool


class OnchainResourcesTools:
    @tool("Get recent payment data for an address")
    @staticmethod
    def get_recent_payment_data(address: str):
        """Get the recent payment data for a given address."""
        return BunScriptRunner.bun_run(
            "stacks-m2m-v2", "get-recent-payment-data-by-address.ts", address
        )

    @tool("Get resource data for a resource")
    @staticmethod
    def get_resource_data(dummy_arg: None):
        """Get the resource data for the resource."""
        return BunScriptRunner.bun_run("stacks-m2m-v2", "get-resource-by-name.ts")

    @tool("Get user data by address")
    @staticmethod
    def get_user_data_by_address(address: str):
        """Get the user data for a given address."""
        return BunScriptRunner.bun_run(
            "stacks-m2m-v2", "get-user-data-by-address.ts", address
        )

    @tool("Pay invoice for resource")
    @staticmethod
    def pay_invoice_for_resource(dummy_arg: None):
        """Pay the invoice for a given resource."""
        return BunScriptRunner.bun_run("stacks-m2m-v2", "pay-invoice.ts")
