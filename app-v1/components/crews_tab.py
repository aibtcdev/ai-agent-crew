import streamlit as st
import ast
import inspect
from crew_ai import crews
import importlib


def add_crew():
    st.session_state.adding_crew = True


def save_new_crew(name, agents):
    with open("crew_ai/crews.py", "a") as file:
        new_crew = f"""
@ui_class("{name}")
class {name.replace(" ", "")}:
    @staticmethod
    @ui_method("{name}")
    def get_{name.lower().replace(" ", "_")}(agents, tasks):
        return Crew(
            agents=[agents["{agent}"] for agent in {agents}],
            tasks=[],  # You might want to add a way to specify tasks
            process=Process.sequential,
            verbose=2,
        )
"""
        file.write(new_crew)
    st.session_state.adding_crew = False
    sync_crews()


def sync_crews():
    importlib.reload(crews)
    st.session_state.crews = {}
    for name, obj in inspect.getmembers(crews):
        if inspect.isclass(obj) and hasattr(obj, "ui_name"):
            for method_name, method in inspect.getmembers(obj):
                if inspect.isfunction(method) and hasattr(method, "ui_name"):
                    crew = method(
                        st.session_state.get("agents", {}),
                        st.session_state.get("tasks", {}),
                    )
                    st.session_state.crews[obj.ui_name] = crew
    st.success("Crews synced successfully!")


def render_crews_tab():
    if "crews" not in st.session_state:
        sync_crews()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Crew", use_container_width=True):
            add_crew()
    with col2:
        if st.button("Sync Crews", use_container_width=True):
            sync_crews()

    if st.session_state.get("adding_crew", False):
        with st.form("new_crew"):
            name = st.text_input("Crew Name")
            agents = st.multiselect(
                "Select Agents", options=list(st.session_state.get("agents", {}).keys())
            )
            if st.form_submit_button("Save Crew"):
                save_new_crew(name, agents)

    for crew_name, crew in st.session_state.crews.items():
        st.subheader(crew_name)

        with st.container():
            st.markdown(
                f"**{len(crew.agents)} Agent{'s' if len(crew.agents) > 1 else ''}**"
            )

            num_agents = len(crew.agents)
            num_columns = min(num_agents, 4)
            image_width = 50 if num_agents == 1 else None

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
