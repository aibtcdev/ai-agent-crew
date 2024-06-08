from crewai import Crew, Process, Task
from crewai.tasks import TaskOutput
from agents import MeetingsCrew
from news_examples import good_example, bad_example

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

scraped_content_list = []
key_points_list = []
news_list = []


def build_scraped_content_list(crew_output: TaskOutput):
    # takes the output from the agent
    # and builds a list of scraped content from each output
    scraped_content_list.append(crew_output.raw_output)


def build_key_points_list(crew_output: TaskOutput):
    # takes the output from the agent
    # and builds a list of key points from each output
    key_points_list.append(crew_output.raw_output)


def build_news_list(url, content, summary):
    news_item = {"url": url, "content": content, "summary": summary}
    news_list.append(news_item)


# define the tasks


# 1. scrape website, return tweet content (callback: build news link list, simpler: url is index of next list?)
def create_scrape_website_task(url):
    return Task(
        description=(
            f"Provided URL: {url}."
            "Fetch the contents of this tweet and return the raw content for use in a later step."
        ),
        expected_output="The entire contents of the tweet excluding any HTML code.",
        agent=MeetingsCrew.website_scraper(),
        callback=build_scraped_content_list,
    )


# 2. using tweet content, extract key points (callback: build key points list)
def create_extract_key_points_task(url, scrape_task: Task):
    return Task(
        description=(
            "Extract key points from the tweet content. "
            "Focus on identifying the most important information and creating a concise summary."
        ),
        expected_output="Key points extracted from the tweet content.",
        agent=MeetingsCrew.meeting_writer(),
        context=[scrape_task],
        callback=build_key_points_list,
    )


# 3. using key points list, create a markdown file with a summary for the agenda
#   - how to give context on our group? (who-we-are, what-we-do type files/vars)
#   - how to use past examples? (available in communications repo, submodule? last 1? last 3? just use one in here?)
# NOTE: unused rn, defined in 2nd crew instead for now, need to be able to pass info for dict creation
def create_agenda_summary_task(news_list):
    return Task(
        description=(
            "Create a markdown file with a summary of the key points extracted from the tweet. "
            "Include relevant links and context. "
            "Ensure the summary is concise and informative."
            "News List:"
            f"{news_list}"
        ),
        expected_output="A markdown file with the heading 'Latest AI News' and a bullet point summary of all the related information from each tweet. The first line for each list item should summarize the news content and link to the original source.",
        agent=MeetingsCrew.meeting_writer(),
    )


# aggregate the tasks into a list


def create_task_list(url_list):
    tasks = []
    for url in url_list:
        scrape_task = create_scrape_website_task(url)
        tasks.append(scrape_task)
        extract_key_points_task = create_extract_key_points_task(url, scrape_task)
        tasks.append(extract_key_points_task)
    return tasks


# define the crew and run the tasks


def engage_crew_with_tasks(url_list):
    # define the tasks for the crew to complete
    # based on the list of URLs provided
    # NOTE: scoped to X links for now, for simplicity
    task_list = create_task_list(url_list)

    # create the crew to handle the research / prep
    info_gathering_crew = Crew(
        agents=[
            MeetingsCrew.website_scraper(),
            MeetingsCrew.meeting_writer(),
        ],
        process=Process.sequential,
        tasks=task_list,
        verbose=0,
    )

    # Run the crew against all tasks
    info_gathering_crew.kickoff()

    # print URL list for debug
    print("--------------------------------------------------")
    print(f"URL List: {len(url_list)} items.")
    print(url_list)
    print("--------------------------------------------------")

    # print scraped content list for debug
    print("--------------------------------------------------")
    print(f"Scraped Content List: {len(scraped_content_list)} items.")
    print(scraped_content_list)
    print("--------------------------------------------------")

    # print key points list for debug
    print("--------------------------------------------------")
    print(f"Key Points List: {len(key_points_list)} items.")
    print(key_points_list)
    print("--------------------------------------------------")

    # create the news list from the url, content, and key points lists
    for i in range(len(url_list)):
        build_news_list(url_list[i], scraped_content_list[i], key_points_list[i])

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
                    "The provided news list contains a url, scraped content, and generated summary for each news item."
                    "Your job is to review all of the news items and create a markdown file with a summary of the key points extracted from the tweet."
                    "[START GOOD EXAMPLE]"
                    f"{good_example}"
                    "[END GOOD EXAMPLE]"
                    "[START BAD EXAMPLE]"
                    f"{bad_example}"
                    "[END BAD EXAMPLE]"
                    "[START NEWS LIST]"
                    f"{news_list}"
                    "[END NEWS LIST]"
                ),
                expected_output=(
                    "A markdown file with the L3 heading 'Latest AI News' and a bullet point summary of all the related information from each tweet."
                ),
                agent=MeetingsCrew.meeting_writer(),
            )
        ],
        verbose=2,
    )

    # Run the crew against all tasks
    crew_result = agenda_preparation_crew.kickoff()

    # Print the result
    print("--------------------------------------------------")
    print("Meeting Agenda Prepartion Crew Final Result:")
    print(crew_result)
    print("--------------------------------------------------")

    # Create a YYYY-MM-DD-HH-MM timestamp
    from datetime import datetime

    file_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")

    # create generated-meeting-agenda.md file with the result
    with open(f"agendas/{file_timestamp}-generated-meeting-agenda.md", "w") as file:
        file.write("## Latest AI News\n")
        # for item in news_list:
        #    file.write(f"## News Item\n")
        #    file.write(f"- URL: {item['url']}\n")
        #    file.write(f"- Content:\n{item['content']}\n")
        #    file.write(f"- Summary:\n{item['summary']}\n")
        #    file.write("\n")
        file.write(crew_result)


if __name__ == "__main__":
    url_list = [
        "https://x.com/hirosystems/status/1796579639982440751",
        "https://x.com/LangChainAI/status/1796942281821585864",
        "https://x.com/rohanpaul_ai/status/1798457077037469962",
        "https://x.com/Steve8708/status/1798720674875560220",
    ]
    engage_crew_with_tasks(url_list)
