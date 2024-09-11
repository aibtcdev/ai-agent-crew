from crewai import Task


def get_wallet_status(agent):
    return Task(
        description="Get the current wallet status and display the information.",
        expected_output="A detailed report of the current wallet status including balance and recent transactions.",
        agent=agent,
    )


def get_aibtc_balance(agent):
    return Task(
        description="Retrieve and display the current aiBTC balance.",
        expected_output="The current aiBTC balance as a numerical value with appropriate units.",
        agent=agent,
    )


def get_aibtc_faucet_drip(agent):
    return Task(
        description="Request aiBTC from the faucet and display the transaction ID.",
        expected_output="The transaction ID of the aiBTC faucet drip request.",
        agent=agent,
    )


def get_aibtc_resource_data(agent):
    return Task(
        description="Retrieve and display resource data for a given address",
        expected_output="A detailed report of the resource data associated with the provided address.",
        agent=agent,
    )
