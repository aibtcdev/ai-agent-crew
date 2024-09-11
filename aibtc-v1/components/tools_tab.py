import importlib
import re
import streamlit as st
from typing import Dict, Type
from utils.session import get_crew_class


def extract_bun_run_command(source: str) -> str:
    lines = source.split("\n")
    bun_run_lines = []
    in_bun_run = False
    parentheses_count = 0

    for line in lines:
        if "BunScriptRunner.bun_run" in line:
            in_bun_run = True

        if in_bun_run:
            bun_run_lines.append(line.strip())
            parentheses_count += line.count("(") - line.count(")")

            if parentheses_count == 0:
                break

    joined_command = " ".join(bun_run_lines)

    # normalize spacing
    normalized_command = re.sub(r"\s*([(),])\s*", r"\1 ", joined_command)
    normalized_command = re.sub(r"\s+", " ", normalized_command)
    normalized_command = normalized_command.replace("( ", "(").replace(" )", ")")

    return normalized_command.strip()


def render_tools_tab(crew_selection):
    st.subheader("Tools")

    crew_class = get_crew_class(crew_selection)

    if crew_class is None:
        st.warning(
            f"No crew found for {crew_selection}. Please check your crew definitions."
        )
        return

    try:
        tools = crew_class.get_all_tools()  # We're ignoring the debug_info here
    except Exception as e:
        st.error(f"Error getting tools: {str(e)}")
        tools = []

    if not tools:
        st.info("No tools found for this crew.")
    else:
        st.write(f"Number of tools found: {len(tools)}")
        for tool in tools:
            with st.expander(tool.name):
                st.write("**Description:**")
                st.write(tool.description)
                st.write("**Usage:**")
                st.code(f"{tool.name}(address: str) -> str")
