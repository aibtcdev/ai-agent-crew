from crewai import Agent, Task, Crew
from langchain_ollama import ChatOllama
import os

os.environ["OPENAI_API_KEY"] = "NA"

llm = ChatOllama(model="llama3.1", base_url="http://localhost:11434")

general_agent = Agent(
    role="Math Professor",
    goal="""Provide the solution to the students that are asking mathematical questions and give them the answer.""",
    backstory="""You are an excellent math professor that likes to solve math questions in a way that everyone can understand your solution""",
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

task = Task(
    description="""what is 3 + 5""",
    agent=general_agent,
    expected_output="A numerical answer.",
)

crew = Crew(agents=[general_agent], tasks=[task], verbose=True)

result = crew.kickoff()

print(result)
