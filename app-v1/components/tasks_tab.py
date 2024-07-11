import streamlit as st


def render_tasks_tab(tasks):
    for task_name, task in tasks.items():
        with st.expander(task_name):
            st.write(f"Description: {task.description}")
            st.write(f"Assigned Agent: {task.agent.role}")
