import streamlit as st
from components.crews.contract_audit_crew import render_contract_audit_crew


def render_execution_tab():
    st.write("This is where the magic happens.")
    render_contract_audit_crew()
