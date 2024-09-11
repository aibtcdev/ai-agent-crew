import inspect
import re
import streamlit as st
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
    crew_class = get_crew_class(crew_selection)

    if crew_class is None:
        st.warning(
            f"No crew found for {crew_selection}. Please check your crew definitions."
        )
        return

    try:
        tools = crew_class.get_all_tools()
    except Exception as e:
        st.error(f"Error getting tools: {str(e)}")
        tools = []

    if not tools:
        st.info("No tools found for this crew.")
    else:
        for tool in tools:
            st.markdown(f"#### {tool.name}")
            st.write(f"**Description:**: {tool.description}")
            # get the function signature
            sig = inspect.signature(tool.func)
            params = sig.parameters

            if params:
                st.write("**Arguments:**")
                for param_name, param in params.items():
                    if param_name == "dummy_arg":
                        st.write(f"(none)")
                    else:
                        st.write(
                            f"- {param_name}: {param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any'}"
                        )
            else:
                st.write("**Arguments:** No arguments")
            st.markdown("---")
