import streamlit as st
import inspect
from crew_ai import crews
import importlib
from utils import update_session_state


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
            tasks=[],
            process=Process.sequential,
            verbose=2,
        )
"""
        file.write(new_crew)
    st.session_state.adding_crew = False
    sync_crews()


def sync_crews():
    importlib.reload(crews)
    if "crews" not in st.session_state:
        st.session_state.crews = {}
    if "agents" not in st.session_state:
        st.session_state.agents = {}
    if "tasks" not in st.session_state:
        st.session_state.tasks = {}

    new_crews = {}
    for name, obj in inspect.getmembers(crews):
        if inspect.isclass(obj) and hasattr(obj, "ui_name"):
            for method_name, method in inspect.getmembers(obj):
                if inspect.isfunction(method) and hasattr(method, "ui_name"):
                    try:
                        crew = method(
                            st.session_state.agents,
                            st.session_state.tasks,
                        )
                        new_crews[obj.ui_name] = crew
                    except ValueError as e:
                        st.warning(f"Failed to create crew '{obj.ui_name}': {str(e)}")
                    except Exception as e:
                        st.error(
                            f"An unexpected error occurred while creating crew '{obj.ui_name}': {str(e)}"
                        )

    update_session_state("crews", new_crews)

    if new_crews:
        st.success(f"Successfully synced {len(new_crews)} crews.")
    else:
        st.info(
            "No crews were synced. Please check if all required agents and tasks are created."
        )

    # Display the current state of agents and tasks
    st.subheader("Current Agents")
    for agent_name in st.session_state.agents.keys():
        st.write(f"- {agent_name}")

    st.subheader("Current Tasks")
    for task_name in st.session_state.tasks.keys():
        st.write(f"- {task_name}")


def assign_tasks_to_crew(crew_name, task_list):
    if crew_name in st.session_state.crews:
        crew = st.session_state.crews[crew_name]
        crew.tasks.extend(task_list)
        update_session_state("crews", st.session_state.crews)
        st.success(f"Tasks assigned to {crew_name} successfully!")
    else:
        st.error(f"Crew '{crew_name}' not found.")


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

            # Display current tasks
            if crew.tasks:
                st.markdown("**Current Tasks:**")
                for task in crew.tasks:
                    st.markdown(f"- {task}")
            else:
                st.markdown("*No tasks assigned yet.*")

            # Placeholder for future task assignment UI
            st.markdown("### Assign Tasks")
            st.markdown(
                "*Task assignment functionality will be added in a future iteration.*"
            )

        st.markdown("---")

    # Demonstration of task assignment (for testing purposes)
    st.subheader("Assign Tasks to Crew (Demo)")
    demo_crew = st.selectbox("Select Crew", options=list(st.session_state.crews.keys()))
    demo_tasks = st.text_area("Enter tasks (one per line)")
    if st.button("Assign Tasks"):
        task_list = [task.strip() for task in demo_tasks.split("\n") if task.strip()]
        assign_tasks_to_crew(demo_crew, task_list)
