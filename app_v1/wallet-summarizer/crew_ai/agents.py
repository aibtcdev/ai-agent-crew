from textwrap import dedent
from crewai import Agent
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from crew_ai.tools import StacksWalletTools


llm = ChatOllama(model="gemma2", base_url="http://localhost:11434")
# llm = ChatOpenAI(
#     model="gpt-4o",
#     openai_api_key="",
# )


class WalletAnalysisAgents:

    def wallet_data_retriever_agent(self):
        return Agent(
            role="wallet data retriever",
            goal="Retrieve basic wallet information from a single tool call.",
            tools=[StacksWalletTools.get_address_balance_detailed],
            backstory=dedent(
                """
                You are a blockchain data analyst specializing in wallet activity on the Stacks blockchain."""
            ),
            llm=llm,
            verbose=True,
        )

    def transaction_retriever_agent(self):
        return Agent(
            role="transaction retriever",
            goal="Retrieve the last 20 transactions for the specified wallet, if available.",
            tools=[StacksWalletTools.get_address_transactions],
            backstory=dedent(
                """
               You are an expert in blockchain transaction analysis, capable of efficiently querying and filtering large data sets."""
            ),
            llm=llm,
            verbose=True,
        )

    def activity_analyzer_agent(self):
        return Agent(
            role="activity analyzer",
            goal="Analyze the retrieved data to determine the type of activity the wallet is usually involved in, such as frequent transactions, holding patterns, and interaction with contracts.",
            tools=[],
            backstory=dedent(
                """
               You are a blockchain activity analyst with expertise in behavioral analysis on the Stacks blockchain. """
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def report_compiler_agent(self):
        return Agent(
            role="report compiler",
            goal="Compile all output into a final report.",
            tools=[],
            backstory=dedent(
                """
               You are a technical writer with expertise in creating clear and concise reports on complex blockchain topics in the Clarity language on the Stacks blockchain."""
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
