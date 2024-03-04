<p align="center"><img src="https://github.com/aibtcdev/landing-page/blob/main/public/logos/aibtcdev-logo-sm-250px.png" alt="Bitcoin x AI Logo" width="150px" ></p>

# Bitcoin x AI: AI Agent Crew

## Description

> [!CAUTION]
> This is an early experiment, agents do automatic things, here be dragons, run at your own risk.

This repository contains the code for the AI Agent Crew, a collection of agents that can be used to perform assigned tasks using defined tools.

## Development

Tech stack:

- Python 3.11 ([miniconda recommended](https://docs.anaconda.com/free/miniconda/index.html#latest-miniconda-installer-links) for virtual env)
- CrewAI
- CrewAI Tools

To run this locally:

1. Clone this repository
2. Create or activate the virtual environment
   1. Create: `conda create -n ai-agent-crew python=3.11`
   2. Activate: `conda activate ai-agent-crew`
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `python run_crew.py`

### Choosing an LLM

CrewAI allows for multiple model configurations, from using OpenAI/Microsoft Azure APIs to running local models, [see the documentation](https://docs.crewai.com/how-to/LLM-Connections/#configuration-examples) for more info on how to configure for your specific needs.

An example env file (`.env.example`) is provided.

Current testing is being done with [Text generation web UI](https://github.com/oobabooga/text-generation-webui)

Command to run Text generation web UI:
`python server.py --api --verbose`

Command to run Text generation web UI on another machine:
`python server.py --api --verbose --listen`

If you already have local models downloaded, you can specify the model directory for Text generation web UI to read from:
`python server.py --model-dir /path/to/your/model_files --listen --api --verbose`

Once running, access the web UI at port 7860 and:

- On the `Model` tab, select the model to load
- (optional) On the `Parameters - Generation` tab, set custom parameters for the model
- On the `Model` tab, load the model and wait until "Successfully loaded" appears

> [!TIP]
> The IP address and port of the model running on Text generation web UI should be set in `.env` to use a local model.

### Setting up the Wallet

This repository also imports the `aibtcdev/agent-tools-ts` repository as a submodule.

This provides Typescript functions to interact with a Stacks wallet using Stacks.js.

To clone the repository and sync the submodule, run the following command:

- ssh: `git clone --recurse-submodules git@github.com:aibtcdev/ai-agent-crew.git`
- https: `git clone --recurse-submodules https://github.com/aibtcdev/ai-agent-crew.git`

To update the submodule, run the following command:
`git submodule update --remote --merge`

Within the `scripts` directory is a `.env.example` file that should be copied to `.env` and filled out with the wallet information.

Within the `scripts/src` directory are various scripts that can be run to interact with the wallet. These should be wrapped as a langchain `@tool` for LLMs to access it.

## AI Agent Framework

### CrewAI

[CrewAI](https://crewai.io) provides an easy-to-use interface for creating and managing agents, tasks, tools, and crews. It is built on top of [Langchain](https://python.langchain.com/docs/get_started/introduction), a decentralized, open-source, and privacy-focused AI platform.

- **Agents:** a team member; an autonomous unit programmed to perform tasks, make decisions, and communication with other agents
- **Tasks:** a task; individual assignments that agents complete
- **Tools:** a skill; single-input functions that agents can use to complete tasks (can use [any Langchain tool](https://python.langchain.com/docs/modules/agents/tools/) or define custom ones)
- **Crew:** a collaborative group; a group of agents that work together to complete a set of tasks

### Agents

- Agent definitions are in the `agents.py` file

### Tools

- Tool definitions are in the `/tools` directory
