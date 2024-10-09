import os
import requests
from bs4 import BeautifulSoup
from crewai_tools import Tool
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from litellm import embedding
from chromadb import Client as ChromaClient
from chromadb.config import Settings
import chromadb
import streamlit as st

load_dotenv()


class AIBTCEmbeddings:
    """A class to get embeddings using LiteLLM."""

    def __init__(self):
        self.model_name = os.getenv("OPENAI_EMBEDDER_MODEL", "text-embedding-3-small")

    def get_embedding(self, text):
        """Retrieve embeddings for a given text using LiteLLM."""
        response = embedding(model=self.model_name, input=[text])
        if not response or "data" not in response or not response["data"]:
            raise Exception(f"Failed to get embeddings: {response}")
        return response["data"][0]["embedding"]

    def embed_documents(self, texts):
        """Embed a list of texts (documents) using LiteLLM."""
        return [self.get_embedding(text) for text in texts]

    def embed_query(self, query):
        """Embed a single query string using LiteLLM."""
        return self.get_embedding(query)


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
    """Create a vector store from a list of URLs using LiteLLM embeddings."""
    documents = []
    for url in urls:
        content = fetch_clarity_book_content(url)
        documents.append(Document(page_content=content, metadata={"source": url}))

    # Split the documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)

    # Initialize AIBTCEmbeddings
    aibtc_embeddings = AIBTCEmbeddings()

    # Create embeddings for each document chunk
    embeddings = aibtc_embeddings.embed_documents([doc.page_content for doc in splits])

    # Create a new Chroma client
    chroma_client = chromadb.PersistentClient(path="./chroma")

    # Create or get a collection in Chroma for storing embeddings
    collection = chroma_client.get_or_create_collection(name="example_collection")

    # Add the document chunks, metadata, and their embeddings to the Chroma collection
    collection.add(
        documents=[doc.page_content for doc in splits],
        metadatas=[doc.metadata for doc in splits],
        ids=[str(i) for i in range(len(splits))],
        embeddings=embeddings,
    )

    return collection


def create_vector_search_tool(vector_store, name, description):
    """Create a vector search tool using the given vector store."""

    def search_func(query: str):
        results = vector_store.similarity_search(query, k=3)
        return "\n\n".join(
            f"From {doc.metadata['source']}:\n{doc.page_content}" for doc in results
        )

    return Tool(name=name, func=search_func, description=description)


# Define the URLs for different sections of the Clarity book
clarity_book_code_vector_store = create_vector_store(
    [
        "https://book.clarity-lang.org/ch04-00-storing-data.html",
        "https://book.clarity-lang.org/ch05-00-functions.html",
        "https://book.clarity-lang.org/ch03-00-keywords.html",
        "https://book.clarity-lang.org/ch02-00-types.html",
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
