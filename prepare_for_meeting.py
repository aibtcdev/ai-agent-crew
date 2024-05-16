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

# setup news list to be built by the crew

news_list = []


def build_news_list(output):
    news_list.append(
        {"description": output.description, "raw_output": output.raw_output}
    )


# define the tasks


def create_research_task(url, context):
    return Task(
        description=(
            f"Fetch information from the URL: {url}. "
            f"Context: {context}. "
            "Open the link and summarize key points in the article, especially focusing on crypto and AI if mentioned. "
            "Create a short sentence that represents the content."
        ),
        expected_output="Raw content from the URL, including a short sentence summary",
        agent=MeetingsCrew.meeting_researcher(),
    )


def create_extraction_task(raw_content):
    return Task(
        description=(
            "Extract relevant content from the provided raw data. "
            "Focus on identifying the key points and important information. "
            "Create 4-5 bullet points that represent the key points."
            f"Raw data: {raw_content}"
        ),
        expected_output="Relevant content extracted from the raw data in bullet points",
        agent=MeetingsCrew.content_extractor(),
    )


def create_writing_task(extracted_content, url):
    return Task(
        description=(
            "Summarize the extracted information into bullet points and format it as a markdown file. "
            "Include relevant links and context. "
            "Ensure the summary is concise and informative."
            f"URL: {url}"
            f"Extracted content: {extracted_content}. "
        ),
        expected_output="A markdown file with a summary of all the information",
        agent=MeetingsCrew.meeting_writer(),
        callback=build_news_list,
    )


# aggregate the tasks into a list


def create_all_tasks(urls_with_contexts):
    tasks = []
    for url, context in urls_with_contexts:
        research_task = create_research_task(url, context)
        extraction_task = create_extraction_task(research_task.expected_output)
        writing_task = create_writing_task(extraction_task.expected_output, url)
        tasks.extend([research_task, extraction_task, writing_task])
    return tasks


# define the crew and run the tasks


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
    info_gathering_crew.kickoff()

    # print news list for debug
    print("--------------------------------------------------")
    print("News List:")
    print(news_list)
    print("--------------------------------------------------")

    # Create a 2nd crew to review all the content in the news_list
    agenda_preparation_crew = Crew(
        agents=[MeetingsCrew.meeting_writer()],
        process=Process.sequential,
        tasks=[
            Task(
                description=(
                    f"Review the content from the news list. "
                    "Summarize the key points and create a markdown file with all the information."
                ),
                expected_output="A markdown file with a summary of all the information",
            )
        ],
        verbose=2,
    )

    # Run the crew against all tasks
    crew_result = agenda_preparation_crew.kickoff(news_list)

    # Print the result
    print("--------------------------------------------------")
    print("Information Gathering Crew Final Result:")
    print(crew_result)
    print("--------------------------------------------------")


if __name__ == "__main__":
    urls_with_contexts = [
        ("https://www.reddit.com/r/LocalLLaMA/", "Local LLAMA community"),
        (
            "https://x.com/_philschmid/status/1789999841579315705?t=iutbHiG30u8Xj6zBkTqmkQ&s=09",
            "new model release",
        ),
        (
            "https://x.com/AlphaSignalAI/status/1790070779813433589?t=m5TY8PEfbKqCyY4nPoI6yA&s=09",
            "new model release",
        ),
    ]
    engage_crew_with_tasks(urls_with_contexts)
