# app.py

import streamlit as st
import ollama
import time
import crews.trading_analyzer as trading_analyzer
from utils.session import init_session_state

# initialize session state
init_session_state()


# set up streamlit pag
st.set_page_config(page_title="CrewAI Chatbot", layout="centered")

# custom css styling
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
    "Token Analyzer": "Analyzes token prices provides recommendation.",
}


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
    """Handles the conversation by sending the input to the Ollama client."""
    messages = [{"role": "user", "content": user_input}]
    response = client.chat(
        model="llama3.2", messages=messages
    )  # Adjust model as needed
    return response["message"]["content"]


def run_crew_ai(crew_name):
    """Runs the selected CrewAI and simulates execution output."""
    # Placeholder for CrewAI execution logic
    llm = st.session_state.llm

    st.write("Step Progress:")
    st.session_state.crew_step_container = st.empty()
    st.write("Task Progress:")
    st.session_state.crew_task_container = st.empty()

    st.session_state.crew_step_callback = []
    st.session_state.crew_task_callback = []

    trading_class = trading_analyzer.TradingAnalyzerCrew()
    trading_class.setup_agents(llm)
    trading_class.setup_tasks("welsh")
    crypto_trading_crew = trading_class.create_crew()

    with st.spinner("Analyzing..."):
        result = crypto_trading_crew.kickoff()

    st.success("Analysis complete!")

    # display_token_usage(result.token_usage)

    st.subheader("Analysis Results")

    # Display results
    result_str = str(result.raw)

    time.sleep(2)  # Simulate execution time
    return f"Execution complete for {crew_name} CrewAI. Results: {result_str}"


def match_crew(user_input):
    """
    Determines if the user input matches or refers to a CrewAI.
    Returns the CrewAI name if a match is found, otherwise None.
    """
    # Check if user input contains any CrewAI name or keyword
    for crew_name in available_crews.keys():
        if crew_name.lower() in user_input.lower():
            return crew_name

    # Additional keyword-based matching logic (can be extended)
    keywords = {
        "wallet": "Wallet Analysis",
        "contract": "Contract Scan",
        "token": "Token Analyzer",
    }

    for keyword, crew_name in keywords.items():
        if keyword.lower() in user_input.lower():
            return crew_name

    return None


def handle_user_input(user_input):
    """
    Directs the conversation flow based on user input.
    Starts with guiding the user about available CrewAIs and progresses to execution.
    """
    # Check the current context of the conversation
    context = st.session_state["conversation_context"]

    if context == "intro":
        # Initial context: Introduce the available CrewAIs and guide the user
        response = "Welcome to CrewAI Chatbot! I can help you run different CrewAIs. Here are the available options:\n\n"
        for crew_name, description in available_crews.items():
            response += f"- **{crew_name}**: {description}\n"
        response += "\nYou can ask me more about any of these or tell me which one you'd like to run."
        add_to_chat("Bot", response)
        st.session_state["conversation_context"] = "awaiting_selection"

    elif context == "awaiting_selection":
        # Determine if the user has selected a CrewAI
        matched_crew = match_crew(user_input)

        if matched_crew:
            # Execute the matched CrewAI and get the result
            add_to_chat("Bot", f"Great! Executing the {matched_crew} CrewAI...")
            crew_output = run_crew_ai(matched_crew)
            add_to_chat("Bot", f"**{matched_crew} Output:**\n{crew_output}")
            st.session_state["crew_selected"] = matched_crew
            st.session_state["conversation_context"] = "crew_executed"
        else:
            # Respond using LLM to provide further guidance
            response = handle_conversation(user_input)
            add_to_chat("Bot", response)

    elif context == "crew_executed":
        # After executing a CrewAI, allow the user to ask questions or select another
        response = "I've executed the CrewAI you selected. Would you like to run another CrewAI or discuss the results?"
        add_to_chat("Bot", response)
        st.session_state["conversation_context"] = "awaiting_selection"


if __name__ == "__main__":
    main()
