from crewai import Task
from textwrap import dedent

class SmartContractAnalysisTasks:

    def summarize_task(self, agent, contract_code):
        return Task(
            description=dedent(f"""
                Provide a comprehensive summary of the given smart contract's purpose.
                Contract Code:
                {contract_code}
                Your response should be a detailed paragraph providing what the codes and the functions are in the contract.
                Store your summary in the crew's shared memory with the key 'summary'.
            """),
            expected_output="A detailed paragraph summarizing the smart contract's purpose and main functions.",
            agent=agent
        )

    def analyze_task(self, agent, contract_functions):
        return Task(
            description=dedent(f"""
                Identify all public, private, and read-only functions, and indicate if they move funds.
                Contract Code:
                {contract_functions}
                Your response should be a detailed paragraph listing and describing each function, its visibility, and whether it moves funds.
                Store your analysis in the crew's shared memory with the key 'function_analysis'.
            """),
            expected_output="A detailed paragraph listing and describing each function, its visibility, and whether it moves funds.",
            agent=agent,
        )

    def updateable_task(self, agent, contract_functions):
        return Task(
            description=dedent(f"""
                Assess if any parts of the contract can be updated and by whom by checking the following contract. 
                {contract_functions}
                Your response should be a detailed paragraph explaining which parts of the contract are upgradeable, if any, 
                and who has the authority to make updates.
                Store your assessment in the crew's shared memory with the key 'updateability'.
            """),
            expected_output="A detailed paragraph explaining which parts of the contract are upgradeable and who can update them.",
            agent=agent,
        )
    
    def security_task(self, agent, contract_functions, contract_code):
        return Task(
            description=dedent(f"""
                Analyze the given smart contract code{contract_code } and its function: {contract_functions} to check if there is any potential security vulnerabilities like reentrancy, access control issues, integer overflow and underflow, unchecked return values from low-level calls, denial of service (DoS), bad randomness, time manipulation, and short address attacks. If there's any outline and show the security vulnerabilities.

                Store your analysis in the crew's shared memory with the key 'security_analysis'.
            """),
            expected_output="A list of SecurityVulnerability objects, each containing a description of the vulnerability, potential exploit, and potential issues.",
            agent=agent,
            tools=[]
        )

    def compiler_task(self, agent):
        return Task(
            description=dedent(f"""
                Compile all the output into a comprehensive final report.
                               
                Use the following information from the crew's shared memory to create a detailed report:
                1. Summary (Access this from the shared memory with the key 'summary')
                2. Functions Analysis (Access this from the shared memory with the key 'function_analysis')
                3. Updateability (Access this from the shared memory with the key 'updateability')
                4. Security (Access this from the shared memory with the key 'security_analysis')
            """),
            expected_output="A comprehensive final report integrating all analyses into a markdown.",
            agent=agent,
            async_execution=False
        )