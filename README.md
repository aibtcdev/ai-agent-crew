# 🤖💳🤖 Stacks M2M

## Agents with Wallets

> [!CAUTION]
> This is an early experiment, agents do automatic things, here be dragons, run at your own risk.

## Choosing an LLM

CrewAI allows for multiple model configurations, from using OpenAI/Microsoft Azure APIs to running local models, [see the documentation](https://docs.crewai.com/how-to/LLM-Connections/#configuration-examples) for more info on how to configure for your specific needs. An example env file (`.env.example`) is provided.

Current testing is being done with [Text generation web UI](https://github.com/oobabooga/text-generation-webui)

- temperature 0.01
- seed 1234567890
- miqu-70b-q5_k_m
- 32k context length

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

## Setting up the Wallet

This repository also imports the `stacks-m2m/scripts` repository as a submodule.

This provides Typescript functions to interact with a Stacks wallet using Stacks.js.

To clone the repository, run the following command:

- ssh: `git clone --recurse-submodules git@github.com:stacks-m2m/crew.git`
- https: `git clone --recurse-submodules https://github.com/stacks-m2m/crew.git`

To update the submodule, run the following command:
`git submodule update --remote --merge`

- TODO: list of script functions (pay-invoice, send-stx, send-btc (abtc))
- TODO: configure .env with wallet info

## Local Development

### CrewAI

- TODO: high level explanation of CrewAI principals
- Agent
- Crew
- Task

### Agents

- TODO: where they are defined

### Tools

- TODO: where they are defined
