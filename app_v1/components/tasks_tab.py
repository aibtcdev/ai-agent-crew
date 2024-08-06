import inspect
import importlib
from crew_ai import tasks
import streamlit as st


def sync_tasks():
    importlib.reload(tasks)
    st.session_state.tasks = {}
    for name, func in inspect.getmembers(tasks, inspect.isfunction):
        if name.startswith("get_"):
            task_name = name[4:].replace("_", " ").title()
            st.session_state.tasks[task_name] = func


def render_tasks_tab():
    sync_tasks()

    if not st.session_state.tasks:
        st.warning(
            "No tasks found. Please check your crew_ai/tasks.py file and ensure tasks are defined correctly."
        )
    else:
        for task_name, task_func in st.session_state.tasks.items():
            with st.container():
                st.subheader(task_name)

                try:
                    # Create an instance of the task
                    # Note: We're passing None as the agent for now
                    task = task_func(None)

                    st.markdown(f"**Description:** {task.description}")
                    st.markdown(f"**Expected Output:** {task.expected_output}")

                except Exception as e:
                    st.error(f"Error displaying task {task_name}: {str(e)}")

                st.markdown("---")  # Add a horizontal line between tasks
