import streamlit as st


def render_execution_tab(crews):
    user_input = st.text_area(
        "Initial Input", "Enter your instructions or query here..."
    )

    selected_crew = st.selectbox("Select Crew", options=list(crews.keys()))

    crew = crews[selected_crew]
    available_tasks = [task.description for task in crew.tasks]
    selected_tasks = st.multiselect("Select Tasks", options=available_tasks)

    input_dict = {"user_input": user_input}

    if st.button("Execute"):
        st.write("Execution Output:")
        tasks_to_execute = [
            task for task in crew.tasks if task.description in selected_tasks
        ]
        crew.tasks = tasks_to_execute
        result = crew.kickoff(inputs=input_dict)
        st.write(result)
