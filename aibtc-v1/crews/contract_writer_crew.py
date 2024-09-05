import streamlit as st
from crewai import Agent, Crew, Process, Task
from textwrap import dedent
from utils.session import crew_step_callback, crew_task_callback
from .tools import ClarinetTools, StacksResources

####################
# AGENTS
####################


class ClarityAgents:

    @staticmethod
    def get_clarity_writer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Clarity Writer",
            goal=dedent(
                """
                Write clear, efficient, and valid Clarity code to meet the specific user request. Ensure the code conforms to standards and handles the intricacies of token creation and management on the Stacks blockchain.
                """
            ),
            tools=[
                StacksResources.get_code_search_tool,
                StacksResources.get_function_search_tool,
            ],  # No tools required for writing
            backstory=dedent(
                """
                You are a senior blockchain developer with expertise in smart contract development, particularly on the Stacks blockchain. 
                You have years of experience creating and refining Clarity contracts. Your responsibility 
                is to write robust and clean code that adheres to best practices, is well-documented, and performs efficiently.
                """
            ),
            verbose=True,
            memory=True,  # Enable memory to pass contract code
            **kwargs,
        )

    @staticmethod
    def get_clarity_reviewer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Clarity Reviewer",
            goal=dedent(
                """
                Carefully review the Clarity code for any syntax errors, logical issues, and inefficiencies. Ensure the code strictly adheres to the standard for the Stacks blockchain, and provide actionable feedback to improve code quality.
                """
            ),
            tools=[
                ClarinetTools.check_clarinet_syntax
            ],  # Reviewer agent uses Clarinet tools to check code syntax
            backstory=dedent(
                """
                You are a seasoned Clarity code reviewer with a meticulous eye for detail. You have in-depth knowledge of Clarity and standards, 
                with a focus on spotting logical inconsistencies, security vulnerabilities, and potential inefficiencies. You collaborate closely with 
                the writer to improve the contract iteratively, providing detailed feedback on every issue found.
                """
            ),
            verbose=True,
            memory=True,  # Enable memory to retrieve and store contract code
            **kwargs,
        )

    @staticmethod
    def get_clarity_validator_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Clarity Validator",
            goal=dedent(
                """
                Validate the Clarity code by running it through all required Clarinet checks. Ensure the contract passes syntax checks, logical checks, 
                and is ready for deployment in a live Stacks blockchain environment. Ensure the contract adheres to all standards and passes 
                every required test case.
                """
            ),
            tools=[
                ClarinetTools.create_clarinet_project,
                ClarinetTools.create_clarinet_contract,
                ClarinetTools.write_clarity_contract,
                ClarinetTools.check_clarinet_syntax,
            ],  # Validator agent uses tools for project creation, contract creation, and validation
            backstory=dedent(
                """
                You are an experienced validator with expertise in ensuring the robustness and reliability of smart contracts. You specialize 
                in using the Clarinet toolkit to verify contract integrity, ensuring that each contract passes stringent checks for deployment on 
                the Stacks blockchain. Your role is to ensure that all syntax errors are resolved and that the contract adheres to the expected 
                specifications before final approval.
                """
            ),
            verbose=True,
            memory=True,  # Enable memory for passing contract between tasks
            **kwargs,
        )


####################
# TASKS
####################


class ClarityTasks:

    @staticmethod
    def create_clarinet_project_task(agent):
        return Task(
            description=dedent(
                """
                Create a new Clarinet project where the Clarity contract will be written, reviewed, and validated. 
                This project is essential for organizing and running all subsequent tests and checks on the contract.
                """
            ),
            expected_output="A new Clarinet project has been initialized and is ready for contract development.",
            async_execution=False,
            agent=agent,
        )

    @staticmethod
    def create_clarinet_contract_task(agent):
        return Task(
            description=dedent(
                """
                Create a new Clarity contract within the initialized Clarinet project. The contract will act as a template 
                where the actual logic will be written by the Clarity Writer.
                """
            ),
            expected_output="A new Clarity contract has been created within the Clarinet project.",
            async_execution=False,
            agent=agent,
        )

    @staticmethod
    def write_clarity_code_task(agent, user_request):
        return Task(
            description=dedent(
                f"""
                Write the Clarity code for the contract based on the following user request:

                **User Request:** {user_request}

                Ensure the contract follows best practices, and is optimized for the Stacks blockchain.
                """
            ),
            expected_output="The Clarity code has been written and stored in memory under the key 'contract_code'.",
            async_execution=False,
            agent=agent,
        )

    @staticmethod
    def review_clarity_code_task(agent):
        return Task(
            description=dedent(
                """
                Review the Clarity code stored in memory for syntax, logic errors, and performance issues. Ensure the contract conforms standards and recommend improvements or corrections where necessary.
                """
            ),
            expected_output="The Clarity code has been reviewed and feedback, including improvements and fixes, has been added to memory.",
            async_execution=False,
            agent=agent,
        )

    @staticmethod
    def validate_clarity_code_task(agent):
        return Task(
            description=dedent(
                """
                Run the final Clarity code stored in memory through Clarinet to validate it. Check for syntax errors and logical inconsistencies. The process should continue until no errors are found.
                """
            ),
            expected_output="The Clarity code has been validated and is either error-free or the errors are stored in memory for further revision.",
            async_execution=False,
            agent=agent,
        )


####################
# CREW(S)
####################


class ClarityCrew:

    @staticmethod
    def create_clarity_code_crew(user_request):
        llm = st.session_state.llm

        clarity_writer = ClarityAgents.get_clarity_writer_agent(llm)
        clarity_reviewer = ClarityAgents.get_clarity_reviewer_agent(llm)
        clarity_validator = ClarityAgents.get_clarity_validator_agent(llm)

        # Tasks
        create_project_task = ClarityTasks.create_clarinet_project_task(
            clarity_validator
        )
        create_contract_task = ClarityTasks.create_clarinet_contract_task(
            clarity_validator
        )
        write_code_task = ClarityTasks.write_clarity_code_task(
            clarity_writer, user_request
        )
        review_code_task = ClarityTasks.review_clarity_code_task(clarity_reviewer)
        validate_code_task = ClarityTasks.validate_clarity_code_task(clarity_validator)

        return Crew(
            agents=[clarity_writer, clarity_reviewer, clarity_validator],
            tasks=[
                create_project_task,  # Create Clarinet project once
                create_contract_task,  # Create Clarinet contract once
                write_code_task,  # Iteratively write
                review_code_task,  # Iteratively review
                validate_code_task,  # Iteratively validate until it passes
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,  # Keep memory enabled for passing contract between tasks
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    @staticmethod
    def render_clarity_code_crew():
        st.subheader("Clarity Contract Generator and Validator")
        st.markdown(
            "This tool will generate and validate a Clarity contract based on your request."
        )

        with st.form("clarity_code_form"):
            user_request = st.text_area(
                "Request",
                help="Enter your request for Clarity code (e.g., 'Create a contract for Stacks').",
            )
            submitted = st.form_submit_button("Generate and Validate Code")

        if submitted and user_request:
            st.subheader("Processing")
            try:
                # create containers for real-time updates
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()

                # reset callback lists
                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                crew = ClarityCrew.create_clarity_code_crew(user_request)

                with st.spinner("Generating and Validating..."):
                    result = crew.kickoff()

                st.success("Process complete!")

                st.subheader("Results")

                # Retrieve the final contract code from memory
                final_code = crew.agents[0].memory.get("contract_code", "No code found")

                st.markdown(f"**Generated Clarity Code:**\n\n```{final_code}```")

                st.download_button(
                    label="Download Clarity Code (Text)",
                    data=final_code,
                    file_name="clarity_code.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your inputs and try again.")
        else:
            st.info(
                "Enter your request, then click 'Generate and Validate Code' to see results."
            )
