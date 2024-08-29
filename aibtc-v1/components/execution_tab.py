import streamlit as st
from crews.wallet_summary_crew import AIBTC_Crew


def render_execution_tab():
    # st.write("This is where the magic happens.")
    AIBTC_Crew.render_wallet_summary_crew()
