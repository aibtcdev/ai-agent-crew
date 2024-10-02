import inspect
import os
import streamlit as st
from crewai import Agent, Task
from crewai_tools import tool, Tool
from textwrap import dedent
from utils.clarinet import ClarinetInterface
from utils.clarity import clarityFunctionsList, clarityHints, clarityKeywordsList
from utils.crews import AIBTC_Crew, display_token_usage
from utils.scripts import get_timestamp


class ClarityCodeGeneratorCrewV2(AIBTC_Crew):
    def __init__(self):
        super().__init__("Clarity Code Generator V2")

    def setup_agents(self, llm):
        clarity_environment_maintainer = Agent(
            role="Clarity Environment Maintainer",
            goal="Ensure the Clarity environment is set up correctly and ready for code generation and review.",
            backstory=dedent(
                "You are responsible for maintaining the Clarity environment, ensuring that all tools and dependencies are correctly installed and configured. "
                "Your goal is to provide a stable and reliable environment for generating and reviewing Clarity code."
            ),
            tools=[AgentTools.initialize_clarinet],
            allow_delegation=False,
            memory=True,
            verbose=True,
            llm=llm,
        )
        self.add_agent(clarity_environment_maintainer)

        clarity_project_manager = Agent(
            role="Clarity Project Manager",
            goal="Create a new Clarinet project and add the generated Clarity code to it.",
            backstory=dedent(
                "You are a skilled project manager with expertise in setting up Clarinet projects for smart contract development.",
            ),
            tools=[
                AgentTools.create_clarinet_project,
            ],
            allow_delegation=False,
            memory=True,
            verbose=True,
            llm=llm,
        )
        self.add_agent(clarity_project_manager)

        clarity_code_generator = Agent(
            role="Clarity Code Generator",
            goal="Generate Clarity code for a smart contract on the Stacks blockchain based on user input requirements.",
            backstory=dedent(
                "You are an expert in Clarity, a smart contract language for the Stacks blockchain. "
                "Your goal is to write secure, efficient, and functional Clarity code based on specific user requirements. "
                "You should tailor your code generation to meet the exact needs described in the user input. "
                f"Remember to follow the Clarity hints for best practices:\n{clarityHints}"
                f"{clarityKeywordsList}"
                f"{clarityFunctionsList}"
            ),
            tools=[AgentTools.add_new_smart_contract, AgentTools.update_smart_contract],
            allow_delegation=False,
            memory=True,
            verbose=True,
            llm=llm,
        )
        self.add_agent(clarity_code_generator)

        clarity_code_reviewer = Agent(
            role="Clarity Code Reviewer",
            goal="Review the generated Clarity code, create a Clarinet project, and check its syntax.",
            backstory=dedent(
                "You are a meticulous Clarity code reviewer known for ensuring smart contract security and code quality on the Stacks blockchain. "
                "Your goal is to analyze the generated code by checking the syntax, providing detailed feedback on any issues found. "
                "If you encounter issues, provide detailed context and ask the Clarity Code Generator to update the contract. "
                "Do not continue until the code passes the syntax check. "
                f"Remember to follow the Clarity hints for best practices:\n{clarityHints}"
            ),
            tools=[
                AgentTools.check_all_smart_contract_syntax,
            ],
            allow_delegation=True,
            memory=True,
            verbose=True,
            llm=llm,
        )
        self.add_agent(clarity_code_reviewer)

        clarity_code_reporter = Agent(
            role="Clarity Code Reporter",
            goal="Create a detailed report on the code quality, syntax check results, and any issues found.",
            backstory=dedent(
                "You are a skilled Clarity code reporter, responsible for creating detailed reports on the quality and syntax of Clarity code. "
                "Your goal is to provide a comprehensive analysis of the code review results, highlighting any issues found and suggesting improvements."
                "You ensure that the output clearly presents both the code and its review in a user-friendly Markdown format."
                f"Remember to follow the Clarity hints for best practices:\n{clarityHints}"
            ),
            tools=[],
            allow_delegation=False,
            memory=True,
            verbose=True,
            llm=llm,
        )
        self.add_agent(clarity_code_reporter)

    def setup_tasks(self, user_input):
        setup_clarinet_environment = Task(
            description="Initialize the Clarinet environment to ensure all tools and dependencies are correctly set up.",
            expected_output="A confirmation that the Clarinet environment has been successfully initialized.",
            agent=self.agents[0],  # clarity_environment_maintainer
        )
        self.add_task(setup_clarinet_environment)

        create_clarinet_project = Task(
            description=f"Create a new Clarinet project to manage the generated Clarity code based on the user's input: {user_input}",
            expected_output="A confirmation that the Clarinet project has been successfully created.",
            agent=self.agents[1],  # clarity_project_manager
        )
        self.add_task(create_clarinet_project)

        generate_clarity_code = Task(
            description=(
                f"Generate a Clarity code snippet for a smart contract on the Stacks blockchain based on the following user requirements: {user_input}. "
                "Ensure the code is secure, efficient, and properly handles exceptions. "
                "Store the generated code using your tools to create a new smart contract."
            ),
            expected_output="The generated Clarity code snippet for the smart contract, saved in the Clarinet project.",
            agent=self.agents[2],  # clarity_code_generator
        )
        self.add_task(generate_clarity_code)

        # TODO: check for and add requirements
        # needs to be able to get all requirements currently in project
        # needs to be able to add requirements if needed before syntax check
        # might also be callable from reviewer if issue found in syntax check

        review_clarity_code = Task(
            description=(
                "Review the generated Clarity code by checking its syntax using your tools. "
                "Provide a detailed report on the code quality, syntax check results, and any issues found. "
                f"Consider how well the code meets the original user requirements: {user_input}. "
                "Delegate to the Clarity Code Generator until the code passes the syntax check."
            ),
            expected_output="Once the syntax check passes, a detailed report on the code quality, syntax check results, and any issues found.",
            agent=self.agents[3],  # clarity_code_reviewer
            context=[generate_clarity_code],
        )
        self.add_task(review_clarity_code)

        compile_clarity_code_report = Task(
            description=(
                "Combine the generated Clarity code and the code review report into a comprehensive output that can be displayed in the Streamlit app. "
                f"Ensure that the output clearly shows how the code meets the original user requirements: {user_input}. "
            ),
            expected_output="The final output that includes the Clarity code, the code review report, and how it addresses the user's requirements.",
            agent=self.agents[4],  # clarity_code_reporter
            context=[generate_clarity_code, review_clarity_code],
        )
        self.add_task(compile_clarity_code_report)

    @staticmethod
    def get_task_inputs():
        return ["user_input"]

    @classmethod
    def get_all_tools(cls):
        return AgentTools.get_all_tools()

    def render_crew(self):
        st.subheader("Clarity Code Generator V2 🧙")
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
                st.write("Tool Outputs:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                # reset callback lists
                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                # get LLM from session state
                llm = st.session_state.llm

                # create and run the crew
                print("Creating Clarity Code Generator V2 Crew...")
                clarity_code_generator_crew_class = ClarityCodeGeneratorCrewV2()
                clarity_code_generator_crew_class.setup_agents(llm)
                clarity_code_generator_crew_class.setup_tasks(user_input)
                clarity_code_generator_crew = (
                    clarity_code_generator_crew_class.create_crew()
                )

                with st.spinner("Generating Clarity code..."):
                    print("Running Clarity Code Generator V2 Crew...")
                    result = clarity_code_generator_crew.kickoff()

                st.success("Code generation complete!")

                display_token_usage(result.token_usage)

                st.subheader("Clarity Code Generation Results")

                result_str = str(result.raw)
                st.markdown(result_str)

                timestamp = get_timestamp()
                file_name = f"{timestamp}_generated_clarity_code.clar"

                st.download_button(
                    label="Download Clarity Code (Text)",
                    data=result_str,
                    file_name=file_name,
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Error during code generation: {e}")
                st.error("Please check your inputs and try again.")
        else:
            st.write(
                "Please enter your smart contract requirements and click 'Generate Clarity Code'."
            )


#########################
# Agent Tools
#########################


class AgentTools:
    clarinet_interface = None  # hodls ClarinetInterface instance

    @staticmethod
    @tool("Initialize Clarinet")
    def initialize_clarinet() -> str:
        """Initialize Clarinet by detecting the Clarinet binary and setting up the environment."""
        AgentTools.clarinet_interface = ClarinetInterface()
        try:
            AgentTools.clarinet_interface.initialize_clarinet()
            return "Clarinet initialized successfully."
        except Exception as e:
            return f"Error initializing Clarinet: {str(e)}"

    @staticmethod
    @tool("Create New Clarinet Project")
    def create_clarinet_project(project_name: str) -> str:
        """Create a new Clarinet project with the given name."""
        if not AgentTools.clarinet_interface:
            return (
                "Error: Clarinet is not initialized. Please initialize Clarinet first."
            )
        result = AgentTools.clarinet_interface.create_project(project_name)
        if result["returncode"] != 0:
            return f"Error creating Clarinet project: {result['stdout'] + result['stderr']}"
        return f"Successfully created new Clarinet project: {project_name}\n{result['stdout']}"

    @staticmethod
    @tool("Add New Smart Contract")
    def add_new_smart_contract(contract_name: str, contract_code: str) -> str:
        """Add a new smart contract to the Clarinet project with the given name and code."""
        if (
            not AgentTools.clarinet_interface
            or not AgentTools.clarinet_interface.project_dir
        ):
            return "Error: Clarinet project is not created. Please create a Clarinet project first."
        result = AgentTools.clarinet_interface.add_contract(contract_name)
        if result["returncode"] != 0:
            return f"Error adding smart contract: {result['stderr']}"

        # Write the contract code to the contract file
        contract_file_path = os.path.join(
            AgentTools.clarinet_interface.project_dir,
            "contracts",
            f"{contract_name}.clar",
        )
        try:
            with open(contract_file_path, "w") as f:
                f.write(contract_code)
            return (
                f"Successfully added new contract '{contract_name}'\n{result['stdout']}"
            )
        except Exception as e:
            return f"Error writing contract code: {str(e)}"

    @staticmethod
    @tool("Update Smart Contract")
    def update_smart_contract(contract_name: str, contract_code: str) -> str:
        """Update an existing smart contract in the Clarinet project with the given name and code."""
        if (
            not AgentTools.clarinet_interface
            or not AgentTools.clarinet_interface.project_dir
        ):
            return "Error: Clarinet project is not created. Please create a Clarinet project first."
        result = AgentTools.clarinet_interface.update_contract(
            contract_name, contract_code
        )
        if result["returncode"] != 0:
            return f"Error updating smart contract: {result['stderr']}"
        return f"Successfully updated contract '{contract_name}'\n{result['stdout']}"

    @staticmethod
    @tool("Check All Smart Contracts Syntax")
    def check_all_smart_contract_syntax() -> str:
        """Check the syntax of all of the smart contracts in the Clarinet project."""
        if (
            not AgentTools.clarinet_interface
            or not AgentTools.clarinet_interface.project_dir
        ):
            return "Error: Clarinet project is not created. Please create a Clarinet project first."
        result = AgentTools.clarinet_interface.check_all_contracts()
        if result["returncode"] != 0:
            return f"Syntax errors found:\n{result['stdout']}\n{result['stderr']}"
        return f"Syntax check passed:\n{result['stdout']}"

    @staticmethod
    @tool("Check Smart Contract Syntax")
    def check_single_smart_contract_syntax(contract_name: str) -> str:
        """Check the syntax of a specific smart contract in the Clarinet project."""
        if (
            not AgentTools.clarinet_interface
            or not AgentTools.clarinet_interface.project_dir
        ):
            return "Error: Clarinet project is not created. Please create a Clarinet project first."
        result = AgentTools.clarinet_interface.check_contract(contract_name)
        if result["returncode"] != 0:
            return f"Syntax errors found for contract '{contract_name}':\n{result['stdout']}\n{result['stderr']}"
        return (
            f"Syntax check passed for contract '{contract_name}':\n{result['stdout']}"
        )

    @staticmethod
    @tool("Add Mainnet Contract as Requirement")
    def add_mainnet_contract_as_requirement(contract_id: str) -> str:
        """Add a mainnet contract as a requirement to the Clarinet project."""
        if (
            not AgentTools.clarinet_interface
            or not AgentTools.clarinet_interface.project_dir
        ):
            return "Error: Clarinet project is not created. Please create a Clarinet project first."
        result = AgentTools.clarinet_interface.add_requirement(contract_id)
        if result["returncode"] != 0:
            return f"Error adding mainnet contract as requirement: {result['stderr']}"
        return f"Successfully added mainnet contract '{contract_id}' as requirement.\n{result['stdout']}"

    @classmethod
    def get_all_tools(cls):
        members = inspect.getmembers(cls)
        tools = [
            member
            for name, member in members
            if isinstance(member, Tool)
            or (hasattr(member, "__wrapped__") and isinstance(member.__wrapped__, Tool))
        ]
        return tools
