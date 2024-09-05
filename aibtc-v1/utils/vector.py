import os
import requests
from bs4 import BeautifulSoup
from crewai_tools import Tool
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def fetch_clarity_book_content(website_url: str):
    """Fetch and parse the content of the provided URL using Beautiful Soup. Targets the main article content."""
    response = requests.get(website_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article = soup.select_one("section#article article")
    if not article:
        return ""

    title = article.find("h2")
    title_text = title.text if title else ""

    for element in article.select(".code, .buttons"):
        element.decompose()

    content = article.get_text(separator="\n", strip=True)

    full_content = f"{title_text}\n\n{content}"

    return full_content


def create_vector_store(urls, chunk_size=1000, chunk_overlap=200):
    documents = []
    for url in urls:
        content = fetch_clarity_book_content(url)
        documents.append(Document(page_content=content, metadata={"source": url}))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)

    # TODO: what about other embedding options? requires OpenAI here?
    return Chroma.from_documents(
        splits, OpenAIEmbeddings(openai_api_key=openai_api_key)
    )


def create_vector_search_tool(vector_store, name, description):
    def search_func(query: str):
        results = vector_store.similarity_search(query, k=3)
        return "\n\n".join(
            f"From {doc.metadata['source']}:\n{doc.page_content}" for doc in results
        )

    return Tool(name=name, func=search_func, description=description)


# TODO: these are avialable in markdown format too
# TODO: add to training data repo, use it for vectors
# TODO: explore larger vector stores (one per project?)
clarity_book_code_vector_store = create_vector_store(
    [
        "https://book.clarity-lang.org/ch04-00-storing-data.html",
        "https://book.clarity-lang.org/ch04-01-constants.html",
        "https://book.clarity-lang.org/ch04-02-variables.html",
        "https://book.clarity-lang.org/ch04-03-maps.html",
        "https://book.clarity-lang.org/ch05-00-functions.html",
        "https://book.clarity-lang.org/ch03-00-keywords.html",
        "https://book.clarity-lang.org/ch02-00-types.html",
        "https://book.clarity-lang.org/ch13-01-coding-style.html",
        "https://book.clarity-lang.org/ch06-00-control-flow.html",
        "https://book.clarity-lang.org/ch06-01-asserts.html",
        "https://book.clarity-lang.org/ch06-02-try.html",
        "https://book.clarity-lang.org/ch06-03-unwrap-flavours.html",
        "https://book.clarity-lang.org/ch06-04-response-checking.html",
        "https://raw.githubusercontent.com/stacksgov/sips/main/sips/sip-010/sip-010-fungible-token-standard.md",
    ]
)

clarity_book_function_vector_store = create_vector_store(
    [
        "https://book.clarity-lang.org/ch05-00-functions.html",
        "https://book.clarity-lang.org/ch05-01-public-functions.html",
        "https://book.clarity-lang.org/ch05-02-private-functions.html",
        "https://book.clarity-lang.org/ch05-03-read-only-functions.html",
    ]
)
