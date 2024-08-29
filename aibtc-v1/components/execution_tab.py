import streamlit as st
from crews.smart_contract_audit_crew import AIBTC_Crew


def render_execution_tab():
    # st.write("This is where the magic happens.")
    AIBTC_Crew.render_smart_contract_analysis_crew()
