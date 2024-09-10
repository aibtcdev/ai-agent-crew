from crews.wallet_summarizer import WalletSummaryCrew
from crews.smart_contract_auditor import SmartContractAuditCrew
from crews.clarity_code_generator import ClarityCodeGeneratorCrew


def render_execution_tab():
    # st.write("This is where the magic happens.")
    # smart_contract_audit.render_smart_contract_analysis_crew()
    # wallet_summary.render_wallet_summary_crew()
    # WalletSummaryCrew().render_crew()
    # SmartContractAuditCrew().render_crew()
    ClarityCodeGeneratorCrew().render_crew()
