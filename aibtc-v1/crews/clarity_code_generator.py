import os
import streamlit as st
import subprocess
from crewai import Agent, Task
from crewai_tools import tool
from utils.crews import AIBTC_Crew


class ClarityCodeGeneratorCrew(AIBTC_Crew):
    def __init__(self):
        super().__init__("Clarity Code Generator Crew")

    def setup_agents(self, llm):
        clarity_code_generator = Agent(
            role="Clarity Code Generator",
            goal="Generate Clarity code for a smart contract on the Stacks blockchain based on user input requirements.",
            verbose=True,
            memory=True,
            backstory=(
                "You are an expert in Clarity, a smart contract language for the Stacks blockchain. "
                "Your goal is to write secure, efficient, and functional Clarity code based on specific user requirements. "
                "You should tailor your code generation to meet the exact needs described in the user input."
            ),
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(clarity_code_generator)

        clarity_code_reviewer = Agent(
            role="Clarity Code Reviewer",
            goal="Review the generated Clarity code, create a Clarinet project, and check its syntax.",
            verbose=True,
            memory=True,
            backstory=(
                "You are a meticulous Clarity code reviewer known for ensuring smart contract security and code quality on the Stacks blockchain. "
                "Your goal is to analyze the generated code, create a Clarinet project, add the contract, and check the syntax, providing detailed feedback on any issues found."
            ),
            allow_delegation=False,
            llm=llm,
            tools=[
                create_clarinet_project,
                create_new_smart_contract,
                check_smart_contract_syntax,
            ],
        )
        self.add_agent(clarity_code_reviewer)

        clarity_code_compiler = Agent(
            role="Clarity Code Compiler",
            goal="Combine the generated Clarity code and the code review report into a comprehensive output for the Streamlit app.",
            verbose=True,
            memory=True,
            backstory=(
                "You are a Clarity code compilation expert for the Stacks blockchain, responsible for taking the generated Clarity code and the code review report, "
                "and combining them into a final, comprehensive output that can be displayed in the Streamlit app. "
                "You ensure that the output clearly presents both the code and its review in a user-friendly format."
            ),
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(clarity_code_compiler)

    def setup_tasks(self, user_input):
        generate_clarity_code_task = Task(
            description=(
                "Generate a Clarity code snippet for a smart contract on the Stacks blockchain based on the following user requirements: {user_input}. "
                "Ensure the code is secure, efficient, and properly handles exceptions. "
                "Store your code in crew's shared memory 'contract_code'."
            ),
            expected_output="Provide a Clarity code snippet for a smart contract that meets the specified user requirements.",
            agent=self.agents[0],  # clarity_code_generator
        )
        self.add_task(generate_clarity_code_task)

        review_clarity_code_task = Task(
            description=(
                "Review the generated Clarity code, create a Clarinet project with it, and check its syntax. "
                "Provide a detailed report on the code quality, syntax check results, and any issues found. "
                f"Consider how well the code meets the original user requirements: {user_input}. "
                "You can find the code in crew's shared memory 'contract_code'. Store your response in crew's shared memory 'review'."
            ),
            expected_output="A detailed report on code quality, syntax check results, and any issues found, with reference to the original user requirements.",
            agent=self.agents[1],  # clarity_code_reviewer
        )
        self.add_task(review_clarity_code_task)

        compile_clarity_code_task = Task(
            description=(
                "Combine the generated Clarity code and the code review report into a comprehensive output that can be displayed in the Streamlit app. "
                f"Ensure that the output clearly shows how the code meets the original user requirements: {user_input}. "
                "You can access the contract code from crew's shared memory 'contract_code' and the code review from 'review'."
            ),
            expected_output="The final output that includes the Clarity code, the code review report, and how it addresses the user's requirements.",
            agent=self.agents[2],  # clarity_code_compiler
        )
        self.add_task(compile_clarity_code_task)

    def render_crew(self):
        st.subheader("Clarity Code Generator 🎱")
        st.markdown(
            "Generate valid Clarity code for a smart contract on the Stacks blockchain based on user input requirements."
        )

        with st.form("clarity_code_generator_form"):
            user_input = st.text_input(
                "Smart Contract Requirements",
                help="Enter your smart contract requirements",
                placeholder="Implement a function called `calculate-average` that takes a list of unsigned integers and returns the average as a response type. Handle the case where the list is empty.",
            )
            submitted = st.form_submit_button("Generate Clarity Code")

        if submitted and user_input:
            st.subheader("Clarity Code Generation Progress")
            try:
                # create containers for real-time updates
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                # reset callback lists
                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                # get LLM from session state
                llm = st.session_state.llm

                # create and run the crew
                clarity_code_generator_crew_class = ClarityCodeGeneratorCrew()
                clarity_code_generator_crew_class.setup_agents(llm)
                clarity_code_generator_crew_class.setup_tasks(user_input)
                clarity_code_generator_crew = (
                    clarity_code_generator_crew_class.create_crew()
                )

                with st.spinner("Generating Clarity code..."):
                    result = clarity_code_generator_crew.kickoff()

                st.success("Code generation complete!")
                st.subheader("Clarity Code Generation Results")

                result_str = str(result)
                st.markdown(result_str)

                st.download_button(
                    label="Download Clarity Code (Text)",
                    data=result_str,
                    file_name="generated_clarity_code.clar",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Error during code generation: {e}")
                st.info("Please check your inputs and try again.")
        else:
            st.info(
                "Please enter your smart contract requirements and click 'Generate Clarity Code'."
            )


#########################
# Agent Tools
#########################


@tool("Create Clarinet Project")
def create_clarinet_project(project_name: str) -> str:
    """
    Create a new Clarinet project in the working directory.
    """
    try:
        os.makedirs(WORKING_DIR, exist_ok=True)
        os.makedirs(os.path.join(WORKING_DIR, ".clarinet"), exist_ok=True)
        with open(os.path.join(WORKING_DIR, ".clarinet", "clarinetrc.toml"), "w") as f:
            f.write("enable_telemetry = true")

        subprocess.run(["clarinet", "new", project_name], check=True, cwd=WORKING_DIR)
        return f"Successfully created new Clarinet project: {project_name} in {WORKING_DIR}"
    except subprocess.CalledProcessError as e:
        return f"Error creating Clarinet project: {e}"


@tool("Create New Smart Contract")
def create_new_smart_contract(
    project_name: str, contract_name: str, contract_code: str
) -> str:
    """
    Create a new smart contract in an existing Clarinet project within the working directory.
    """
    project_dir = os.path.join(WORKING_DIR, project_name)
    try:
        subprocess.run(
            ["clarinet", "contract", "new", contract_name], check=True, cwd=project_dir
        )

        contract_file_path = os.path.join(
            project_dir, "contracts", f"{contract_name}.clar"
        )
        with open(contract_file_path, "w") as contract_file:
            contract_file.write(contract_code)

        return f"Successfully added new contract '{contract_name}' to project '{project_name}' and wrote code to {contract_file_path}"
    except subprocess.CalledProcessError as e:
        return f"Error creating smart contract: {e}"
    except IOError as e:
        return f"Error writing contract code: {e}"


@tool("Check Smart Contract Syntax")
def check_smart_contract_syntax(project_name: str, contract_name: str) -> str:
    """
    Check the syntax of a smart contract in a Clarinet project within the working directory.
    """
    project_dir = os.path.join(WORKING_DIR, project_name)
    try:
        contract_file_path = os.path.join("contracts", f"{contract_name}.clar")

        result = subprocess.run(
            ["clarinet", "check", contract_file_path],
            capture_output=True,
            text=True,
            cwd=project_dir,
        )

        return (
            f"Syntax check result for '{contract_name}' in project '{project_name}':\n{result.stdout}"
            if result.returncode == 0
            else f"Syntax errors in '{contract_name}':\n{result.stderr}"
        )
    except subprocess.CalledProcessError as e:
        return f"Error checking syntax: {e}"
    except IOError as e:
        return f"Error accessing contract file: {e}"


#########################
# Helper Functions
#########################

WORKING_DIR = "./working_dir"
