import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()


# Environment Variables for AI models
# os.environ["OPENAI_API_KEY"] = "Your OpenAI Key"
# os.environ["ANTHROPIC_API_KEY"] = "Your Anthropic Key"
# os.environ["OLLAMA_API_BASE"] = "Your Ollama API Base URL"

# Function to get the appropriate LLM based on the selected model
def get_llm(model_name):
    if model_name.startswith("gpt"):
        return ChatOpenAI(model_name=model_name)
    elif model_name == "llama2":
        return OllamaLLM(model=model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


model_name = "gpt-4o"  # OpenAI
# model_name = "claude-3-opus-20240229"  # Anthropic
# model_name = "llama2"  # Ollama

# Get the LLM object
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
    llm=llm
)
task = Task(
    description="Add a new smart contract to the Clarinet project.",
    expected_output="A message indicating the success or failure of the contract addition operation.",
    agent=research_agent,
    tools=[summarize_tool],
    function_args={'project_name': 'my_clarinet_project',
                   'contract_name': 'my_new_contract',
                   'contract_code': '{{agent_response}}'}
)

# Define the task for generating Clarity code
generate_clarity_code_task = Task(
    description=(
        "Generate Clarity code for a smart contract that allows users to lock Bitcoin for a specific time period. "
        "The code should ensure security, prevent re-entrancy, and handle exceptions properly."
    ),
    expected_output="A Clarity smart contract code snippet that locks Bitcoin for a specified period. Do not create anything beside code.",
    agent=clarity_code_generator

)

# Define the task for reviewing Clarity code
review_clarity_code_task = Task(
    description=(
        "Review the generated Clarity code for any syntax errors, logic errors, security vulnerabilities, "
        "and adherence to best practices. Ensure the code is optimized for performance and is secure."
    ),
    expected_output="A detailed report on code quality, potential errors, security vulnerabilities, and suggestions for improvement.",
    agent=clarity_code_reviewer
)

# Forming the crew with both agents and their tasks
crew = Crew(
    agents=[clarity_code_generator,
            #  clarity_code_reviewer
            ],
    tasks=[generate_clarity_code_task,
           # review_clarity_code_task
           ],
    process=Process.sequential,
    verbose=True  # Running tasks sequentially; first generation, then review
)

# Function to run the crew


def generate_and_review_contract(user_input):
    result = crew.kickoff(inputs={"user_input": user_input})
    return result


def main():
    st.title("Clarity Smart Contract Generator and Reviewer")

    user_input = st.text_area("Enter your smart contract requirements:",
                              "Create a Clarity smart contract to lock Bitcoin for a specified time.")

    if st.button("Generate and Review Smart Contract"):
        with st.spinner("Generating and reviewing smart contract..."):
            result = generate_and_review_contract(user_input)

        # Display results
        st.subheader("Generated Clarity Code")

        st.markdown(result)


if __name__ == "__main__":
    main()
