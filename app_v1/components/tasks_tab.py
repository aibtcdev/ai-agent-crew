import inspect
import importlib
import streamlit as st
from crew_ai import tasks


def sync_tasks():
    importlib.reload(tasks)
    st.session_state.tasks = {}
    for name, func in inspect.getmembers(tasks, inspect.isfunction):
        if name.startswith("get_"):
            task_name = name.replace("_", " ").title()
            st.session_state.tasks[task_name] = func


def render_tasks_tab():
    if not st.session_state.tasks:
        st.warning(
            "No tasks found. Please check your crew_ai/tasks.py file and ensure tasks are defined correctly."
        )
    else:

        # search functionality
        search_term = st.text_input(
            "Search tasks", value=st.session_state.tasks_search_term
        ).lower()
        st.session_state.tasks_search_term = search_term

        # filtering tasks based on search
        filtered_tasks = {
            name: func
            for name, func in st.session_state.tasks.items()
            if search_term in name.lower()
        }

        # stats in 2 columns for tasks
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"**Showing {len(filtered_tasks)} / {len(st.session_state.tasks)} tasks**"
            )
        with col2:
            if st.button("Clear filters"):
                st.session_state.tasks_search_term = ""
                st.rerun()

        for task_name, task_func in filtered_tasks.items():
            with st.expander(task_name):
                try:
                    # create an instance of the task
                    task = task_func(None)

                    st.markdown(f"**Description:** {task.description}")
                    st.markdown(f"**Expected Output:** {task.expected_output}")
                except Exception as e:
                    st.error(f"Error displaying task {task_name}: {str(e)}")
