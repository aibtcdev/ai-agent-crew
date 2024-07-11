import importlib
import pandas as pd
import streamlit as st


def sync_agents():
    app_config = load_config()
    spec = importlib.util.spec_from_file_location(
        "aibtcdev_agents", "aibtcdev_agents.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    defined_agents = [
        name
        for name in dir(module)
        if name.startswith("get_") and callable(getattr(module, name))
    ]
    config_agents = app_config.get("agents", [])

    new_agents = [agent for agent in defined_agents if agent not in config_agents]
    if new_agents:
        app_config["agents"] = config_agents + new_agents
        save_config(app_config)
        st.success(f"Synced {len(new_agents)} new agents: {', '.join(new_agents)}")
    else:
        st.info("No new agents to sync.")


def get_agent_classes():
    import aibtcdev_agents

    importlib.reload(aibtcdev_agents)

    # Get all attributes of the aibtcdev_agents module
    all_attributes = dir(aibtcdev_agents)

    # Filter classes that are defined in aibtcdev_agents (not imported)
    # and end with 'Crew' to ensure we're only getting crew classes
    crew_classes = [
        getattr(aibtcdev_agents, attr)
        for attr in all_attributes
        if isinstance(getattr(aibtcdev_agents, attr), type)
        and getattr(aibtcdev_agents, attr).__module__ == "aibtcdev_agents"
        and attr.endswith("Crew")
    ]

    return crew_classes


def add_agent_form(all_tools):
    st.subheader("Add New Agent")

    app_config = load_config()
    existing_agents = app_config.get("agents", [])

    with st.form("add_agent_form"):
        role = st.text_input("Role")
        goal = st.text_input("Goal")
        backstory = st.text_area("Backstory")
        selected_tools = st.multiselect("Tools", options=all_tools)

        submitted = st.form_submit_button("Add Agent")
        if submitted:
            function_name = f"get_{role.lower().replace(' ', '_')}"
            new_agent = f"""
def {function_name}(llm):
    return Agent(
        role="{role}",
        goal="{goal}",
        backstory="{backstory}",
        tools=[{', '.join(selected_tools)}],
        verbose=True,
        llm=llm,
    )
"""
            with open("aibtcdev_agents.py", "a") as file:
                file.write(new_agent)

            if function_name not in existing_agents:
                existing_agents.append(function_name)
                app_config["agents"] = existing_agents
                save_config(app_config)

            st.success(f"Agent '{role}' added successfully!")
            st.experimental_rerun()


def render_agents_tab(llm, all_tools):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Agent", use_container_width=True):
            add_agent_form(all_tools)
    with col2:
        if st.button("Sync Agents", use_container_width=True):
            sync_agents()
            st.experimental_rerun()

    agent_classes = get_agent_classes()

    col1, col2 = st.columns(2)

    for i, agent_class in enumerate(agent_classes):
        methods = [method for method in dir(agent_class) if method.startswith("get_")]
        for j, method_name in enumerate(methods):
            method = getattr(agent_class, method_name)
            try:
                agent = method(llm)
            except Exception as e:
                st.error(f"Error creating agent {method_name}: {str(e)}")
                continue

            with col1 if j % 2 == 0 else col2:
                with st.container():
                    st.subheader(agent.role)

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
