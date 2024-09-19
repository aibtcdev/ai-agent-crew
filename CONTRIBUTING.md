# Contributing to AIBTC AI Agent Crew

We're excited that you're interested in contributing to the AIBTC AI Agent Crews! This document provides guidelines for contributing to make the process smooth and effective for everyone involved.

## How to Contribute

### Reporting Issues

- Check if the issue has already been reported in the [GitHub Issues](https://github.com/aibtcdev/ai-agent-crew/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/aibtcdev/ai-agent-crew/issues/new).
- Clearly describe the issue, including steps to reproduce when it is a bug.

### Suggesting Enhancements

- Open a new issue with a clear title and detailed description of the suggested enhancement.
- Provide any relevant examples or mock-ups if possible.

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. Ensure your code follows the existing style guidelines.
4. Make sure your code lints.
5. Issue a pull request!

## Development Setup

1. Clone the repository:

   ```
   git clone --recurse-submodules https://github.com/aibtcdev/ai-agent-crew.git
   ```

2. Set up a virtual environment:

   ```
   conda create -n ai-agent-crew python=3.11
   conda activate ai-agent-crew
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your API keys and other configuration.

5. Set up the agent-tools-ts submodule:

   Follow the setup instructions in the `agent-tools-ts/README.md`, excluding the `.env` instructions which are handled in the top-level `ai-agent-crew` files.

## Project Structure

- `aibtc-v1/app.py`: Main Streamlit application
- `aibtc-v1/crews/`: AI agent crews
- `aibtc-v1/components/`: Streamlit UI components
- `aibtc-v1/utils/`: Utility functions and classes
- `agent-tools-ts/`: Submodule for TypeScript blockchain tools

## Adding a New Crew

To add a new crew:

1. Create a new Python file in the `aibtc-v1/crews/` directory.
2. Define a new class that inherits from `AIBTC_Crew` in `aibtc-v1/utils/crews.py`.
3. Implement the required methods: `setup_agents()`, `setup_tasks()`, and `render_crew()`.
4. Update the `aibtc-v1/utils/session.py` file to include your new crew in the `generate_crew_mapping()` function.

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use type hints for function arguments and return values.
- Write docstrings for all functions, classes, and modules.
- Keep functions small and focused on a single task.
- Use meaningful variable and function names.

## Documentation

- Update the README.md if you change functionality.
- Document new features, commands, or significant changes.
- Keep code comments up-to-date.

## Commit Messages

- Use clear and meaningful commit messages.
- Start the commit message with a short summary (up to 50 characters).
- If necessary, add a detailed description after a blank line.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations, and container parameters.
3. Submit a pull request that clearly describes the changes for maintainers to review.

## Questions?

If you have any questions about contributing, feel free to ask in the [AIBTC Discord](https://discord.gg/Z59Z3FNbEX) or reach out to us on Twitter [@aibtcdev](https://x.com/aibtcdev).

Thank you for your interest in improving AIBTC AI Agent Crew!
