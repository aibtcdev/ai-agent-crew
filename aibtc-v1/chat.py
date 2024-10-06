# Import necessary libraries
import streamlit as st
import ollama
import time
import logging
from utils.session import init_session_state
from crews.trading_analyzer import TradingAnalyzerCrew

# Initialize session state
init_session_state()

# Set up Streamlit page
st.set_page_config(page_title="CrewAI Chatbot", layout="centered")


# Load custom styles
def load_custom_styles():
    custom_styles = """
    <style>
    /* Custom styles here */
    </style>
    """
    st.write(custom_styles, unsafe_allow_html=True)


# Initialize the Ollama client
client = ollama.Client(host="localhost")


# Placeholder for user session and chat history
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        # Add the initial welcome message to the chat history
        add_to_chat("Bot", INITIAL_WELCOME_MESSAGE)
        st.session_state["conversation_context"] = "awaiting_selection"
    if "crew_selected" not in st.session_state:
        st.session_state["crew_selected"] = None
    if "conversation_context" not in st.session_state:
        st.session_state["conversation_context"] = "awaiting_selection"


# map looks like the following
# crew_mapping[crew_name] = {
#     "description": crew_description,
#     "class": obj,
#     "task_inputs": getattr(obj, "get_task_inputs", lambda: []),
# }
AVAILABLE_CREWS = st.session_state.crew_mapping


# Dynamically generate the initial welcome message
def generate_initial_welcome_message():
    message = "Welcome to CrewAI Chatbot! I can help you run different CrewAIs. Here are the available options:\n\n"
    for crew_name, crew_info in AVAILABLE_CREWS.items():
        message += f"- **{crew_name}**: {crew_info['description']}\n"
    message += "\nYou can ask me more about any of these or tell me what you want to do, and I'll recommend a CrewAI to run."
    return message


INITIAL_WELCOME_MESSAGE = generate_initial_welcome_message()


def main():
    st.title("AIBTC.DEV Chatbot")
    load_custom_styles()
    initialize_session_state()

    # Display chat history
    for speaker, message in st.session_state["chat_history"]:
        with st.chat_message(speaker.lower()):
            st.markdown(message)

    # Text input box for user interaction
    user_input = st.chat_input("Type your message here...")

    if user_input:
        add_to_chat("User", user_input)
        handle_user_input(user_input)
        st.rerun()


def add_to_chat(speaker, message):
    """Adds a new message to the chat history."""
    st.session_state["chat_history"].append((speaker, message))


def handle_conversation(user_input):
    """
    Handles the conversation by sending the input to the LLM and letting it determine the action.
    The LLM will suggest the CrewAI to run and any required parameters.
    """
    # Dynamically generate the options for the LLM prompt
    options = "\n".join(
        [f"- {name}: {info['description']}" for name, info in AVAILABLE_CREWS.items()]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a specialized assistant designed to help users select the most appropriate CrewAI for their needs. "
                "Your task is to analyze the user's input and determine which CrewAI is most relevant from the following options:\n"
                f"{options}\n"
                "\nYour response should strictly include the exact name of the relevant CrewAI, "
                "followed by any required parameters"
                "example would be Wallet Analysis || SP2SDRD31DZD2477M39Q0GTH18G0WJH4J984JKQE8"
                "Do not provide any additional information, explanations, or suggestions. "
                "If the user's input is unclear, ask a clarifying question to gather more information."
            ),
        },
        {"role": "user", "content": user_input},
    ]
    response = client.chat(
        model="llama3.2", messages=messages
    )  # Adjust model as needed

    # Parse the LLM's response to extract the crew and parameters
    try:
        print(f"Response received: {response}")
        response_content = response["message"]["content"]
        # Assuming LLM returns something like: "Wallet Analysis || SP2SDRD31DZD2477M39Q0GTH18G0WJH4J984JKQE8"
        crew_name = None
        parameters = {}
        if "||" in response_content:
            parts = response_content.split("||")
            crew_name = parts[0].strip()
            if len(parts) > 1:
                parameters = parts[1].strip()  # Convert to dictionary
    except (KeyError, IndexError, SyntaxError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response received: {response}")
        crew_name, parameters = None, {}

    return crew_name, parameters, response["message"]["content"]


def run_crew_ai(crew_name, parameters=None):
    """Runs the selected CrewAI and simulates execution output with optional parameters."""
    st.write("Step Progress:")
    st.session_state.crew_step_container = st.empty()
    st.write("Task Progress:")
    st.session_state.crew_task_container = st.empty()

    st.session_state.crew_step_callback = []
    st.session_state.crew_task_callback = []

    # Dynamically select the crew class based on crew_name
    crew_class = AVAILABLE_CREWS.get(crew_name, {}).get("class", None)

    if crew_class:
        print(parameters)
        crew_instance = crew_class()
        llm = st.session_state.llm
        crew_instance.setup_agents(llm)
        crew_instance.setup_tasks(parameters)
        crew = crew_instance.create_crew()

        with st.spinner(f"Running {crew_name} CrewAI..."):
            result = crew.kickoff()

        st.success(f"Execution complete for {crew_name}!")

        st.subheader("Analysis Results")
        result_str = str(result.raw)
        return f"Execution complete for {crew_name} CrewAI. Results: {result_str}"
    else:
        return f"CrewAI {crew_name} is not implemented yet."


def handle_user_input(user_input):
    """Directs the conversation flow based on user input and executes the necessary CrewAI."""
    context = st.session_state["conversation_context"]

    if context == "awaiting_selection":
        crew_name, parameters, response = handle_conversation(user_input)

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
            st.session_state["crew_selected"] = crew_name
            st.session_state["conversation_context"] = "crew_executed"
        else:
            add_to_chat("Bot", response)

    elif context == "crew_executed":
        response = "I've executed the CrewAI you selected. Would you like to run another CrewAI or discuss the results?"
        add_to_chat("Bot", response)
        st.session_state["conversation_context"] = "awaiting_selection"


if __name__ == "__main__":
    main()
