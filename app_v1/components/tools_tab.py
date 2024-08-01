import importlib
import inspect
import re
import streamlit as st
from typing import Dict, Type
from crewai_tools import Tool

def get_tool_groups() -> Dict[str, Type]:
    import crew_ai.tools
    importlib.reload(crew_ai.tools)
    return crew_ai.tools.get_tool_groups()

def extract_bun_run_command(source: str) -> str:
    lines = source.split('\n')
    bun_run_lines = []
    in_bun_run = False
    parentheses_count = 0

    for line in lines:
        if 'BunScriptRunner.bun_run' in line:
            in_bun_run = True
        
        if in_bun_run:
            bun_run_lines.append(line.strip())
            parentheses_count += line.count('(') - line.count(')')
            
            if parentheses_count == 0:
                break

    joined_command = ' '.join(bun_run_lines)
    
    # Normalize spacing
    normalized_command = re.sub(r'\s*([(),])\s*', r'\1 ', joined_command)
    normalized_command = re.sub(r'\s+', ' ', normalized_command)
    normalized_command = normalized_command.replace('( ', '(').replace(' )', ')')

    return normalized_command.strip()

def render_tools_tab():
    col1, col2 = st.columns(2)
    with col1:
        st.button("Add Tool", use_container_width=True)
    with col2:
        st.button("Sync Tools", use_container_width=True)

    tool_groups = get_tool_groups()

    for group_name, tool_class in tool_groups.items():
        st.subheader(group_name)

        class_dict = tool_class.__dict__
        for name, value in class_dict.items():
            if isinstance(value, staticmethod):
                tool = value.__func__
                if isinstance(tool, Tool):
                    with st.expander(f"{tool.name}"):
                        st.write(f"**Description:** {tool.description}")

                        # Get the function signature
                        sig = inspect.signature(tool.func)
                        params = sig.parameters

                        if params:
                            st.write("**Arguments:**")
                            for param_name, param in params.items():
                                if param_name == 'dummy_arg':
                                    st.write(f"(none)")
                                else:
                                    st.write(f"- {param_name}: {param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any'}")
                        else:
                            st.write("**Arguments:** No arguments")

                        # Extract and display the BunScriptRunner command
                        source = inspect.getsource(tool.func)
                        bun_run_command = extract_bun_run_command(source)
                        if bun_run_command:
                            st.write("**Bun execution:**")
                            st.code(bun_run_command, language="python")
