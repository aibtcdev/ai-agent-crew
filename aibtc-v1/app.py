import streamlit as st
from components.agents_tab import render_agents_tab
from components.execution_tab import render_execution_tab
from components.tasks_tab import render_tasks_tab
from components.tools_tab import render_tools_tab
from utils.session import init_session_state


# set up streamlit page
st.set_page_config(
    page_title="AIBTC Crews",
    layout="wide",
)

# initialize session state
init_session_state()

# set max page width
page_width = """
<style>
.main .block-container {
    max-width: 800px;
    padding-top: 2rem;
    padding-right: 1rem;
    padding-left: 1rem;
    padding-bottom: 3rem;
    margin: 0 auto;
}
</style>
"""
st.write(page_width, unsafe_allow_html=True)

# custom tab styling
tab_style = """
<style>
button[data-baseweb="tab"] {
    margin: 0;
    width: 100%;
}
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 24px !important;
  font-weight: bold !important;
}
</style>
"""
st.write(tab_style, unsafe_allow_html=True)

# custom text input styling
text_input_style = """
<style>
.stTextInput > div > div > input {
    background-color: #000000;
}
</style>
"""
st.write(text_input_style, unsafe_allow_html=True)

# Display logo full width
st.image(
    "https://aibtc.dev/logos/aibtcdev-primary-logo-white-wide-1000px.png",
    use_column_width=True,
)

# Main layout with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Agents", "Tools", "Tasks", "Execution"])

with tab1:
    render_agents_tab()

with tab2:
    render_tools_tab()

with tab3:
    render_tasks_tab()

with tab4:
    render_execution_tab()
