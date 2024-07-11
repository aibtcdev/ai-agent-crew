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

# load the transcript file

# load the chat notes
