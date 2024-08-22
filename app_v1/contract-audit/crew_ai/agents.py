from textwrap import dedent
from crewai import Agent
from crew_ai.mytool import code_search_tool, function_search_tool


class SmartContractAnalysisAgents:

    def contract_summarizer_agent(self):
        return Agent(
            role="contract summarizer",
            goal="Provide a comprehensive summary of the smart contract's purpose.",
            tools=[code_search_tool],
            backstory=dedent(
                """
                You are a blockchain analyst with expertise in understanding smart contract code in the Clarity language."""
            ),
            verbose=True,
        )

    def function_analyzer_agent(self):
        return Agent(
            role="function analyzer",
            goal="Identify all functions in the smart contract.",
            tools=[function_search_tool],
            backstory=dedent(
                """
               You are a smart contract developer with deep knowledge of function analysis in the Clarity language on the Stacks blockchain."""
            ),
            verbose=True,
        )

    def update_analyzer_agent(self):
        return Agent(
            role="updateability analyzer",
            goal=" Assess if any parts of the contract can be updated and by whom.",
            tools=[],
            backstory=dedent(
                """
               You are a smart contract auditor with expertise in contract governance and upgrade mechanisms in the Clarity language on the Stacks blockchain."""
            ),
            verbose=True,
            allow_delegation=False,
        )

    def security_analyzer_agent(self):
        return Agent(
            role="security analyzer",
            goal="Identify and explain potential security vulnerabilities in the contract",
            tools=[function_search_tool],
            backstory=dedent(
                """
               You are a blockchain security expert with a keen eye for detecting potential vulnerabilities in smart contracts in the Clarity language on the Stacks blockchain."""
            ),
            verbose=True,
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
            verbose=True,
            allow_delegation=False,
        )
