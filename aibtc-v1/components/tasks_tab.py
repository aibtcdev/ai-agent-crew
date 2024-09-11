import streamlit as st
from utils.session import get_crew_class, get_crew_inputs


def render_tasks_tab(crew_selection):
    crew_class = get_crew_class(crew_selection)
    if crew_class is None:
        st.warning(
            f"No crew found for {crew_selection}. Please check your crew definitions."
        )
        return

    input_names = get_crew_inputs(crew_selection)

    st.write(f"Expected inputs for {crew_selection}:")
    for input_name in input_names:
        st.write(f"- {input_name}")

    # Create an instance of the crew
    crew_instance = crew_class()

    # Create mock data
    mock_data = {input_name: f"mock_{input_name}" for input_name in input_names}

    # Pass the mock data to the setup_tasks method
    llm = st.session_state.llm
    crew_instance.setup_agents(llm)
    crew_instance.setup_tasks(**mock_data)

    st.write("Tasks for this crew:")
    if hasattr(crew_instance, "tasks") and crew_instance.tasks:
        for i, task in enumerate(crew_instance.tasks, 1):
            st.markdown(f"**Task {i}:** {task.description}")
            st.markdown(f"*Expected Output:* {task.expected_output}")
            st.markdown("---")
    else:
        st.info("No tasks have been set up for this crew.")
