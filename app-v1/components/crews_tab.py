import streamlit as st


def render_crews_tab(crews):
    for crew_name, crew in crews.items():
        st.subheader(crew_name)

        with st.container():
            st.markdown(
                f"**{len(crew.agents)} Agent{'s' if len(crew.agents) > 1 else ''}**"
            )

            num_agents = len(crew.agents)
            num_columns = min(num_agents, 4)
            image_width = 150 if num_agents == 1 else None

            cols = st.columns(num_columns)

            for i, agent in enumerate(crew.agents):
                with cols[i % num_columns]:
                    st.image(
                        f"https://bitcoinfaces.xyz/api/get-image?name={agent.role}",
                        width=image_width,
                        use_column_width=image_width is None,
                        output_format="auto",
                        caption=agent.role,
                        clamp=True,
                    )

            st.markdown(f"*{crew_name} is ready for action!*")

        st.markdown("---")
