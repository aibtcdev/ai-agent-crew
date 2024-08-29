import requests
import streamlit as st
import time
from crewai import Agent, Crew, Process, Task
from crewai_tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from streamlit_mermaid import st_mermaid
from textwrap import dedent
from utils.scripts import BunScriptRunner
from utils.session import crew_step_callback, crew_task_callback
from utils.vector import (
    create_vector_search_tool,
    clarity_book_code_vector_store,
    clarity_book_function_vector_store,
)

####################
# HELPERS
####################


def parse_contract_identifier(identifier):
    parts = identifier.split(".")
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None


def fetch_contract_source(contract_address, contract_name):
    url = f"https://api.hiro.so/v2/contracts/source/{contract_address}/{contract_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("source")
    else:
        return f"Error: {response.status_code} - {response.text}"


def fetch_function(contract_address, contract_name):
    url = (
        f"https://api.hiro.so/v2/contracts/interface/{contract_address}/{contract_name}"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("functions")
    else:
        return f"Error: {response.status_code} - {response.text}"


diagram_llm = ChatOpenAI(model="gpt-4o")


def create_diagram(contract_code):
    prompt_template = """
    You are a visualization expert specializing in creating clear and informative flow diagrams using mermaid. Analyze the following Clarity smart contract code and its functions, then create a simplest mermaid code to visualize the internal control flow of the contract with correct syntax. Ensure the flow diagram code matches strictly with the documentation.

    This diagram should include:

    Nodes: Representing different functions and processes of the contract.
    Edges: Showing how the flow of execution moves between the functions.
    The code should be compatible with streamlit-mermaid version 0.2.0
    Contract Code:

    {contract_code}

    Generate only a simple Mermaid diagram code as text, nothing extra. Use appropriate colors and shapes to represent different elements in diagram. Ensure that the diagrams are clear and simplest.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    diagram_chain = prompt | diagram_llm

    response = diagram_chain.invoke({"contract_code": contract_code})

    diagram_code = response.content
    diagram_code = diagram_code.replace("`", "").replace("mermaid", "")

    return diagram_code


####################
# AGENTS
####################


class AIBTC_Agents:

    @staticmethod
    def get_contract_summarizer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Contract Summarizer",
            goal="Provide a comprehensive summary of the smart contract's purpose.",
            backstory="You are a blockchain analyst with expertise in understanding smart contract code in the Clarity language.",
            tools=[AIBTC_Tools.get_code_search_tool],
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def get_function_analyzer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Function Analyzer",
            goal="Identify all functions in the smart contract.",
            backstory="You are a smart contract developer with deep knowledge of function analysis in the Clarity language on the Stacks blockchain.",
            tools=[AIBTC_Tools.get_function_search_tool],
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def get_update_analyzer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Updateability Analyzer",
            goal=" Assess if any parts of the contract can be updated and by whom.",
            backstory="You are a smart contract auditor with expertise in contract governance and upgrade mechanisms in the Clarity language on the Stacks blockchain.",
            tools=[],
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def get_security_analyzer_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Security Analyzer",
            goal="Identify and explain potential security vulnerabilities in the contract",
            backstory="You are a blockchain security expert with a keen eye for detecting potential vulnerabilities in smart contracts in the Clarity language on the Stacks blockchain.",
            tools=[AIBTC_Tools.get_function_search_tool],
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def get_report_compiler_agent(llm=None):
        kwargs = {}
        if llm is not None:
            kwargs["llm"] = llm

        return Agent(
            role="Report Compiler",
            goal="Compile all output into a final report.",
            tools=[],
            backstory="You are a technical writer with expertise in creating clear and concise reports on complex blockchain topics in the Clarity language on the Stacks blockchain.",
            verbose=True,
            allow_delegation=False,
        )


####################
# TASKS
####################


class AIBTC_Tasks:

    # summarize_task
    @staticmethod
    def get_smart_contract_summary(agent, contract_code):
        return Task(
            description=dedent(
                f"""
                Provide a comprehensive summary of the given smart contract's purpose.
                Contract Code:
                {contract_code}
                Your response should be a detailed paragraph providing what the codes and the functions are in the contract.
                Store your summary in the crew's shared memory with the key 'summary'.
            """
            ),
            expected_output="A detailed paragraph summarizing the smart contract's purpose and main functions.",
            agent=agent,
        )

    # analyze_task
    @staticmethod
    def get_smart_contract_function_analysis(agent, contract_functions):
        return Task(
            description=dedent(
                f"""
                Identify all public, private, and read-only functions, and indicate if they move funds.
                Contract Code:
                {contract_functions}
                Your response should be a detailed paragraph listing and describing each function, its visibility, and whether it moves funds.
                Store your analysis in the crew's shared memory with the key 'function_analysis'.
            """
            ),
            expected_output="A detailed paragraph listing and describing each function, its visibility, and whether it moves funds.",
            agent=agent,
        )

    # updateable_task
    @staticmethod
    def get_smart_contract_updateability_analysis(agent, contract_functions):
        return Task(
            description=dedent(
                f"""
                Assess if any parts of the contract can be updated and by whom by checking the following contract. 
                {contract_functions}
                Your response should be a detailed paragraph explaining which parts of the contract are upgradeable, if any, 
                and who has the authority to make updates.
                Store your assessment in the crew's shared memory with the key 'updateability'.
            """
            ),
            expected_output="A detailed paragraph explaining which parts of the contract are upgradeable and who can update them.",
            agent=agent,
        )

    # security_task
    @staticmethod
    def get_smart_contract_security_analysis(agent, contract_functions, contract_code):
        return Task(
            description=dedent(
                f"""
                Analyze the given smart contract code{contract_code } and its function: {contract_functions} to check if there is any potential security vulnerabilities like reentrancy, access control issues, integer overflow and underflow, unchecked return values from low-level calls, denial of service (DoS), bad randomness, time manipulation, and short address attacks. If there's any outline and show the security vulnerabilities.

                Store your analysis in the crew's shared memory with the key 'security_analysis'.
            """
            ),
            expected_output="A list of SecurityVulnerability objects, each containing a description of the vulnerability, potential exploit, and potential issues.",
            agent=agent,
            tools=[],
        )

    # compiler_task
    @staticmethod
    def get_smart_contract_report(agent):
        return Task(
            description=dedent(
                f"""
                Compile all the output into a comprehensive final report.
                Use the following information from the crew's shared memory to create a detailed report:
                1. Summary (Access this from the shared memory with the key 'summary')
                2. Functions Analysis (Access this from the shared memory with the key 'function_analysis')
                3. Updateability (Access this from the shared memory with the key 'updateability')
                4. Security (Access this from the shared memory with the key 'security_analysis')
            """
            ),
            expected_output="A comprehensive final report integrating all analyses into a markdown.",
            agent=agent,
            async_execution=False,
        )


####################
# TOOLS
####################


class AIBTC_Tools:

    @staticmethod
    @tool("Get contract source code")
    def get_contract_source_code(contract_name: str):
        """Get the source code for a given contract. It must be the fully qualified name with ADDRESS.CONTRACT_NAME"""
        return BunScriptRunner.bun_run(
            "stacks-contracts", "get-contract-source-code.ts", contract_name
        )

    @staticmethod
    @tool("Get Clarity Code Search Tool")
    def get_code_search_tool():
        """Get the code search tool for the Clarity book with information about Clarity language syntax, types, and general concepts."""
        return create_vector_search_tool(
            clarity_book_code_vector_store,
            "Code Search",
            "Search for code snippets in the Clarity book.",
        )

    @staticmethod
    @tool("Get Clarity Function Search Tool")
    def get_function_search_tool():
        """Get the function search tool for the Clarity book with specific information about functions in Clarity language."""
        return create_vector_search_tool(
            clarity_book_function_vector_store,
            "Function Search",
            "Search for function documentation in the Clarity book.",
        )


####################
# CREW(S)
####################


class AIBTC_Crew:

    @staticmethod
    def create_smart_contract_analysis_crew(contract_code, contract_functions):
        contract_summarizer = AIBTC_Agents.get_contract_summarizer_agent()
        function_analyzer = AIBTC_Agents.get_function_analyzer_agent()
        updateability_analyzer = AIBTC_Agents.get_update_analyzer_agent()
        security_analyzer = AIBTC_Agents.get_security_analyzer_agent()
        report_compiler = AIBTC_Agents.get_report_compiler_agent()

        assigned_tasks = [
            AIBTC_Tasks.get_smart_contract_summary(contract_summarizer, contract_code),
            AIBTC_Tasks.get_smart_contract_function_analysis(
                function_analyzer, contract_functions
            ),
            AIBTC_Tasks.get_smart_contract_updateability_analysis(
                updateability_analyzer, contract_functions
            ),
            AIBTC_Tasks.get_smart_contract_security_analysis(
                security_analyzer, contract_code, contract_functions
            ),
            AIBTC_Tasks.get_smart_contract_report(report_compiler),
        ]

        return Crew(
            agents=[
                contract_summarizer,
                function_analyzer,
                updateability_analyzer,
                report_compiler,
            ],
            tasks=assigned_tasks,
            process=Process.sequential,
            memory=True,
            step_callback=crew_step_callback,
            task_callback=crew_task_callback,
        )

    @staticmethod
    def render_smart_contract_analysis_crew():
        st.subheader("Smart Contract Analyzer 🧠")
        st.markdown(
            "Analyze Stacks smart contracts with ease using AI-powered insights."
        )

        with st.form("analysis_form"):
            contract_identifier = st.text_input(
                "Contract Address",
                help="Enter the full contract identifier or just the address",
                placeholder="e.g. SP000000000000000000002Q6VF78.pox or SP000000000000000000002Q6VF78",
            )
            contract_name = st.text_input(
                "Contract Name",
                help="Enter the name of the deployed contract",
                placeholder="e.g. pox in SP000000000000000000002Q6VF78.pox",
            )
            submitted = st.form_submit_button("Analyze Contract")

        if submitted:
            parsed_address, parsed_name = parse_contract_identifier(contract_identifier)

            if parsed_address and parsed_name:
                contract_address = parsed_address
                contract_name = parsed_name
            elif "." not in contract_identifier:
                contract_address = contract_identifier
            else:
                st.error(
                    "Invalid contract identifier format. Please use 'address.name' or provide both fields separately."
                )
                st.stop()

            if not contract_address or not contract_name:
                st.error(
                    "Both contract address and name are required. Please provide both."
                )
                st.stop()

            with st.spinner("Fetching contract data..."):
                contract_code = fetch_contract_source(contract_address, contract_name)
                contract_functions = fetch_function(contract_address, contract_name)

            if isinstance(contract_code, str) and contract_code.startswith("Error"):
                st.error(f"Failed to fetch contract code: {contract_code}")
            elif isinstance(contract_functions, str) and contract_functions.startswith(
                "Error"
            ):
                st.error(f"Failed to fetch contract functions: {contract_functions}")
            else:
                with st.expander("View Contract Code"):
                    st.download_button(
                        label="Download Smart Contract Code",
                        data=contract_code,
                        file_name=f"{contract_address}.{contract_name}.clar",
                        mime="text/plain",
                    )
                    st.write("Source code:")
                    st.code(contract_code)

                st.header("Analysis Results")
                try:
                    # create containers for real-time updates
                    st.write("Step Progress:")
                    st.session_state.crew_step_container = st.empty()
                    st.write("Task Progress:")
                    st.session_state.crew_task_container = st.empty()

                    # reset callback lists
                    st.session_state.crew_step_callback = []
                    st.session_state.crew_task_callback = []

                    crew = AIBTC_Crew.create_smart_contract_analysis_crew(
                        contract_code, contract_functions
                    )

                    with st.spinner("Analyzing..."):
                        result = crew.kickoff()

                    st.success("Analysis complete!")

                    result_str = str(result)
                    st.markdown(result_str)

                    diagram_placeholder = st.empty()

                    with st.spinner("Generating diagram..."):
                        diagram_code = create_diagram(contract_code)

                    diagram_placeholder.markdown("### Control flow Diagram")
                    diagram_placeholder.code(diagram_code)
                    st.header("Flow Diagram")
                    st_mermaid(diagram_code, key="contract_diagram", height="1000px")

                    st.download_button(
                        label="Download Analysis Report (Text)",
                        data=result_str,
                        file_name="smart_contract_analysis.txt",
                        mime="text/plain",
                    )

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Please check your inputs and try again.")
        else:
            st.info(
                "Enter Contract Address and Contract Name, then click 'Analyze Contract' to see results."
            )
