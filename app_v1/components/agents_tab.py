import streamlit as st
import pandas as pd


def render_agents_tab():
    if not st.session_state.agents:
        st.warning(
            "No agents found. Please check your aibtc_crews/agents.py file and ensure agents are defined correctly."
        )
    else:
        for agent_name, agent_func in st.session_state.agents.items():
            with st.container():

                try:
                    # create an instance of the agent
                    agent = agent_func()

                    img_col, info_col = st.columns([1, 3])

                    with img_col:
                        st.image(
                            f"https://bitcoinfaces.xyz/api/get-image?name={agent.role.replace(' ', '-')}",
                            use_column_width=False,
                            output_format="auto",
                            caption=agent.role,
                            width=100,
                        )

                    with info_col:
                        st.markdown(f"**Goal:** {agent.goal}")
                        st.markdown(f"**Backstory:** {agent.backstory}")

                    with st.expander("Tools and Capabilities"):
                        tool_data = []
                        for tool in agent.tools:
                            tool_name = (
                                tool.name if hasattr(tool, "name") else str(tool)
                            )
                            tool_data.append({"Tool": tool_name})

                        if tool_data:
                            df = pd.DataFrame(tool_data)
                            st.dataframe(
                                df,
                                column_config={
                                    "Tool": st.column_config.TextColumn(
                                        "Tool",
                                        width="medium",
                                        help="Name of the tool",
                                    ),
                                },
                                hide_index=True,
                                use_container_width=True,
                            )
                        else:
                            st.write("No tools available for this agent.")
                except Exception as e:
                    st.error(f"Error displaying agent {agent_name}: {str(e)}")

                st.markdown("---")
