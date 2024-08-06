from crewai import Crew, Process, Task
from crewai.tasks import TaskOutput
from agents import MeetingsCrew
from news_examples import good_example, bad_example

from dotenv import load_dotenv
from langchain.globals import set_debug

load_dotenv()
set_debug(False)

from langchain_openai import ChatOpenAI

default_llm = ChatOpenAI(model="gpt-4o")

scraped_content_list = []
key_points_list = []
news_list = []


def build_scraped_content_list(crew_output: TaskOutput):
    scraped_content_list.append(crew_output.raw_output)


def build_key_points_list(crew_output: TaskOutput):
    key_points_list.append(crew_output.raw_output)


def build_news_list(url, content, summary):
    news_item = {"url": url, "content": content, "summary": summary}
    news_list.append(news_item)


def create_scrape_website_task(url):
    return Task(
        description=(
            f"Provided URL: {url}. Fetch the contents of this tweet and return the raw content for use in a later step. "
            "Ensure you extract all relevant text content from the tweet without any HTML tags or extraneous information."
        ),
        expected_output="The entire contents of the tweet excluding any HTML code. Example: 'Tweet content here.'",
        agent=MeetingsCrew.website_scraper(),
        callback=build_scraped_content_list,
    )


def create_extract_key_points_task(url, scrape_task: Task):
    return Task(
        description=(
            "Using the tweet content, extract key points focusing on the most important information. "
            "Summarize the tweet in 1-2 sentences and format it according to the provided good example. "
            "Ensure the summary sentence includes a link to the original tweet in markdown format, and format any supporting points as bullet points."
        ),
        expected_output="Key points extracted from the tweet content, including the summary sentence with a markdown link to the original tweet. Example: 'Summary sentence [tweet_author](tweet_url).'",
        agent=MeetingsCrew.meeting_writer(),
        context=[scrape_task],
        callback=build_key_points_list,
    )


def create_task_list(url_list):
    tasks = []
    for url in url_list:
        scrape_task = create_scrape_website_task(url)
        tasks.append(scrape_task)
        extract_key_points_task = create_extract_key_points_task(url, scrape_task)
        tasks.append(extract_key_points_task)
    return tasks


def format_news_item(url, content, summary):
    tweet_author = url.split("/")[3]
    formatted_item = f"{summary} [{tweet_author}]({url})\n\n"
    if "-" in content:
        bullet_points = content.split("- ")[1:]
        for point in bullet_points:
            formatted_item += f"- {point.strip()}\n"
    return formatted_item


def engage_crew_with_tasks(url_list):
    task_list = create_task_list(url_list)

    info_gathering_crew = Crew(
        agents=[
            MeetingsCrew.website_scraper(),
            MeetingsCrew.meeting_writer(),
        ],
        process=Process.sequential,
        tasks=task_list,
        verbose=0,
    )

    info_gathering_crew.kickoff()

    print("--------------------------------------------------")
    print(f"URL List: {len(url_list)} items.")
    print(url_list)
    print("--------------------------------------------------")

    print("--------------------------------------------------")
    print(f"Scraped Content List: {len(scraped_content_list)} items.")
    print(scraped_content_list)
    print("--------------------------------------------------")

    print("--------------------------------------------------")
    print(f"Key Points List: {len(key_points_list)} items.")
    print(key_points_list)
    print("--------------------------------------------------")

    for i in range(len(url_list)):
        build_news_list(url_list[i], scraped_content_list[i], key_points_list[i])

    print("--------------------------------------------------")
    print("News List:")
    print(news_list)
    print("--------------------------------------------------")

    formatted_news_list = ""
    for item in news_list:
        formatted_news_list += format_news_item(
            item["url"], item["content"], item["summary"]
        )

    agenda_preparation_crew = Crew(
        agents=[MeetingsCrew.meeting_writer()],
        process=Process.sequential,
        tasks=[
            Task(
                description=(
                    "The provided news list contains a URL, scraped content, and generated summary for each news item."
                    "Your job is to review all of the news items and create a markdown file with a summary of the key points extracted from the tweets."
                    "Ensure that the format adheres to the good example provided below and avoid the issues in the bad example."
                    "[START GOOD EXAMPLE]"
                    f"{good_example}"
                    "[END GOOD EXAMPLE]"
                    "[START BAD EXAMPLE]"
                    f"{bad_example}"
                    "[END BAD EXAMPLE]"
                    "[START NEWS LIST]"
                    f"{formatted_news_list}"
                    "[END NEWS LIST]"
                ),
                expected_output=(
                    "A markdown file with the L3 heading 'Latest AI News' and a bullet point summary of all the related information from each tweet. Example: 'Summary sentence [tweet_author](tweet_url).'"
                ),
                agent=MeetingsCrew.meeting_writer(),
            )
        ],
        verbose=2,
    )

    crew_result = agenda_preparation_crew.kickoff()

    print("--------------------------------------------------")
    print("Meeting Agenda Preparation Crew Final Result:")
    print(crew_result)
    print("--------------------------------------------------")

    from datetime import datetime

    file_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")

    with open(f"agendas/{file_timestamp}-generated-meeting-agenda.md", "w") as file:
        file.write("## Latest AI News\n")
        file.write(crew_result)


if __name__ == "__main__":
    url_list = [
        "https://x.com/hirosystems/status/1796579639982440751",
        "https://x.com/LangChainAI/status/1796942281821585864",
        "https://x.com/rohanpaul_ai/status/1798457077037469962",
        "https://x.com/Steve8708/status/1798720674875560220",
    ]
    engage_crew_with_tasks(url_list)
