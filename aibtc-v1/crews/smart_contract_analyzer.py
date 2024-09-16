import inspect
import re
import requests
import streamlit as st
from crewai import Agent, Task
from crewai_tools import tool, Tool
from streamlit_mermaid import st_mermaid
from textwrap import dedent
from utils.crews import AIBTC_Crew, display_token_usage
from utils.scripts import BunScriptRunner, get_timestamp
from utils.vector import (
    create_vector_search_tool,
    clarity_book_code_vector_store,
    clarity_book_function_vector_store,
)


class SmartContractAnalyzerCrew(AIBTC_Crew):
    def __init__(self):
        super().__init__("Smart Contract Analyzer")

    def setup_agents(self, llm):
        contract_summarizer = Agent(
            role="Contract Summarizer",
            goal="Provide a comprehensive summary of the smart contract's purpose.",
            backstory="You are a blockchain analyst with expertise in understanding smart contract code in the Clarity language.",
            tools=[AgentTools.get_code_search_tool],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(contract_summarizer)

        function_analyzer = Agent(
            role="Function Analyzer",
            goal="Identify all functions in the smart contract.",
            backstory="You are a smart contract developer with deep knowledge of function analysis in the Clarity language on the Stacks blockchain.",
            tools=[AgentTools.get_function_search_tool],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(function_analyzer)

        updateability_analyzer = Agent(
            role="Updateability Analyzer",
            goal=" Assess if any parts of the contract can be updated and by whom.",
            backstory="You are a smart contract auditor with expertise in contract governance and upgrade mechanisms in the Clarity language on the Stacks blockchain.",
            tools=[],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(updateability_analyzer)

        security_analyzer = Agent(
            role="Security Analyzer",
            goal="Identify and explain potential security vulnerabilities in the contract",
            backstory="You are a blockchain security expert with a keen eye for detecting potential vulnerabilities in smart contracts in the Clarity language on the Stacks blockchain.",
            tools=[AgentTools.get_function_search_tool],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(security_analyzer)

        report_compiler = Agent(
            role="Report Compiler",
            goal="Compile all output into a final report.",
            tools=[],
            backstory="You are a technical writer with expertise in creating clear and concise reports on complex blockchain topics in the Clarity language on the Stacks blockchain.",
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(report_compiler)

        diagram_creator = Agent(
            role="Diagram Creator",
            goal="Create a clear and informative flow diagram of the smart contract using mermaid syntax.",
            backstory="You are a visualization expert specializing in creating clear and informative flow diagrams for Clarity smart contracts.",
            tools=[],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )
        self.add_agent(diagram_creator)

    def setup_tasks(self, contract_code, contract_functions):
        summarize_contract_task = Task(
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
            agent=self.agents[0],  # contract_summarizer
        )
        self.add_task(summarize_contract_task)

        analyze_functions_task = Task(
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
            agent=self.agents[1],  # function_analyzer
        )
        self.add_task(analyze_functions_task)

        analyze_updateability_task = Task(
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
            agent=self.agents[2],  # updateability_analyzer
        )
        self.add_task(analyze_updateability_task)

        analyze_security_task = Task(
            description=dedent(
                f"""
                Analyze the given smart contract code{contract_code } and its function: {contract_functions} to check if there is any potential security vulnerabilities like reentrancy, access control issues, integer overflow and underflow, unchecked return values from low-level calls, denial of service (DoS), bad randomness, time manipulation, and short address attacks. If there's any outline and show the security vulnerabilities.

                Store your analysis in the crew's shared memory with the key 'security_analysis'.
            """
            ),
            expected_output="A list of SecurityVulnerability objects, each containing a description of the vulnerability, potential exploit, and potential issues.",
            agent=self.agents[3],  # security_analyzer
            tools=[],
        )
        self.add_task(analyze_security_task)

        create_diagram_task = Task(
            description=dedent(
                f"""
                Analyze the following Clarity smart contract code and create a mermaid diagram to visualize the internal control flow of the contract.
                Contract Code:
                {contract_code}
                Your response should be a mermaid diagram code that represents the contract's flow.
                Ensure the diagram includes:
                1. Nodes representing different functions and processes of the contract.
                2. Edges showing how the flow of execution moves between the functions.
                3. Appropriate colors and shapes to represent different elements.
                The code should be compatible with streamlit-mermaid version 0.2.0.
                Store your diagram code in the crew's shared memory with the key 'contract_diagram'.
                """
            ),
            expected_output="A mermaid diagram code representing the smart contract's flow.",
            agent=self.agents[5],  # diagram_creator
            callback=diagram_callback,
        )
        self.add_task(create_diagram_task)

        smart_contract_report_task = Task(
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
            agent=self.agents[4],  # report_compiler
            async_execution=False,
        )
        self.add_task(smart_contract_report_task)

    @staticmethod
    def get_task_inputs():
        return ["contract_code", "contract_functions"]

    @classmethod
    def get_all_tools(cls):
        return AgentTools.get_all_tools()

    def render_crew(self):
        st.subheader("Smart Contract Analyzer 🧠")
        st.markdown(
            "Analyze Stacks smart contracts with ease using AI-powered insights."
        )

        with st.form("analysis_form"):
            contract_identifier = st.text_input(
                "Contract Identifier",
                help="Enter the full contract identifier including address and name.",
                placeholder="e.g. SP000000000000000000002Q6VF78.pox",
            )
            submitted = st.form_submit_button("Analyze Contract")

        if submitted and contract_identifier:
            parsed_address, parsed_name = parse_contract_identifier(contract_identifier)

            if parsed_address and parsed_name:
                contract_address = parsed_address
                contract_name = parsed_name
            else:
                st.error(
                    "Invalid contract identifier format. Please use 'address.name' format."
                )
                st.stop()

            if not contract_address or not contract_name:
                st.error(
                    "Both contract address and name are required. Please use 'address.name' format."
                )
                st.stop()

            with st.spinner("Fetching contract data..."):
                contract_code = fetch_contract_source(contract_address, contract_name)
                contract_functions = fetch_contract_functions(
                    contract_address, contract_name
                )

            if isinstance(contract_code, str) and contract_code.startswith("Error"):
                st.error(f"Failed to fetch contract code: {contract_code}")
            elif isinstance(contract_functions, str) and contract_functions.startswith(
                "Error"
            ):
                st.error(f"Failed to fetch contract functions: {contract_functions}")
            else:
                timestamp = get_timestamp()

                with st.expander("View Contract Code"):
                    st.download_button(
                        label="Download Smart Contract Code",
                        data=contract_code,
                        file_name=f"{timestamp}_{contract_address}.{contract_name}.clar",
                        mime="text/plain",
                    )
                    st.write("Source code:")
                    st.code(contract_code)

            st.subheader("Analysis Progress")
            try:
                # create containers for real-time updates
                st.write("Step Progress:")
                st.session_state.crew_step_container = st.empty()
                st.write("Task Progress:")
                st.session_state.crew_task_container = st.empty()
                st.write("Contract Diagram:")
                st.session_state.crew_diagram_container = st.empty()

                # reset callback lists
                st.session_state.crew_step_callback = []
                st.session_state.crew_task_callback = []

                # get LLM from session state
                llm = st.session_state.llm
                smart_contract_analyzer_crew_class = SmartContractAnalyzerCrew()
                smart_contract_analyzer_crew_class.setup_agents(llm)
                smart_contract_analyzer_crew_class.setup_tasks(
                    contract_code, contract_functions
                )
                smart_contract_analyzer_crew = (
                    smart_contract_analyzer_crew_class.create_crew()
                )

                with st.spinner("Analyzing..."):
                    result = smart_contract_analyzer_crew.kickoff()

                st.success("Analysis complete!")

                display_token_usage(result.token_usage)

                st.subheader("Analysis Results")

                result_str = str(result.raw)
                st.markdown(result_str)

                timestamp = get_timestamp()

                st.download_button(
                    label="Download Analysis Report (Text)",
                    data=result_str,
                    file_name=f"{timestamp}_smart_contract_analysis.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your inputs and try again.")
        else:
            st.write(
                "Enter Contract Address and Contract Name, then click 'Analyze Contract' to see results."
            )


#########################
# Agent Tools
#########################


class AgentTools:

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


#########################
# Helper Functions
#########################


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


def fetch_contract_functions(contract_address, contract_name):
    url = (
        f"https://api.hiro.so/v2/contracts/interface/{contract_address}/{contract_name}"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("functions")
    else:
        return f"Error: {response.status_code} - {response.text}"


def diagram_callback(output):
    # Regular expression to find content between ```mermaid and ``` tags
    mermaid_pattern = r"```mermaid\n(.*?)\n```"
    match = re.search(mermaid_pattern, output.raw, re.DOTALL)

    if match:
        # Extract the mermaid code
        mermaid_code = match.group(1).strip()
        # Create a new subheader and render the mermaid diagram
        with st.session_state.crew_diagram_container:
            st.subheader("Contract Flow Diagram")
            st_mermaid(mermaid_code)
    else:
        # Display a message if no mermaid diagram is found
        st.session_state.crew_diagram_container.info(
            "No mermaid diagram found in the output."
        )
