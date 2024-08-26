from langchain_ollama import ChatOllama
import streamlit as st
from crewai import Crew, Process
from crew_ai.agents import WalletAnalysisAgents
from crew_ai.tasks import WalletAnalysisTasks
import os
import time

# os.environ["OPENAI_API_BASE"] = "http://localhost:11434"
# os.environ["OPENAI_MODEL_NAME"] = "llama3.1"  # Specify your custom model
os.environ["OPENAI_API_KEY"] = ""  # No API Key required for Ollama


def create_wallet_analysis_crew(address):

    agents = WalletAnalysisAgents()
    tasks = WalletAnalysisTasks()
    wallet_retriever = agents.wallet_data_retriever_agent()
    transaction_retriever = agents.transaction_retriever_agent()
    activity_analyzer = agents.activity_analyzer_agent()
    # security_analyzer = agents.security_analyzer_agent()
    report_compiler = agents.report_compiler_agent()

    task1 = tasks.retrieve_wallet_info_task(wallet_retriever, address)
    task2 = tasks.retrieve_transactions_task(transaction_retriever, address)
    task3 = tasks.analyze_activity_task(activity_analyzer, address)
    task4 = tasks.compile_report_task(report_compiler, address)

    crew = Crew(
        agents=[
            wallet_retriever,
            transaction_retriever,
            activity_analyzer,
            report_compiler,
        ],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True,
        planning=False,
        planning_llm=ChatOllama(model="llama3.1", base_url="http://localhost:11434"),
        memory=False,
        embedder={
            "provider": "huggingface",
            "config": {
                "model": "mixedbread-ai/mxbai-embed-large-v1",  # https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1
            },
        },
    )
    return crew


def main():
    st.set_page_config(page_title="Wallet Analyzer", page_icon="", layout="wide")

    st.title("Wallet Analyzer 🧠")
    st.markdown("Analyze Stacks Wallet addresses with ease using AI-powered insights.")

    with st.form("analysis_form"):
        address = st.text_input("Address", help="Enter the wallet address")
        submitted = st.form_submit_button("Analyze Wallet")

    if submitted and address:
        st.header("Analysis Results")
        try:
            crew = create_wallet_analysis_crew(address)
            progress_bar = st.progress(0)

            with st.spinner("Analyzing..."):
                result = crew.kickoff()

                for i in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(i + 1)

            st.success("Analysis complete!")

            result_str = str(result)
            st.markdown(result_str)

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
        st.info("Enter Wallet Address, then click 'Analyze Wallet' to see results.")

    st.sidebar.header("Credits")
    st.sidebar.markdown(
        """
    - ***Find me on X:***
        - [@human058382928](https://x.com/human058382928)
    """
    )


if __name__ == "__main__":
    main()
