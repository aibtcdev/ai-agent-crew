from crewai import Crew, Process, Task
from agents import MeetingsCrew

# set global vars

from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

# set global llm

from langchain_openai import ChatOpenAI

default_llm = ChatOpenAI(
    model="gpt-4o"
    # model="gpt-4-turbo-preview"
    # model="gpt-3.5-turbo-0125"
)


def create_research_task(url, context):
    return Task(
        description=(f"Fetch information from the URL: {url}. " f"Context: {context}"),
        expected_output="Raw content from the URL",
        agent=MeetingsCrew.meeting_researcher(),
    )


def create_extraction_task(raw_content):
    return Task(
        description=(
            "Extract relevant content from the provided raw data. "
            "Focus on identifying the key points and important information."
            f"Raw content: {raw_content}"
        ),
        expected_output="Relevant content extracted from the raw data",
        agent=MeetingsCrew.content_extractor(),
    )


def create_writing_task(extracted_content, url):
    return Task(
        description=(
            "Summarize the extracted information into bullet points and format it as a markdown file. "
            "Include relevant links and context."
            f"URL: {url}"
            f"Extracted content: {extracted_content}"
        ),
        expected_output="A markdown file with a summary of the information",
        agent=MeetingsCrew.meeting_writer(),
    )


def create_all_tasks(urls_with_contexts):
    tasks = []
    for url, context in urls_with_contexts:
        research_task = create_research_task(url, context)
        extraction_task = create_extraction_task(research_task.expected_output)
        writing_task = create_writing_task(extraction_task.expected_output, url)
        tasks.extend([research_task, extraction_task, writing_task])
    return tasks


def engage_crew_with_tasks(urls_with_contexts):
    # Define the tasks
    all_tasks = create_all_tasks(urls_with_contexts)

    # Create a crew
    info_gathering_crew = Crew(
        agents=[
            MeetingsCrew.meeting_researcher(),
            MeetingsCrew.content_extractor(),
            MeetingsCrew.meeting_writer(),
        ],
        process=Process.sequential,
        tasks=all_tasks,
        verbose=2,
    )

    # Run the crew against all tasks
    crew_result = info_gathering_crew.kickoff()

    # Print the result
    print("--------------------------------------------------")
    print("Information Gathering Crew Final Result:")
    print(crew_result)
    print("--------------------------------------------------")


if __name__ == "__main__":
    urls_with_contexts = [
        ("https://openai.com/index/hello-gpt-4o/", "New LLM model release"),
        (
            "https://github.com/jina-ai/reader/)",
            "",
        ),
        ("https://www.reddit.com/r/ai/", "AI news and discussions"),
        ("https://www.reddit.com/r/LocalLLaMA/", "Local LLAMA community"),
    ]
    engage_crew_with_tasks(urls_with_contexts)
