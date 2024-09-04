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


@tool("Clarinet")
def runClarinet(project_name: str, contract_name: str, contract_code: str) -> str:
    """
    Create a new Clarinet project, add a new contract, and check its syntax.

    This tool creates a new Clarinet project, adds a new contract to it,
    writes the provided contract code, and checks its syntax.

    Args:
        project_name (str): The name of the Clarinet project to be created.
        contract_name (str): The name of the contract to be created.
        contract_code (str): The code to be written into the new contract file.

    Returns:
        str: A message indicating the result of the operations.
    """
    initial_dir = os.getcwd()
    try:
        # Create a new Clarinet project
        subprocess.run(["clarinet", "new", project_name], check=True)
        print(f"Created new Clarinet project: {project_name}")

        # Change directory to the project folder
        os.chdir(project_name)

        # Add a new contract
        subprocess.run(["clarinet", "contract", "new",
                       contract_name], check=True)
        print(f"Added new contract: {contract_name}")

        # Write the contract code to the contract file
        contract_file_path = os.path.join("contracts", f"{contract_name}.clar")
        with open(contract_file_path, "w") as contract_file:
            contract_file.write(contract_code)
        print(f"Wrote code to {contract_file_path}")

        # Check the syntax of the contract
        result = subprocess.run(
            ["clarinet", "check", contract_name], capture_output=True, text=True
        )
        print(f"Syntax check result: {result.stdout}")

        return f"Successfully created project '{project_name}', added contract '{contract_name}', and checked its syntax."
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    finally:
        os.chdir(initial_dir)


def get_llm(model_name):
    if model_name.startswith("gpt"):
        return ChatOpenAI(model_name=model_name)
    elif model_name == "llama2":
        return OllamaLLM(model=model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


# Set your desired model name
model_name = "gpt-4o"  # Example with OpenAI GPT-4
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
    goal="Review the generated Clarity code, create a Clarinet project, and check its syntax.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous Clarity code reviewer known for ensuring smart contract security and code quality. "
        "Your goal is to analyze the generated code, create a Clarinet project, and check the syntax."
    ),
    allow_delegation=False,
    llm=llm,
    tools=[runClarinet]
)

# Define the Clarity Code Compiler Agent
clarity_code_compiler = Agent(
    role="Clarity Code Compiler",
    goal="Combine the generated Clarity code and the code review report into a comprehensive output for the Streamlit app.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a Clarity code compilation expert responsible for taking the generated Clarity code and the code review report, and combining them into a final, comprehensive output that can be displayed in the Streamlit app."
    ),
    allow_delegation=False,
    llm=llm
)

# Define the task for generating Clarity code
generate_clarity_code_task = Task(
    description=(
        "Generate a Clarity code snippet for a smart contract that defines and manages token transfers, including functions for minting, transferring, and checking balances. The code should ensure security, prevent re-entrancy, and handle exceptions properly."
        "Store your code in crew's shared memory 'contract_code' "

    ),
    expected_output="Provide a Clarity code snippet for a smart contract that defines and manages token transfers.",
    agent=clarity_code_generator,
)

# Define the task for reviewing Clarity code
review_clarity_code_task = Task(
    description=(
        "Review the generated Clarity code, create a Clarinet project with it, and check its syntax. "
        "Provide a report on the code quality and any issues found during the syntax check. You can find the code in crew's shared memory 'contract code', store your response in crew's shared memory 'review' "
    ),
    expected_output="A detailed report on code quality, syntax check results, and any issues found.",
    agent=clarity_code_reviewer,
)

# Define the task for compiling the Clarity code and review report
compile_clarity_code_task = Task(
    description=(
        "Combine the generated Clarity code and the code review report into a comprehensive output that can be displayed in the Streamlit app. You can access the contract code from crew's shared memory 'contract_code' and the code review from 'review'."
    ),
    expected_output="The final output that includes the Clarity code and the code review report.",
    agent=clarity_code_compiler,
)
crew = Crew(
    agents=[clarity_code_generator,
            clarity_code_reviewer, clarity_code_compiler],
    tasks=[generate_clarity_code_task,
           review_clarity_code_task, compile_clarity_code_task],
    process=Process.sequential,
    verbose=True
)
# # Forming the crew with both agents and their tasks
# crew = Crew(
#     agents=[clarity_code_generator, clarity_code_reviewer],
#     tasks=[generate_clarity_code_task, review_clarity_code_task],
#     process=Process.sequential,
#     verbose=True
# )

# Function to run the crew


def generate_and_review_contract(user_input):
    result = crew.kickoff(inputs={"user_input": user_input})
    print(result, "result(*(***))")

    return result

# Streamlit app definition


def main():
    st.title("Clarity Smart Contract Generator and Reviewer")

    user_input = st.text_area("Enter your smart contract requirements:",
                              "write functions that will return the info from the map, individually and all in one call")

    if st.button("Generate and Review Smart Contract"):
        with st.spinner("Generating and reviewing smart contract..."):
            generated_code = generate_and_review_contract(
                user_input)

        st.subheader("Generated Clarity Code")
        st.code(generated_code, language='clarity')

        # st.subheader("Review Report")
        # st.markdown(review_report)


if __name__ == "__main__":
    main()
