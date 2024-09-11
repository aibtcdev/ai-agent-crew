import streamlit as st


def crew_step_callback(output):
    if "crew_step_callback" not in st.session_state:
        st.session_state.crew_step_callback = []
    st.session_state.crew_step_callback.append(output)
    with st.session_state.crew_step_container.container():
        for i, step in enumerate(st.session_state.crew_step_callback):
            with st.expander(f"Step {i+1}", expanded=False):
                st.markdown(step)


def crew_task_callback(output):
    if "crew_task_callback" not in st.session_state:
        st.session_state.crew_task_callback = []
    st.session_state.crew_task_callback.append(output)
    with st.session_state.crew_task_container.container():
        for i, task in enumerate(st.session_state.crew_task_callback):
            with st.expander(f"Task {i+1}", expanded=False):
                st.markdown(task)
