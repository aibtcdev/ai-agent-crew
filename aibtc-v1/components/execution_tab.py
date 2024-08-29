import streamlit as st
from crews.wallet_summary_crew import AIBTC_Crew as wallet_summary
from crews.smart_contract_audit_crew import AIBTC_Crew as smart_contract_audit


def render_execution_tab():
    # st.write("This is where the magic happens.")
    smart_contract_audit.render_smart_contract_analysis_crew()
    wallet_summary.render_wallet_summary_crew()
