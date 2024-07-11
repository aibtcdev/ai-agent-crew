import streamlit as st


def render_tasks_tab(tasks):
    col1, col2 = st.columns(2)
    with col1:
        st.button("Add Task", use_container_width=True)
    with col2:
        st.button("Sync Tasks", use_container_width=True)

    for task_name, task in tasks.items():
        with st.expander(task_name):
            st.write(f"Description: {task.description}")
            st.write(f"Assigned Agent: {task.agent.role}")
