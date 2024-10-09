import streamlit as st
from typing import Dict, Any, Union
from crewai.tasks.task_output import TaskOutput
from crewai.agents.parser import AgentAction


def format_task_output(task_output: TaskOutput) -> str:
    """Format TaskOutput for display."""
    output = f"**Description**: {task_output.description}\n\n"
    output += f"**Agent**: {task_output.agent}\n\n"

    if task_output.expected_output:
        output += f"**Expected Output**: {task_output.expected_output}\n\n"

    # output += f"**Output Format**: {task_output.output_format.value}\n\n"

    # if task_output.output_format.value == "JSON":
    #    output += f"**JSON Output**:\n```json\n{task_output.json}\n```\n\n"
    # elif task_output.pydantic:
    #    output += f"**Structured Output**:\n```\n{task_output.pydantic}\n```\n\n"
    # else:
    #    output += f"**Raw Output**:\n{task_output.raw}\n\n"

    return output


def format_agent_action(agent_action: AgentAction) -> str:
    """Format AgentAction for display."""
    output = f"**Thought**: {agent_action.thought}\n\n"
    output += f"**Action**: {agent_action.tool}\n\n"
    output += f"**Input**: {agent_action.tool_input}\n\n"
    # if hasattr(agent_action, "result"):
    #    output += f"**Result**: {agent_action.result}\n\n"
    return output


def crew_step_callback(step: Union[Dict[str, Any], AgentAction]):
    if "crew_step_callback" not in st.session_state:
        st.session_state.crew_step_callback = []
    st.session_state.crew_step_callback.append(step)
    with st.session_state.crew_step_container.container():
        with st.expander("Completed Steps", expanded=False):
            for i, step_data in enumerate(st.session_state.crew_step_callback):
                st.markdown(f"#### Step {i+1}")
                if isinstance(step_data, dict) and "task_output" in step_data:
                    task_output = TaskOutput(**step_data["task_output"])
                    st.markdown(format_task_output(task_output))
                elif isinstance(step_data, AgentAction):
                    st.markdown(format_agent_action(step_data))
                else:
                    st.markdown(f"```\n{step_data}\n```")
                if i < len(st.session_state.crew_step_callback) - 1:
                    st.markdown("---")


def crew_task_callback(task: TaskOutput):
    if "crew_task_callback" not in st.session_state:
        st.session_state.crew_task_callback = []
    st.session_state.crew_task_callback.append(task)
    with st.session_state.crew_task_container.container():
        with st.expander("Completed Tasks", expanded=True):
            for i, task_output in enumerate(st.session_state.crew_task_callback):
                st.markdown(f"#### Task {i+1}")
                st.markdown(format_task_output(task_output))
                if i < len(st.session_state.crew_task_callback) - 1:
                    st.markdown("---")
