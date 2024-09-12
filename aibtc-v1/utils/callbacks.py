import streamlit as st


def extract_step_output(step):
    if isinstance(step, dict):
        # Check if 'log' is directly in the step dictionary
        if "log" in step:
            return step["log"]
        # Check if it's nested in 'return_values'
        elif "return_values" in step and isinstance(step["return_values"], dict):
            if "log" in step["return_values"]:
                return step["return_values"]["log"]
    elif isinstance(step, list):
        # If it's a list, try to find 'log' in its items
        for item in step:
            if isinstance(item, dict) and "log" in item:
                return item["log"]
    # If we couldn't find the log, return full step as a string
    return str(step)


def crew_step_callback(output):
    if "crew_step_callback" not in st.session_state:
        st.session_state.crew_step_callback = []
    st.session_state.crew_step_callback.append(output)
    with st.session_state.crew_step_container.container():
        with st.expander("Completed Steps", expanded=False):
            for i, step in enumerate(st.session_state.crew_step_callback):
                st.markdown(f"**Step {i+1}:**")
                step_log = extract_step_output(step)
                st.markdown(step_log)
                if i < len(st.session_state.crew_step_callback) - 1:
                    st.markdown("---")


def crew_task_callback(output):
    if "crew_task_callback" not in st.session_state:
        st.session_state.crew_task_callback = []
    st.session_state.crew_task_callback.append(output)
    with st.session_state.crew_task_container.container():
        with st.expander("Completed Tasks", expanded=False):
            for i, task in enumerate(st.session_state.crew_task_callback):
                st.markdown(f"**Task {i+1} Result:**")
                st.markdown(task)
                if i < len(st.session_state.crew_task_callback) - 1:
                    st.markdown("---")
