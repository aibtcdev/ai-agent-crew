import os
import subprocess
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Define a custom tool for interacting with the Clarinet CLI


@tool("Clarinet")
def runClarinet(project_name: str, contract_name: str, contract_code: str) -> str:
    """
    Add a new contract to the specified Clarinet project and write code into it.

    This tool allows users to create a new smart contract within a specified
    Clarinet project. It changes the current working directory to the project folder,
    creates a new contract file using the `clarinet contract new` command,
    and writes the provided contract code into that file.

    Args:
        project_name (str): The name of the Clarinet project folder.
        contract_name (str): The name of the contract to be created.
        contract_code (str): The code to be written into the new contract file.

    Returns:
        str: A message indicating the success or failure of the contract addition operation.
    """
    initial_dir = os.getcwd()
    try:
        # Create a new Clarinet project
        subprocess.run(["clarinet", "new", project_name], check=True)

        # Change directory to the project folder
        os.chdir(project_name)

        # Add a new contract
        subprocess.run(["clarinet", "contract", "new",
                       contract_name], check=True)

        # Write the contract code to the contract file
        contract_file_path = os.path.join("contracts", f"{contract_name}.clar")
        with open(contract_file_path, "w") as contract_file:
            contract_file.write(contract_code)

        # Check the syntax of the contract
        subprocess.run(["clarinet", "check", contract_name], check=True)

        return f"Successfully created and checked contract '{contract_name}' in project '{project_name}'."
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    finally:
        os.chdir(initial_dir)

# Function to get the appropriate LLM based on the selected model


def get_llm(model_name):
    if model_name.startswith("gpt"):
        return ChatOpenAI(model_name=model_name)
    elif model_name == "llama2":
        return OllamaLLM(model=model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


# Set your desired model name
model_name = "gpt-4"  # Example with OpenAI GPT-4
llm = get_llm(model_name)

# Define the Clarity Code Generator Agent
clarity_code_generator = Agent(
    role="Clarity Code Generator",
    goal="Generate Clarity code for a smart contract on the Bitcoin blockchain based on user input requirements.",
    verbose=True,
    memory=True,
    backstory=(
        "You are an expert in Clarity, a smart contract language for the Bitcoin blockchain. "
        "Your goal is to write secure, efficient, and functional Clarity code based on user instructions. Do not create or write anything beside code."
    ),
    allow_delegation=False,
    llm=llm
)

# Define the Clarity Code Reviewer Agent
clarity_code_reviewer = Agent(
    role="Clarity Code Reviewer",
    goal="Review the generated Clarity code for correctness, security vulnerabilities, and adherence to best practices.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous Clarity code reviewer known for ensuring smart contract security and code quality. "
        "Your goal is to analyze the generated code, detect potential issues, and provide feedback for improvements."
    ),
    allow_delegation=False,
    tools=[runClarinet],
    llm=llm
)

# Define the task for generating Clarity code
generate_clarity_code_task = Task(
    description=(
        "Generate Clarity code for a smart contract that allows users to lock Bitcoin for a specific time period. "
        "The code should ensure security, prevent re-entrancy, and handle exceptions properly."
    ),
    expected_output="A Clarity smart contract code snippet that locks Bitcoin for a specified period.",
    agent=clarity_code_generator,
    output_key="clarity_code"  # Store the generated code in this key
)

# Define tool for clarity
# task = Task(
#     description="Add a new smart contract to the Clarinet project.",
#     expected_output="A message indicating the success or failure of the contract addition operation.",
#     agent=research_agent,
#     tools=[runClarinet],
#     function_args={'project_name': 'my_clarinet_project',
#                    'contract_name': 'my_new_contract',
#                    'contract_code': '{{agent_response}}'}
# )

# Define the task for reviewing Clarity code
review_clarity_code_task = Task(
    description=(
        "Review the generated Clarity code for any syntax errors, logic errors, security vulnerabilities, "
        "and adherence to best practices. Ensure the code is optimized for performance and is secure."
    ),
    expected_output="A detailed report on code quality, potential errors, security vulnerabilities, and suggestions for improvement.",
    agent=clarity_code_reviewer,
    # Pass the generated code from the previous task
    inputs={"contract_code": "clarity_code"},
    output_key="review_report"  # Store the review report in this key
)

# Forming the crew with both agents and their tasks
crew = Crew(
    agents=[clarity_code_generator, clarity_code_reviewer],
    tasks=[generate_clarity_code_task, review_clarity_code_task],
    # Running tasks sequentially; first generation, then review
    process=Process.sequential,
    verbose=True
)

# Function to run the crew


def generate_and_review_contract(user_input):
    result = crew.kickoff(inputs={"user_input": user_input})
    return result

# Streamlit app definition


def main():
    st.title("Clarity Smart Contract Generator and Reviewer")

    user_input = st.text_area("Enter your smart contract requirements:",
                              "Create a Clarity smart contract to lock Bitcoin for a specified time.")

    if st.button("Generate and Review Smart Contract"):
        with st.spinner("Generating and reviewing smart contract..."):
            result = generate_and_review_contract(user_input)

        # Display results
        st.subheader("Generated Clarity Code")
        generated_code = result.get('clarity_code')
        st.code(generated_code, language='clar')

        st.subheader("Review Report")
        review_report = result.get('review_report')
        st.markdown(review_report)


if __name__ == "__main__":
    main()
