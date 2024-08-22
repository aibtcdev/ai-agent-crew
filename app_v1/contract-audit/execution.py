import sys
sys.modules['sqlite3'] = __import__('pysqlite3')
import time
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from streamlit_mermaid import st_mermaid
from crewai import Crew, Process
from crew_ai.agents import SmartContractAnalysisAgents
from crew_ai.tasks import SmartContractAnalysisTasks
from utils.contract_fetcher import fetch_contract_source, fetch_function
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

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
    diagram_chain = prompt | llm
    
    response = diagram_chain.invoke({"contract_code": contract_code})
    
    diagram_code = response.content
    diagram_code = diagram_code.replace("`", "").replace("mermaid", "")
    
    return diagram_code

def create_smart_contract_analysis_crew(contract_code, contract_functions):
    agents = SmartContractAnalysisAgents()
    tasks = SmartContractAnalysisTasks()

    contract_summarizer = agents.contract_summarizer_agent()
    function_analyzer = agents.function_analyzer_agent()
    updateability_analyzer = agents.update_analyzer_agent()
    security_analyzer = agents.security_analyzer_agent()
    report_compiler = agents.report_compiler_agent()

    task1 = tasks.summarize_task(contract_summarizer, contract_code)
    task2 = tasks.analyze_task(function_analyzer, contract_functions)
    task4 = tasks.updateable_task(updateability_analyzer, contract_functions)
    task5 = tasks.security_task(security_analyzer, contract_code, contract_functions)
    task6 = tasks.compiler_task(report_compiler)

    crew = Crew(
        agents=[contract_summarizer, function_analyzer, updateability_analyzer, report_compiler],
        tasks=[task1, task2, task4, task5, task6],
        process=Process.sequential,
        memory=True
    )

    return crew

def main():
    st.set_page_config(page_title="Smart Contract Analyzer", page_icon="", layout="wide")
    
    st.title("Smart Contract Analyzer 🧠")
    st.markdown("Analyze Stacks smart contracts with ease using AI-powered insights.")

    with st.form("analysis_form"):
        contract_address = st.text_input("Contract Address", help="Enter the unique identifier for the contract", placeholder="e.g. SP000000000000000000002Q6VF78.pox")
        contract_name = st.text_input("Contract Name", help="Enter the name of the contract")
        submitted = st.form_submit_button("Analyze Contract")

    if submitted and contract_address and contract_name:
        with st.spinner("Fetching contract data..."):
            contract_code = fetch_contract_source(contract_address, contract_name)
            contract_functions = fetch_function(contract_address, contract_name)
        
        if isinstance(contract_code, str) and contract_code.startswith("Error"):
            st.error(f"Failed to fetch contract code: {contract_code}")
        elif isinstance(contract_functions, str) and contract_functions.startswith("Error"):
            st.error(f"Failed to fetch contract functions: {contract_functions}")
        else:
            with st.expander("View Contract Code"):
                st.code(contract_code)

            st.header("Analysis Results")
            try:
                crew = create_smart_contract_analysis_crew(contract_code, contract_functions)
                
                progress_bar = st.progress(0)
                
                with st.spinner("Analyzing..."):
                    result = crew.kickoff()
                    for i in range(100):
                        time.sleep(0.05)  
                        progress_bar.progress(i + 1)
                
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
        st.info("Enter Contract Address and Contract Name, then click 'Analyze Contract' to see results.")

    st.sidebar.header("Credits")
    st.sidebar.markdown("""
    - **Resources and inspirations for this project:**
        - [CREW AI](https://www.crewai.com/)
        - [Langchain](https://python.langchain.com/v0.2/docs/introduction/)
        - [Streamlit-Mermaid](https://libraries.io/pypi/streamlit-mermaid)
        - [Hiro Stacks](https://docs.hiro.so/stacks)
        - [Streamlit](https://streamlit.io/)
        - [AIBTC](https://aibtc.dev/)
    - **Special thanks to:**
        - Binaya Tripathi: [@binaya_btc](https://x.com/binaya_btc)
    - ***Find me on X:***
        - Biwas Bhandari: [@biwasbhandarii](https://x.com/biwasbhandarii)
    """)
    
    st.sidebar.header("Sample Audit")
    st.sidebar.markdown("""
    You can view a sample audit report [here](https://drive.google.com/file/d/1eG2xLoaFhpBUg47jIn4AVflOUqXwCbfN/view?usp=sharing).
    """)

if __name__ == "__main__":
    main()