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
    news_list.append({"news_list_item": output.raw_output})


# define the tasks


# 1. scrape website, get as much useful content as possible
def create_research_task(url):
    return Task(
        description=(
            f"Fetch information from the URL: {url}."
            "Fetch all the raw content from the URL, including any relevant information that can be used to create a summary."
        ),
        expected_output="Raw content from the URL excluding any HTML code.",
        agent=MeetingsCrew.website_scraper(),
    )


# 2. extract website content into bullet point list
def create_extraction_task(raw_content):
    return Task(
        description=(
            "Extract relevant content from the provided raw data. "
            "Focus on identifying the key points and important information. "
            "Create 5 bullet points that represent the key points. "
            "Ensure the extracted content is concise and informative. "
            f"Raw data: {raw_content}"
        ),
        expected_output="Relevant content extracted from the raw data in bullet points",
        agent=MeetingsCrew.meeting_writer(),
        callback=build_news_list,  # used by 2nd crew
    )


# unused for now, will revisit
def create_writing_task(extracted_content, url):
    return Task(
        description=(
            "Create a markdown file with a summary of all extracted content. "
            "Include relevant links and context. "
            "Ensure the summary is concise and informative."
            f"URL: {url}"
            f"Extracted content: {extracted_content}. "
        ),
        expected_output="A markdown file with a summary of all the information",
        agent=MeetingsCrew.meeting_writer(),
    )


# aggregate the tasks into a list


def create_all_tasks(url_list):
    tasks = []
    for url in url_list:
        research_task = create_research_task(url)
        # need to chain the outputs here, not the expected output
        extraction_task = create_extraction_task(research_task.expected_output)
        tasks.extend([research_task, extraction_task])
    return tasks


# define the crew and run the tasks


def engage_crew_with_tasks(url_list):
    # Define the tasks
    all_tasks = create_all_tasks(url_list)

    # Create a crew
    info_gathering_crew = Crew(
        agents=[
            MeetingsCrew.website_scraper(),
            MeetingsCrew.meeting_writer(),
        ],
        process=Process.sequential,
        tasks=all_tasks,
        verbose=0,
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
                    f"Review the content from the news list: {news_list}. "
                    "Summarize the key points and create a markdown file with all the information."
                ),
                expected_output="A markdown file with each news item on it's own line and a bullet point summary of all the related information. The first line should summarize the news content and link to the original source.",
                agent=MeetingsCrew.meeting_writer(),
            )
        ],
        verbose=2,
    )

    # Run the crew against all tasks
    crew_result = agenda_preparation_crew.kickoff()

    # Print the result
    print("--------------------------------------------------")
    print("Information Gathering Crew Final Result:")
    print(crew_result)
    print("--------------------------------------------------")

    # Create a YYYY-MM-DD-HH-MM timestamp
    from datetime import datetime

    file_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")

    # create generated-meeting-agenda.md file with the result
    with open(f"agendas/{file_timestamp}-generated-meeting-agenda.md", "w") as file:
        file.write("# News List\n")
        for item in news_list:
            file.write(f"- {item['news_list_item']}\n")
        file.write("## Latest AI News\n")
        file.write(crew_result)


if __name__ == "__main__":
    url_list = [
        "https://x.com/chiefaioffice/status/1793407809847275864",
        "https://x.com/ritakozlov_/status/1793267209441042917",
        "https://x.com/ilblackdragon/status/1793265661839339873",
        "https://x.com/ksaitor/status/1793594843559854536",
        "https://x.com/petergyang/status/1793480607198323196",
    ]
    engage_crew_with_tasks(url_list)
