import streamlit as st
from utils import update_session_state


def render_sidebar():
    with st.sidebar:
        st.title("AIBTCdev Settings")

        with st.expander("Chat Settings", expanded=False):
            if st.button("Clear Chat History", key="clear_chat_history"):
                st.session_state.messages = []
                st.success("Chat history cleared!")

        with st.expander("Current LLM Settings", expanded=False):
            llm_options = ["OpenAI", "Anthropic"]  # extend this list as needed

            st.selectbox(
                "Select LLM:",
                options=llm_options,
                key="llm_model",
                on_change=update_model,
            )
            st.text_input(
                "API Base URL:",
                value=st.session_state.api_base,
                key="api_base",
                on_change=lambda: update_session_state(
                    "api_base", st.session_state.api_base
                ),
            )
            st.text_input(
                "Model Name:",
                value=st.session_state.model_name,
                key="model_name",
                on_change=lambda: update_session_state(
                    "model_name", st.session_state.model_name
                ),
            )
            st.text_input(
                "API Key:",
                value=st.session_state.api_key,
                key="api_key",
                type="password",
                on_change=lambda: update_session_state(
                    "api_key", st.session_state.api_key
                ),
            )

            if st.button("Update LLM Provider"):
                update_session_state("llm_model", st.session_state.llm_model)
                update_session_state("api_base", st.session_state.api_base)
                update_session_state("model_name", st.session_state.model_name)
                update_session_state("api_key", st.session_state.api_key)
                st.success("LLM settings updated successfully!")

        with st.expander("Add LLM Provider", expanded=False):
            new_provider = st.text_input("New Provider Name", placeholder="GroqCloud")
            new_model_name = st.text_input("New Model Name", placeholder="Llama3-70B")
            new_api_base = st.text_input(
                "New API Base URL", placeholder="https://api.groq.com/openai/v1"
            )

            if st.button("Add Provider"):
                if new_provider and new_model_name and new_api_base:
                    if "custom_providers" not in st.session_state:
                        st.session_state.custom_providers = {}
                    st.session_state.custom_providers[new_provider] = {
                        "model_name": new_model_name,
                        "api_base": new_api_base,
                    }
                    st.success(f"Provider {new_provider} added successfully!")
                else:
                    st.error("Please fill in all fields to add a provider.")

        with st.expander("Remove LLM Provider", expanded=False):
            if (
                "custom_providers" in st.session_state
                and st.session_state.custom_providers
            ):
                provider_to_remove = st.selectbox(
                    "Select Provider to Remove",
                    options=list(st.session_state.custom_providers.keys()),
                )
                if st.button("Remove Provider"):
                    if provider_to_remove in st.session_state.custom_providers:
                        del st.session_state.custom_providers[provider_to_remove]
                        st.success(
                            f"Provider {provider_to_remove} removed successfully!"
                        )
                    else:
                        st.error("Selected provider not found.")
            else:
                st.write("No custom providers to remove.")


def update_model():
    model_name = st.session_state.llm_model
    if model_name == "OpenAI":
        update_session_state("api_base", "https://api.openai.com/v1")
        update_session_state("model_name", "gpt-3.5-turbo")
    elif model_name == "Anthropic":
        update_session_state("api_base", "https://api.anthropic.com")
        update_session_state("model_name", "claude-2")
    elif model_name in st.session_state.get("custom_providers", {}):
        provider_settings = st.session_state.custom_providers[model_name]
        update_session_state("api_base", provider_settings["api_base"])
        update_session_state("model_name", provider_settings["model_name"])
    # The API key is not updated here for security reasons
    # Users should input the API key manually when changing providers
