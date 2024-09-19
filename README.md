<img src="https://aibtc.dev/logos/aibtcdev-primary-logo-black-wide-1000px.png" alt="AIBTC Working Group Logo" style="width: 100%; max-width: 1000px; display: block; margin: 1rem auto;" />

# AIBTC AI Agent Crew

## Description

> [!CAUTION]
> This is an early experiment, agents do automatic things, here be dragons, run at your own risk.

AIBTC AI Agent Crew is a Python-based project that leverages AI agents to perform various tasks related to Bitcoin and the Stacks blockchain. It provides a Streamlit user interface for interacting with these AI agents and visualizing their outputs.

The project uses the [CrewAI framework](https://crewai.com) to create and manage AI agents, tasks, and tools. It integrates with the `agent-tools-ts` submodule to perform low-level blockchain operations.

## Key Features

Streamlit UI for easy interaction with AI agents
Multiple specialized crews for different blockchain-related tasks
Integration with various LLM providers (OpenAI, Anthropic, Ollama)
Extensible architecture for adding new crews and tools

## Development

### Tech Stack

- Python 3.11
- Streamlit for the user interface
- CrewAI and CrewAI Tools for AI agent management
- Langchain for language model interactions
- Bun.js (via submodule) for TypeScript-based blockchain tools

### Prerequisites

- Python 3.11 (virtual environment recommended)
- Git

### Installation

1. Clone the repository with submodules:

   ```
   git clone --recurse-submodules https://github.com/aibtcdev/ai-agent-crew.git
   cd ai-agent-crew
   ```

2. Create and activate a virtual environment (using [miniconda](https://docs.anaconda.com/miniconda/)):

   ```
   conda create -n ai-agent-crew python=3.11
   conda activate ai-agent-crew
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up the `agent-tools-ts` submodule:

   Follow the setup instructions in the [agent-tools-ts README](./agent-tools-ts/README.md) to install Bun.js

### Configuration

1. Copy the .env.example file to .env:

   ```
   cp .env.example .env
   ```

2. Edit the `.env` file to set your API keys and other configuration options.

### Usage

To run the Streamlit app:

```
streamlit run aibtc-v1/app.py
```

This will start the Streamlit server and open the application in your default web browser.

### Project Structure

`aibtc-v1/app.py`: Main Streamlit application entry point
`aibtc-v1/crews/`: Contains different AI agent crews (e.g., `SmartContractAnalyzerCrew`, `WalletSummaryCrew`)
`aibtc-v1/components/`: Streamlit UI components for different tabs
`aibtc-v1/utils/`: Utility functions and classes
`agent-tools-ts/`: Submodule for TypeScript-based blockchain tools

### Adding New Crews

To add a new crew:

1. Create a new Python file in the `aibtc-v1/crews/` directory.
2. Define a new class that inherits from `AIBTC_Crew` in `aibtc-v1/utils/crews.py`.
3. Implement the required methods: `setup_agents()`, `setup_tasks()`, and `render_crew()`.
4. Update the `aibtc-v1/utils/session.py` file to include your new crew in the `generate_crew_mapping()` function.

### Setting up the Wallet

This repository also imports the `aibtcdev/agent-tools-ts` repository as a submodule.

This provides TypeScript functions to interact with a Stacks wallet using Stacks.js.

To update the submodule, run the following command:
`git submodule update --remote --merge`

Within the `scripts` directory is a `.env.example` file, you can disregard it as the top-level `.env.example` file for this repository covers all the needed values.

Within the `scripts/src` directory are various scripts that can be run to interact with the wallet tooling. These should be wrapped as a CrewAI `@tool` for LLMs to access it.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](./CONTRIBUTING.md) file for details on how to get started.

## Contact

If you have any questions about contributing, please open an issue, ask in the [AIBTC Discord](https://discord.gg/Z59Z3FNbEX) or reach out to us on X [@aibtcdev](https://x.com/aibtcdev).
