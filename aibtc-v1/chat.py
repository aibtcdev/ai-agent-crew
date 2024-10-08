import streamlit as st
import logging
from typing import Dict, Any
from utils.session import init_session_state

# Initialize session state
init_session_state()

# Set up Streamlit page
st.set_page_config(page_title="AIBTC Chatbot", layout="centered")

# Constants
AVAILABLE_CREWS: Dict[str, Dict[str, Any]] = st.session_state.crew_mapping


def load_custom_styles():
    custom_styles = """
        <style>
        /* load regular custom font */
        @font-face {
        font-family: 'DM Sans 9pt';
        src: url('https://aibtc.dev/fonts/DMSans-9ptRegular.woff2') format('woff2'),
            url('https://aibtc.dev/fonts/DMSans-9ptRegular.woff') format('woff');
        font-weight: normal;
        font-style: normal;
        font-display: swap;
        }

        /* load italic custom font */
        @font-face {
        font-family: 'DM Sans 9pt';
        src: url('https://aibtc.dev/fonts/DMSans-9ptItalic.woff2') format('woff2'),
            url('https://aibtc.dev/fonts/DMSans-9ptItalic.woff') format('woff');
        font-weight: normal;
        font-style: italic;
        font-display: swap;
        }

        /* set font for the entire document */
        html, body {
        font-family: 'DM Sans 9pt', 'DM Sans', sans-serif !important;
        }

        /* set font for common elements */
        h1, h2, h3, h4, h5, h6, p, a, span, div, button, input, select, textarea {
        font-family: 'DM Sans 9pt', 'DM Sans', 'Source Sans Pro', sans-serif !important;
        }

        /* set page bg pattern same as main site */
        /* DISABLED FOR NOW
        .stAppViewMain {
            background-image: url('https://aibtc.dev/logos/aibtcdev-pattern-1-640px.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        @media (min-width: 640px) {
            .stAppViewMain {
                background-image: url('https://aibtc.dev/logos/aibtcdev-pattern-1-1280px.png');
            }
        }
        @media (min-width: 1280px) {
            .stAppViewMain {
                background-image: url('https://aibtc.dev/logos/aibtcdev-pattern-1-1920px.png');
            }
        }
        */

        /* set max page width */
        .stMainBlockContainer {
            max-width: 800px;
            padding-top: 2rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 3rem;
            margin: 0 auto;
            background-color: black;
        }

        /* hide navigation menu */
        header[data-testid="stHeader"] {
            display: none;
            visibility: hidden;
        }

        /* custom tab styling */
        button[data-baseweb="tab"] {
            margin: 0;
            width: 100%;
        }
        button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 24px !important;
        font-weight: bold !important;
        }

        /* custom text input styling */
        .stTextInput > div > div > input {
            background-color: #000000;
        }

        /* custom select box styling */

        /* select box label */
        .stSelectbox label > div > p {
            font-size: 1.5rem !important;
            font-weight: bold !important;
            color: white !important;
        }

        /* select box container */
        .stSelectbox [data-baseweb="select"] {
            background-color: #000000 !important;
        }

        /* select box selected item when closed */
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #000000 !important;
            color: white !important;
            font-size: 1rem !important;
        }

        /* select box dropdown options container */
        .stSelectbox [role="listbox"] {
            background-color: #000000 !important;
        }

        /* icon link styles */
        .icon-links {
            display: flex;
            justify-content: space-evenly;
            gap: 10px;
            margin: 0 auto;
        }
        .icon-link {
            background-color: #58595B;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.3s;
            color: white;
            text-decoration: none;
        }
        .icon-link:hover {
            background-color: #F2F2F2;
        }
        .icon-link svg {
            width: 20px;
            height: 20px;
        }
        </style>
        """
    st.write(custom_styles, unsafe_allow_html=True)


def generate_initial_welcome_message() -> str:
    message = "Welcome to AIBTC! I can help you run different crews of agents. Here are the available options:\n\n"
    message += "\n".join(
        f"- **{name}**: {info['description']}" for name, info in AVAILABLE_CREWS.items()
    )
    message += "\n\nYou can ask me more about any of these or tell me what you want to do, and I'll recommend a crew to run."
    return message


INITIAL_WELCOME_MESSAGE = generate_initial_welcome_message()


def initialize_session_state():
    if st.session_state.messages == []:
        st.session_state.messages = [
            {"role": "Bot", "content": INITIAL_WELCOME_MESSAGE}
        ]
    if "crew_selected" not in st.session_state:
        st.session_state.crew_selected = None
    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = "awaiting_selection"
    if "crew_step_container" not in st.session_state:
        st.session_state.crew_step_container = st.empty()
    if "crew_task_container" not in st.session_state:
        st.session_state.crew_task_container = st.empty()
    if "crew_step_callback" not in st.session_state:
        st.session_state.crew_step_callback = []
    if "crew_task_callback" not in st.session_state:
        st.session_state.crew_task_callback = []


def add_to_chat(speaker: str, message: str):
    st.chat_message(speaker).write(message)
    st.session_state.messages.append({"role": speaker, "content": message})


def handle_conversation(user_input: str) -> tuple:
    options = "\n".join(
        f"- {name}: {info['description']}" for name, info in AVAILABLE_CREWS.items()
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You are a specialized assistant designed to help users select the most appropriate CrewAI for their needs. "
                "Your task is to analyze the user's input and determine which CrewAI is most relevant from the following options:\n"
                f"{options}\n"
                "\nYour response should strictly include the exact name of the relevant CrewAI, "
                "followed by any required parameters. "
                "Example: Wallet Analysis || SP2SDRD31DZD2477M39Q0GTH18G0WJH4J984JKQE8"
                "Do not provide any additional information, explanations, or suggestions. "
                "If the user's input is unclear, ask a clarifying question to gather more information."
            ),
        },
        {"role": "user", "content": user_input},
    ]

    response = st.session_state.llm.call(messages=messages)

    try:
        response_content = response
        print(response_content)
        if "||" in response_content:
            crew_name, parameters = map(str.strip, response_content.split("||"))
            return crew_name, parameters, response_content
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f"Error parsing LLM response: {e}")

    return None, None, response


def run_crew_ai(crew_name: str, parameters: str) -> str:
    st.write("Step Progress:")
    st.session_state.crew_step_container = st.empty()
    st.write("Task Progress:")
    st.session_state.crew_task_container = st.empty()
    st.session_state.crew_step_callback = []
    st.session_state.crew_task_callback = []

    crew_class = AVAILABLE_CREWS.get(crew_name, {}).get("class")
    if not crew_class:
        return f"CrewAI {crew_name} is not implemented yet."

    crew_instance = crew_class(st.session_state.embedder)
    crew_instance.setup_agents(st.session_state.llm)
    crew_instance.setup_tasks(parameters)
    crew = crew_instance.create_crew()

    with st.spinner(f"Running {crew_name} CrewAI..."):
        result = crew.kickoff()

    st.success(f"Execution complete for {crew_name}!")
    st.subheader("Analysis Results")
    return f"Execution complete for {crew_name} CrewAI. Results: {result.raw}"


def handle_user_input(user_input: str):
    context = st.session_state.conversation_context

    if context == "awaiting_selection":
        crew_name, parameters, response = handle_conversation(user_input)
        print(crew_name)
        if crew_name:
            add_to_chat(
                "Bot",
                f"Great! Executing the {crew_name} CrewAI with parameters: {parameters}...",
            )
            try:
                crew_output = run_crew_ai(crew_name, parameters)
                add_to_chat("Bot", f"**{crew_name} Output:**\n{crew_output}")
            except Exception as e:
                logging.error(f"Error executing CrewAI: {e}")
                add_to_chat(
                    "Bot", "There was an error executing the CrewAI. Please try again."
                )
            st.session_state.crew_selected = crew_name
            st.session_state.conversation_context = "crew_executed"
        else:
            add_to_chat("Bot", response)

    elif context == "crew_executed":
        add_to_chat(
            "Bot",
            "I've executed the CrewAI you selected. Would you like to run another CrewAI or discuss the results?",
        )
        st.session_state.conversation_context = "awaiting_selection"


def main():
    st.title("AIBTC.DEV Chatbot")
    load_custom_styles()
    initialize_session_state()

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Type your message here...")

    if user_input:
        add_to_chat("User", user_input)
        handle_user_input(user_input)


if __name__ == "__main__":
    main()
