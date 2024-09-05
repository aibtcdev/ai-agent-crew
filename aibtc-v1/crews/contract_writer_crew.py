import streamlit as st
from crewai import Agent, Crew, Process, Task
from textwrap import dedent
from utils.session import crew_step_callback, crew_task_callback
from .tools import ClarinetTools

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
                Write efficient, clean, valid Clarity code based on the user's request.
                """
            ),
            tools=[],  # Add relevant tools if any
            backstory=dedent(
                """
                You are an expert blockchain developer who is well-versed in Bitcoin, Stacks, and the Clarity language.
                """
            ),
            verbose=True,
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
                Evaluate Clarity code and relay errors to the Clarity Writer when found. You need to setup clarinet project, create new clarinet contract, write the content into the file and check syntax.
                """
            ),
            tools=[
                ClarinetTools.check_clarinet_syntax,
                ClarinetTools.create_clarinet_contract,
                ClarinetTools.write_clarity_contract,
                ClarinetTools.create_clarinet_project,
            ],  # Add relevant tools if any
            backstory=dedent(
                """
                You are an efficient and detail-oriented review expert, who remembers to look at both the big and small picture while meticulously finding errors or possible improvements.
                """
            ),
            verbose=True,
            **kwargs,
        )


####################
# TASKS
####################


class ClarityTasks:

    @staticmethod
    def write_clarity_code_task(agent, user_request):
        return Task(
            description=dedent(
                f"""
                Write Clarity code based on the following user request:

                **Request:** {user_request}

                Ensure the code is efficient, clean, and valid.
                """
            ),
            expected_output="Valid Clarity code that meets the user's request.",
            agent=agent,
        )

    @staticmethod
    def review_clarity_code_task(agent, clarity_code):
        return Task(
            description=dedent(
                f"""
                Review the following Clarity code for errors and improvements:

                **Clarity Code:** {clarity_code}

                Provide detailed feedback and suggestions for improvement.
                """
            ),
            expected_output="Detailed feedback on the Clarity code, including any errors and suggestions for improvement.",
            agent=agent,
        )

    @staticmethod
    def validate_clarity_code_task(agent, clarity_code):
        return Task(
            description=dedent(
                f"""
                Validate the following Clarity code using Clarinet:

                **Clarity Code:** {clarity_code}

                Ensure the code is valid and passes all checks.
                """
            ),
            expected_output="Validation results from Clarinet, including any errors or issues found.",
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

        write_code_task = ClarityTasks.write_clarity_code_task(
            clarity_writer, user_request
        )
        review_code_task = ClarityTasks.review_clarity_code_task(
            clarity_reviewer, write_code_task.expected_output
        )
        validate_code_task = ClarityTasks.validate_clarity_code_task(
            clarity_reviewer, write_code_task.expected_output
        )

        return Crew(
            agents=[
                clarity_writer,
                clarity_reviewer,
            ],
            tasks=[
                write_code_task,
                review_code_task,
                validate_code_task,
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    @staticmethod
    def render_clarity_code_crew():
        st.subheader("Clarity Code Generator and Validator")
        st.markdown(
            "This tool will generate and validate Clarity code based on your request."
        )

        with st.form("clarity_code_form"):
            user_request = st.text_area(
                "Request", help="Enter your request for Clarity code"
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

                result_str = str(result)
                st.markdown(result_str)

                st.download_button(
                    label="Download Clarity Code (Text)",
                    data=result_str,
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
