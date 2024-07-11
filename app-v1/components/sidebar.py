import streamlit as st
from aibtcdev_utils import (
    load_config,
    update_model_settings,
    remove_model_settings,
)


def render_sidebar(app_config):
    with st.sidebar:
        st.title("AIBTCdev Settings")

        with st.expander("Chat Settings", expanded=False):
            if st.button("Clear Chat History", key="clear_chat_history"):
                st.session_state.messages = []
                st.success("Chat history cleared!")

        with st.expander("Current LLM Settings", expanded=False):
            llm_options = list(app_config["model_settings"].keys())

            st.selectbox(
                "Select LLM:",
                options=llm_options,
                key="llm_model",
                on_change=update_model,
            )
            st.text_input(
                "API Base URL:",
                value=st.session_state.get("api_base", ""),
                key="api_base",
            )
            st.text_input(
                "Model Name:", value=st.session_state.model_name, key="model_name"
            )
            st.text_input(
                "API Key:",
                value=st.session_state.api_key,
                key="api_key",
                type="password",
            )

            if st.button("Update LLM Provider"):
                update_model_settings(
                    app_config,
                    st.session_state.llm_model,
                    st.session_state.model_name,
                    st.session_state.api_base,
                )
                st.success("LLM settings updated successfully!")

        with st.expander("Add LLM Provider", expanded=False):
            new_provider = st.text_input("New Provider Name", placeholder="GroqCloud")
            new_model_name = st.text_input("New Model Name", placeholder="Llama3-70B")
            new_api_base = st.text_input(
                "New API Base URL", placeholder="https://api.groq.com/openai/v1"
            )

            if st.button("Add Provider"):
                if new_provider and new_model_name and new_api_base:
                    update_model_settings(
                        app_config, new_provider, new_model_name, new_api_base
                    )
                    st.success(f"Provider {new_provider} added successfully!")
                else:
                    st.error("Please fill in all fields to add a provider.")

        with st.expander("Remove LLM Provider", expanded=False):
            provider_to_remove = st.selectbox(
                "Select Provider to Remove",
                options=list(app_config["model_settings"].keys()),
            )
            if st.button("Remove Provider"):
                if remove_model_settings(app_config, provider_to_remove):
                    st.success(f"Provider {provider_to_remove} removed successfully!")
                else:
                    st.error("Selected provider not found.")


def update_model():
    model_name = st.session_state.llm_model
    app_config = load_config()
    model_settings = app_config["model_settings"].get(
        model_name, app_config["model_settings"]["OpenAI"]
    )
    st.session_state.api_base = model_settings["OPENAI_API_BASE"]
    st.session_state.model_name = model_settings["OPENAI_MODEL_NAME"]
    # should this load from .env? changes between Anthropic and OpenAI
    # st.session_state.api_key = model_settings["OPENAI_API_KEY"]
