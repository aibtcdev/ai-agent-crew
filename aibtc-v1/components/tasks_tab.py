import inspect
import streamlit as st


def render_tasks_tab():
    if not st.session_state.tasks:
        st.warning(
            "No tasks found. Please check your aibtc_crews/tasks.py file and ensure tasks are defined correctly."
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

        # split stats and clear filters button
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"**Showing {len(filtered_tasks)} / {len(st.session_state.tasks)} tasks**"
            )
        with col2:
            if st.button("Clear filters", use_container_width=True):
                st.session_state.tasks_search_term = ""
                st.rerun()

        for task_name, task_func in filtered_tasks.items():
            with st.expander(task_name):
                try:
                    # get the function signature
                    sig = inspect.signature(task_func)
                    # P\prepare default arguments
                    default_args = {
                        "agent": None,
                        "contract_code": "Sample contract code",
                        "contract_functions": "Sample contract functions",
                    }
                    # Only use the arguments that the function accepts
                    func_args = {
                        k: v for k, v in default_args.items() if k in sig.parameters
                    }
                    # create an instance of the task
                    task = task_func(**func_args)
                    # display the task details
                    st.markdown(f"**Description:** {task.description}")
                    st.markdown(f"**Expected Output:** {task.expected_output}")
                except Exception as e:
                    st.error(f"Error displaying task {task_name}: {str(e)}")
