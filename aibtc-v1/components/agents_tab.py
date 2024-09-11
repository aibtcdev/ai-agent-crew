import pandas as pd
import streamlit as st
from utils.session import get_crew_class


def render_agents_tab(crew_selection):
    crew_class = get_crew_class(crew_selection)
    if crew_class is None:
        st.warning(
            f"No crew found for {crew_selection}. Please check your crew definitions."
        )
        return

    crew_instance = crew_class()
    crew_instance.setup_agents(st.session_state.llm)

    if not crew_instance.agents:
        st.warning(
            f"No agents found for {crew_selection}. Please check your crew definition."
        )
    else:
        for agent in crew_instance.agents:
            with st.container():
                try:
                    st.markdown(f"#### {agent.role}")
                    st.markdown(f"**Goal:** {agent.goal}")
                    st.markdown(f"**Backstory:** {agent.backstory}")

                    tool_data = []
                    for tool in agent.tools:
                        tool_name = tool.name if hasattr(tool, "name") else str(tool)
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
                    st.error(f"Error displaying agent {agent.role}: {str(e)}")

                st.markdown("---")
