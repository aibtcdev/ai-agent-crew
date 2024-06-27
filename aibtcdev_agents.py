from crewai import Agent
from tools.wallet import WalletTools
from tools.aibtc_token import AIBTCTokenTools
from tools.onchain_resources import OnchainResourcesTools


def get_wallet_manager(llm):
    return Agent(
        role="Wallet Manager",
        goal="Manage Bitcoin wallet operations and provide information",
        backstory="You are an expert in Bitcoin wallet management with deep knowledge of blockchain technology.",
        tools=[
            WalletTools.get_wallet_status,
            WalletTools.get_wallet_addresses,
            WalletTools.get_transaction_data,
            WalletTools.get_transaction_status,
            AIBTCTokenTools.get_aibtc_balance,
            AIBTCTokenTools.get_faucet_drip,
        ],
        verbose=True,
        llm=llm,
    )


def get_resource_manager(llm):
    return Agent(
        role="Resource Manager",
        goal="Manage on-chain resources and provide relevant information",
        backstory="You are an expert in managing blockchain resources and understanding complex on-chain data.",
        tools=[
            OnchainResourcesTools.get_recent_payment_data,
            OnchainResourcesTools.get_resource_data,
            OnchainResourcesTools.get_user_data_by_address,
            OnchainResourcesTools.pay_invoice_for_resource,
        ],
        verbose=True,
        llm=llm,
    )
