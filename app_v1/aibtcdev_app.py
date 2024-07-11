import streamlit as st
from components.sidebar import render_sidebar
from components.agents_tab import render_agents_tab
from components.crews_tab import render_crews_tab
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


# define tabs used in app
# def crews_tab():
#    render_crews_tab()


# def agents_tab():
#    render_agents_tab()


# def tools_tab():
#    render_tools_tab()


# def tasks_tab():
#    render_tasks_tab()


# def execution_tab():
#    render_execution_tab()


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
# tab1, tab2, tab3, tab4, tab5 = st.tabs(
#    ["Crews", "Agents", "Tools", "Tasks", "Execution"]
# )

# with tab1:
#    crews_tab()

# with tab2:
#    agents_tab()

# with tab3:
#    tools_tab()

# with tab4:
#    tasks_tab()

# with tab5:
#    execution_tab()

render_agents_tab()
