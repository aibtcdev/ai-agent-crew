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


# initialize session state
init_session_state()


# Display logo full width
st.image(
    "https://aibtc.dev/logos/aibtcdev-primary-logo-white-wide-1000px.png",
    use_column_width=True,
)

# Add icon links
icon_links_html = """
<div class="icon-links">
    <a href="https://aibtc.dev" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC Website">
        <svg viewBox="0 0 576 512"><path d="M280.37 148.26L96 300.11V464a16 16 0 0 0 16 16l112.06-.29a16 16 0 0 0 15.92-16V368a16 16 0 0 1 16-16h64a16 16 0 0 1 16 16v95.64a16 16 0 0 0 16 16.05L464 480a16 16 0 0 0 16-16V300L295.67 148.26a12.19 12.19 0 0 0-15.3 0zM571.6 251.47L488 182.56V44.05a12 12 0 0 0-12-12h-56a12 12 0 0 0-12 12v72.61L318.47 43a48 48 0 0 0-61 0L4.34 251.47a12 12 0 0 0-1.6 16.9l25.5 31A12 12 0 0 0 45.15 301l235.22-193.74a12.19 12.19 0 0 1 15.3 0L530.9 301a12 12 0 0 0 16.9-1.6l25.5-31a12 12 0 0 0-1.7-16.93z"></path></svg>
    </a>
    <a href="https://docs.aibtc.dev" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC Documentation">
        <svg viewBox="0 0 448 512"><path d="M448 360V24c0-13.3-10.7-24-24-24H96C43 0 0 43 0 96v320c0 53 43 96 96 96h328c13.3 0 24-10.7 24-24v-16c0-7.5-3.5-14.3-8.9-18.7-4.2-15.4-4.2-59.3 0-74.7 5.4-4.3 8.9-11.1 8.9-18.6zM128 134c0-3.3 2.7-6 6-6h212c3.3 0 6 2.7 6 6v20c0 3.3-2.7 6-6 6H134c-3.3 0-6-2.7-6-6v-20zm0 64c0-3.3 2.7-6 6-6h212c3.3 0 6 2.7 6 6v20c0 3.3-2.7 6-6 6H134c-3.3 0-6-2.7-6-6v-20zm253.4 250H96c-17.7 0-32-14.3-32-32 0-17.6 14.4-32 32-32h285.4c-1.9 17.1-1.9 46.9 0 64z"></path></svg>
    </a>
    <a href="https://github.com/aibtcdev" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC GitHub">
        <svg viewBox="0 0 256 256"><path d="M216,104v8a56.06,56.06,0,0,1-48.44,55.47A39.8,39.8,0,0,1,176,192v40a8,8,0,0,1-8,8H104a8,8,0,0,1-8-8V216H72a40,40,0,0,1-40-40A24,24,0,0,0,8,152a8,8,0,0,1,0-16,40,40,0,0,1,40,40,24,24,0,0,0,24,24H96v-8a39.8,39.8,0,0,1,8.44-24.53A56.06,56.06,0,0,1,56,112v-8a58.14,58.14,0,0,1,7.69-28.32A59.78,59.78,0,0,1,69.07,28,8,8,0,0,1,76,24a59.75,59.75,0,0,1,48,24h24a59.75,59.75,0,0,1,48-24,8,8,0,0,1,6.93,4,59.74,59.74,0,0,1,5.37,47.68A58,58,0,0,1,216,104Z"></path></svg>
    </a>
    <a href="https://replit.com/@wbtc402/ai-agent-crew" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC Replit">
        <svg viewBox="0 0 24 24"><path d="M2 1.5A1.5 1.5 0 0 1 3.5 0h7A1.5 1.5 0 0 1 12 1.5V8H3.5A1.5 1.5 0 0 1 2 6.5ZM12 8h8.5A1.5 1.5 0 0 1 22 9.5v5a1.5 1.5 0 0 1-1.5 1.5H12ZM2 17.5A1.5 1.5 0 0 1 3.5 16H12v6.5a1.5 1.5 0 0 1-1.5 1.5h-7A1.5 1.5 0 0 1 2 22.5Z"></path></svg>
    </a>
    <a href="https://discord.gg/Z59Z3FNbEX" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC Discord">
        <svg viewBox="0 0 640 512"><path d="M524.531,69.836a1.5,1.5,0,0,0-.764-.7A485.065,485.065,0,0,0,404.081,32.03a1.816,1.816,0,0,0-1.923.91,337.461,337.461,0,0,0-14.9,30.6,447.848,447.848,0,0,0-134.426,0,309.541,309.541,0,0,0-15.135-30.6,1.89,1.89,0,0,0-1.924-.91A483.689,483.689,0,0,0,116.085,69.137a1.712,1.712,0,0,0-.788.676C39.068,183.651,18.186,294.69,28.43,404.354a2.016,2.016,0,0,0,.765,1.375A487.666,487.666,0,0,0,176.02,479.918a1.9,1.9,0,0,0,2.063-.676A348.2,348.2,0,0,0,208.12,430.4a1.86,1.86,0,0,0-1.019-2.588,321.173,321.173,0,0,1-45.868-21.853,1.885,1.885,0,0,1-.185-3.126c3.082-2.309,6.166-4.711,9.109-7.137a1.819,1.819,0,0,1,1.9-.256c96.229,43.917,200.41,43.917,295.5,0a1.812,1.812,0,0,1,1.924.233c2.944,2.426,6.027,4.851,9.132,7.16a1.884,1.884,0,0,1-.162,3.126,301.407,301.407,0,0,1-45.89,21.83,1.875,1.875,0,0,0-1,2.611,391.055,391.055,0,0,0,30.014,48.815,1.864,1.864,0,0,0,2.063.7A486.048,486.048,0,0,0,610.7,405.729a1.882,1.882,0,0,0,.765-1.352C623.729,277.594,590.933,167.465,524.531,69.836ZM222.491,337.58c-28.972,0-52.844-26.587-52.844-59.239S193.056,219.1,222.491,219.1c29.665,0,53.306,26.82,52.843,59.239C275.334,310.993,251.924,337.58,222.491,337.58Zm195.38,0c-28.971,0-52.843-26.587-52.843-59.239S388.437,219.1,417.871,219.1c29.667,0,53.307,26.82,52.844,59.239C470.715,310.993,447.538,337.58,417.871,337.58Z"></path></svg>
    </a>
    <a href="https://x.com/aibtcdev" class="icon-link" target="_blank" rel="noopener noreferrer" title="AIBTC on X">
        <svg viewBox="0 0 512 512"><path d="M389.2 48h70.6L305.6 224.2 487 464H345L233.7 318.6 106.5 464H35.8L200.7 275.5 26.8 48H172.4L272.9 180.9 389.2 48zM364.4 421.8h39.1L151.1 88h-42L364.4 421.8z"></path></svg>
    </a>
</div>
"""


# initialize crew selections
available_crews = list(st.session_state.crew_mapping.keys())

# Display crew selection
crew_selection = st.selectbox("Select your crew:", available_crews)

# Main layout with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Run 🏃", "Agents", "Tools", "Tasks"])

with tab1:
    render_execution_tab(crew_selection)

with tab2:
    render_agents_tab(crew_selection)

with tab3:
    render_tools_tab(crew_selection)

with tab4:
    render_tasks_tab(crew_selection)

st.divider()

st.markdown(icon_links_html, unsafe_allow_html=True)
