# Import necessary libraries
import streamlit as st
import ollama
import time
import crews.trading_analyzer as trading_analyzer
from utils.session import init_session_state

# Initialize session state
init_session_state()

# Set up Streamlit page
st.set_page_config(page_title="CrewAI Chatbot", layout="centered")

# Load custom styles (same as before)
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

# Initialize the Ollama client
client = ollama.Client(
    host="localhost"
)  # Adjust base_url if Ollama is hosted elsewhere

# Placeholder for user session and chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "crew_selected" not in st.session_state:
    st.session_state["crew_selected"] = None

if "conversation_context" not in st.session_state:
    st.session_state["conversation_context"] = (
        "intro"  # Start with the introduction context
    )

# List of available CrewAIs and their descriptions
available_crews = {
    "Wallet Analysis": "Analyzes wallet activity and transaction patterns.",
    "Contract Scan": "Scans smart contracts for potential vulnerabilities.",
    "Token Analyzer": "Analyzes token prices and provides recommendations.",
}

# Initial welcome message
INITIAL_WELCOME_MESSAGE = (
    "Welcome to CrewAI Chatbot! I can help you run different CrewAIs. Here are the available options:\n\n"
    "- **Wallet Analysis**: Analyzes wallet activity and transaction patterns.\n"
    "- **Contract Scan**: Scans smart contracts for potential vulnerabilities.\n"
    "- **Token Analyzer**: Analyzes token prices and provides recommendations.\n"
    "\nYou can ask me more about any of these or tell me what you want to do, and I'll recommend a CrewAI to run."
)


def main():
    st.title("AIBTC.DEV Chatbot")

    # Display chat history using Streamlit's `st.chat_message` for better UI
    for speaker, message in st.session_state["chat_history"]:
        with st.chat_message(speaker.lower()):
            st.markdown(message)

    # Text input box for user interaction
    user_input = st.chat_input("Type your message here...")

    # Check if user input exists and process it immediately
    if user_input:
        # Add user input to chat history and update UI immediately
        add_to_chat("User", user_input)

        # Handle the conversation or execute a CrewAI based on user input
        handle_user_input(user_input)

        # Trigger re-render to display the bot response immediately
        st.rerun()


def add_to_chat(speaker, message):
    """Adds a new message to the chat history."""
    st.session_state["chat_history"].append((speaker, message))


def handle_conversation(user_input):
    """
    Handles the conversation by sending the input to the LLM and letting it determine the action.
    The LLM will suggest the CrewAI to run and any required parameters.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a chatbot that helps users interact with and run different CrewAIs based on their needs. "
                "Given the user's input, determine which CrewAI is most relevant from the following options:\n"
                "- Wallet Analysis: Analyzes wallet activity and transaction patterns.\n"
                "- Contract Scan: Scans smart contracts for potential vulnerabilities.\n"
                "- Token Analyzer: Analyzes token prices and provides recommendations.\n"
                "\nIf the user's input indicates interest in one of these options, respond with the exact name of the relevant CrewAI, "
                'followed by any required parameters in JSON format (e.g., {"param1": "value1", "param2": "value2"}). '
                "If the user needs further assistance, provide guidance or ask clarifying questions."
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
        # Assuming LLM returns something like: "CrewAI: Wallet Analysis, Parameters: {'address': 'wallet_address'}"
        crew_name = None
        parameters = {}
        if "CrewAI" in response_content:
            parts = response_content.split("Parameters:")
            crew_name = parts[0].split("CrewAI:")[1].strip()
            if len(parts) > 1:
                parameters = eval(parts[1].strip())  # Convert to dictionary
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

    trading_class = trading_analyzer.TradingAnalyzerCrew()
    llm = st.session_state.llm

    trading_class.setup_agents(llm)
    trading_class.setup_tasks(
        "welsh"
    )  # This should be dynamic based on crew_name and parameters

    crypto_trading_crew = trading_class.create_crew()

    with st.spinner(f"Running {crew_name} CrewAI..."):
        result = crypto_trading_crew.kickoff(
            parameters
        )  # Pass the parameters to the crew

    st.success(f"Execution complete for {crew_name}!")

    st.subheader("Analysis Results")

    # Display results
    result_str = str(result.raw)

    time.sleep(2)  # Simulate execution time
    return f"Execution complete for {crew_name} CrewAI. Results: {result_str}"


import logging


def handle_user_input(user_input):
    """Directs the conversation flow based on user input and executes the necessary CrewAI."""
    context = st.session_state["conversation_context"]

    if context == "intro":
        add_to_chat("Bot", INITIAL_WELCOME_MESSAGE)
        st.session_state["conversation_context"] = "awaiting_selection"

    elif context == "awaiting_selection":
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
            # add_to_chat(
            #     "Bot",
            #     "I couldn't find a matching CrewAI for your request. Could you clarify or provide more details?",
            # )

    elif context == "crew_executed":
        response = "I've executed the CrewAI you selected. Would you like to run another CrewAI or discuss the results?"
        add_to_chat("Bot", response)
        st.session_state["conversation_context"] = "awaiting_selection"


if __name__ == "__main__":
    main()
