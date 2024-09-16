import os
import yaml
from utils.session import generate_crew_mapping, get_llm, load_env_vars


def load_mock_inputs(mock_inputs_file="./training/config/mock_inputs.yaml"):
    """Load mock inputs from mock_inputs.yaml."""
    if not os.path.exists(mock_inputs_file):
        raise FileNotFoundError(f"Mock inputs file not found: {mock_inputs_file}")

    with open(mock_inputs_file, "r") as f:
        mock_inputs = yaml.safe_load(f)
    return mock_inputs


def generate_yaml_for_all_crews(
    output_dir="./training/config",
    mock_inputs_file="./training/config/mock_inputs.yaml",
):
    """Generate separate agents.yaml and tasks.yaml for each crew, using mock inputs."""
    crew_mapping = generate_crew_mapping()  # Get all available crews
    mock_inputs = load_mock_inputs(mock_inputs_file)  # Load mock inputs
    # Setup agents (use the necessary model or config)
    env_vars = load_env_vars()
    llm = get_llm(
        env_vars.get("LLM_PROVIDER", "OpenAI"),
        env_vars.get("OPENAI_API_KEY", ""),
        env_vars.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
        env_vars.get("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    )

    for crew_name, crew_info in crew_mapping.items():
        crew_class = crew_info["class"]

        # Create an instance of the crew
        crew_instance = crew_class()
        crew_instance.setup_agents(llm)

        # Get task inputs for this crew
        task_inputs = crew_info[
            "task_inputs"
        ]()  # Get task input names (e.g., "address", "contract_code")

        # Fetch the mock inputs from the mock_inputs.yaml file
        if crew_name in mock_inputs:
            input_values = mock_inputs[crew_name]
        else:
            raise ValueError(f"No mock input values found for crew: {crew_name}")

        # Ensure all required task inputs have mock data
        missing_inputs = [
            input_name for input_name in task_inputs if input_name not in input_values
        ]
        if missing_inputs:
            raise ValueError(f"Missing mock inputs for {crew_name}: {missing_inputs}")

        # Setup tasks using mock inputs
        crew_instance.setup_tasks(**input_values)

        agents_data = {}
        tasks_data = {}

        # Extract agents and tasks for this crew
        for agent in crew_instance.agents:
            agents_data[agent.name] = {
                "role": agent.role,
                "goal": agent.goal,
                "tools": [tool.name for tool in agent.tools],
                "memory": agent.memory,
                "backstory": agent.backstory,
            }

        for task in crew_instance.tasks:
            tasks_data[task.name] = {
                "description": task.description,
                "expected_output": task.expected_output,
                "agent": task.agent.name,
            }

        # Ensure the output directory exists for each crew
        crew_output_dir = os.path.join(output_dir, crew_name)
        os.makedirs(crew_output_dir, exist_ok=True)

        # Write agents.yaml for this crew
        with open(os.path.join(crew_output_dir, "agents.yaml"), "w") as agents_file:
            yaml.dump(agents_data, agents_file)

        # Write tasks.yaml for this crew
        with open(os.path.join(crew_output_dir, "tasks.yaml"), "w") as tasks_file:
            yaml.dump(tasks_data, tasks_file)

        print(f"Generated YAML files for {crew_name} in {crew_output_dir}")


# Example usage
if __name__ == "__main__":
    generate_yaml_for_all_crews()
