import inspect
import importlib
import os
import pandas as pd
import re
import streamlit as st
from crew_ai import agents, tools


def sync_agents(notify=True):
    importlib.reload(agents)
    st.session_state.agents = {}
    for class_name, class_obj in inspect.getmembers(agents, inspect.isclass):
        if hasattr(class_obj, "ui_name"):
            for method_name, method in inspect.getmembers(
                class_obj, inspect.isfunction
            ):
                if hasattr(method, "ui_name"):
                    try:
                        agent = method(st.session_state.llm)
                        st.session_state.agents[method.ui_name] = agent
                    except Exception as e:
                        st.error(f"Error creating agent {method.ui_name}: {str(e)}")

    if notify:
        if not st.session_state.agents:
            st.warning("No agents found in the crew_ai/agents.py file.")
        else:
            st.success(f"Synced {len(st.session_state.agents)} agents successfully!")


def edit_agent(agent_name):
    agent = st.session_state.agents[agent_name]

    st.subheader(f"Editing Agent: {agent_name}")

    with st.form(key=f"edit_agent_form_{agent_name}"):
        role = st.text_input("Agent Role", value=agent.role)
        goal = st.text_input("Agent Goal", value=agent.goal)
        backstory = st.text_area("Agent Backstory", value=agent.backstory)

        # Get the names of the current tools
        current_tool_names = []
        for tool in agent.tools:
            if hasattr(tool, "__class__") and hasattr(tool, "__name__"):
                tool_name = f"{tool.__class__.__name__}.{tool.__name__}"
                current_tool_names.append(tool_name)
            elif isinstance(tool, str):
                current_tool_names.append(tool)
            else:
                current_tool_names.append(str(tool))

        # Ensure all current tools are in the options
        all_tools = set(st.session_state.all_tools)
        for tool in current_tool_names:
            all_tools.add(tool)

        selected_tools = st.multiselect(
            "Select Tools", options=sorted(list(all_tools)), default=current_tool_names
        )

        submit_button = st.form_submit_button(label="Update Agent")

        if submit_button:
            update_agent(agent_name, role, goal, backstory, selected_tools)
            st.session_state.editing_agent = None
            st.success(f"Agent '{agent_name}' updated successfully!")
            st.rerun()


def update_agent(agent_name, role, goal, backstory, tool_paths):
    agents_file_path = os.path.join("crew_ai", "agents.py")

    with open(agents_file_path, "r") as file:
        content = file.read()

    class_name = "".join(word.capitalize() for word in agent_name.split())
    pattern = rf'@ui_class\("{re.escape(agent_name)}"\)\s*class {re.escape(class_name)}:.*?(?=@ui_class|\Z)'

    tool_imports = set()
    for tool_path in tool_paths:
        tool_class, _ = tool_path.split(".")
        tool_imports.add(f"from crew_ai.tools import {tool_class}")

    new_agent_code = f"""@ui_class("{role}")
class {class_name}:
    @staticmethod
    @ui_method("{role}")
    def get_{role.lower().replace(' ', '_')}(llm=None):
        kwargs = {{"llm": llm}} if llm is not None else {{}}
        return Agent(
            role="{role}",
            goal="{goal}",
            backstory="{backstory}",
            verbose=True,
            memory=True,
            allow_delegation=False,
            tools=[{', '.join(tool_paths)}],
            **kwargs
        )
"""

    updated_content = re.sub(pattern, new_agent_code, content, flags=re.DOTALL)

    # Add imports if they don't exist
    for import_statement in tool_imports:
        if import_statement not in updated_content:
            updated_content = import_statement + "\n" + updated_content

    if updated_content != content:
        with open(agents_file_path, "w") as file:
            file.write(updated_content)
        sync_agents()
    else:
        st.error(f"Could not find agent '{agent_name}' in the file.")


def delete_agent(agent_name):
    agents_file_path = os.path.join("crew_ai", "agents.py")

    with open(agents_file_path, "r") as file:
        content = file.read()

    # Create the pattern to find the existing agent class
    class_name = "".join(word.capitalize() for word in agent_name.split())
    pattern = rf'@ui_class\("{re.escape(agent_name)}"\)\s*class {re.escape(class_name)}:.*?(?=@ui_class|\Z)'

    # Remove the agent code
    updated_content = re.sub(pattern, "", content, flags=re.DOTALL)

    if updated_content != content:
        with open(agents_file_path, "w") as file:
            file.write(updated_content)
        st.success(f"Agent '{agent_name}' deleted successfully!")
    else:
        st.error(f"Could not find agent '{agent_name}' in the file.")

    sync_agents()


def sync_tools():
    st.session_state.all_tools = []
    for module_name, module in inspect.getmembers(tools, inspect.ismodule):
        for class_name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, "ui_name"):
                for method_name, method in inspect.getmembers(obj):
                    if inspect.isfunction(method) and hasattr(method, "ui_name"):
                        tool_name = f"{class_name}.{method_name}"
                        st.session_state.all_tools.append(tool_name)


def save_new_agent(role, goal, backstory, tools):
    # Generate a class name from the role
    class_name = "".join(word.capitalize() for word in role.split())

    # Prepare the new agent code
    new_agent_code = f"""
@ui_class("{role}")
class {class_name}:
    @staticmethod
    @ui_method("{role}")
    def get_{role.lower().replace(' ', '_')}(llm=None):
        kwargs = {{"llm": llm}} if llm is not None else {{}}
        return Agent(
            role="{role}",
            goal="{goal}",
            backstory="{backstory}",
            verbose=True,
            memory=True,
            allow_delegation=False,
            tools=[{', '.join(tools)}],
            **kwargs
        )
"""

    # Append the new agent to the agents.py file
    agents_file_path = os.path.join("crew_ai", "agents.py")
    with open(agents_file_path, "a") as file:
        file.write(new_agent_code)

    st.success(f"Agent '{role}' saved successfully!")
    st.session_state.adding_agent = False
    sync_agents()


def render_agents_tab():
    if "agents" not in st.session_state:
        sync_agents(notify=False)

    if "all_tools" not in st.session_state:
        sync_tools()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Agent", use_container_width=True):
            st.session_state.adding_agent = True
    with col2:
        if st.button("Sync Agents", use_container_width=True):
            sync_agents()

    if st.session_state.get("adding_agent", False):
        with st.form("new_agent"):
            role = st.text_input("Agent Role")
            goal = st.text_input("Agent Goal")
            backstory = st.text_area("Agent Backstory")
            selected_tools = st.multiselect(
                "Select Tools", options=st.session_state.all_tools
            )
            save_agent_col, cancel_save_agent_col = st.columns(2)
            with save_agent_col:
                if st.form_submit_button("Save Agent", use_container_width=True):
                    save_new_agent(role, goal, backstory, selected_tools)
            with cancel_save_agent_col:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.adding_agent = False

    st.markdown("---")

    if not st.session_state.agents:
        st.warning("No agents found. Please add agents or sync the agents list.")
    else:
        col1, col2 = st.columns(2)
        for i, (agent_name, agent) in enumerate(st.session_state.agents.items()):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.subheader(agent_name)

                    img_col, info_col = st.columns([1, 2])

                    with img_col:
                        st.image(
                            f"https://bitcoinfaces.xyz/api/get-image?name={agent.role.replace(' ', '-')}",
                            use_column_width=True,
                            output_format="auto",
                            caption=agent.role,
                            clamp=True,
                        )

                    with info_col:
                        st.markdown(f"**Goal:** {agent.goal}")
                        st.markdown(f"**Backstory:** {agent.backstory}")

                    with st.expander("Tools and Capabilities"):
                        tool_data = []
                        for tool in agent.tools:
                            tool_name = (
                                tool.name if hasattr(tool, "name") else tool.__name__
                            )
                            full_description = (
                                tool.description
                                if hasattr(tool, "description")
                                else "No description available"
                            )
                            description = (
                                full_description.split(" - ")[-1]
                                if " - " in full_description
                                else full_description
                            )
                            tool_data.append(
                                {"Tool": tool_name, "Description": description}
                            )

                        if tool_data:
                            df = pd.DataFrame(tool_data)
                            st.dataframe(
                                df,
                                column_config={
                                    "Tool": st.column_config.TextColumn(
                                        "Tool", width="medium", help="Name of the tool"
                                    ),
                                    "Description": st.column_config.TextColumn(
                                        "Description",
                                        width="large",
                                        help="What the tool does",
                                    ),
                                },
                                hide_index=True,
                                use_container_width=True,
                            )
                        else:
                            st.write("No tools available for this agent.")

                    edit_col, delete_col = st.columns([3, 1])
                    with edit_col:
                        if st.button(
                            "Edit Agent",
                            key=f"edit_{agent_name}",
                            use_container_width=True,
                        ):
                            st.session_state.editing_agent = agent_name
                    with delete_col:
                        if st.button(
                            "Delete Agent",
                            key=f"delete_{agent_name}",
                            use_container_width=True,
                        ):
                            if st.button(
                                f"Are you sure you want to delete {agent_name}?",
                                use_container_width=True,
                            ):
                                delete_agent(agent_name)

    if st.session_state.get("editing_agent"):
        edit_agent(st.session_state.editing_agent)
