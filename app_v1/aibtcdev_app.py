import streamlit as st
from components.sidebar import render_sidebar
from components.agents_tab import render_agents_tab
from components.execution_tab import render_execution_tab
from components.tasks_tab import render_tasks_tab
from components.tools_tab import render_tools_tab
from utils import init_session_state


# set up streamlit page
page_title = "AIBTCdev Interactive Crews"
st.set_page_config(
    page_title=page_title,
    layout="wide",
)

# initialize session state
init_session_state()


# show sidebar for settings
render_sidebar()

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

# Main layout with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Agents", "Tools", "Tasks", "Execution"])

with tab1:
    render_agents_tab()

with tab2:
    render_tools_tab()

with tab3:
    render_tasks_tab()

with tab4:
    st.write("Execution")
    # render_execution_tab()
