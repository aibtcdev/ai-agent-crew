import anthropic
import os
import yaml
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

CONFIG_FILENAME = "aibtcdev_config.yaml"


def load_config():
    load_dotenv()
    with open(CONFIG_FILENAME, "r") as file:
        config = yaml.safe_load(file)

    # Override with environment variables
    for section, settings in config.items():
        if isinstance(settings, dict):
            for key in settings.items():
                env_var = f"{section.upper()}_{key.upper()}"
                if env_var in os.environ:
                    settings[key] = os.environ[env_var]

    return config


def save_config(config):
    with open(CONFIG_FILENAME, "w") as file:
        yaml.dump(config, file)


def init_session_state(config):
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = "OpenAI"
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")
    if "api_base" not in st.session_state:
        st.session_state.api_base = config["model_settings"]["OpenAI"][
            "OPENAI_API_BASE"
        ]
    if "model_name" not in st.session_state:
        st.session_state.model_name = config["model_settings"]["OpenAI"][
            "OPENAI_MODEL_NAME"
        ]


def update_model_settings(config, provider, model_name, api_base):
    config["model_settings"][provider] = {
        "OPENAI_MODEL_NAME": model_name,
        "OPENAI_API_BASE": api_base,
    }
    save_config(config)


def remove_model_settings(config, provider):
    if provider in config["model_settings"]:
        del config["model_settings"][provider]
        save_config(config)
        return True
    return False


def get_llm(model, api_key, api_base):
    if model == "Anthropic":
        return anthropic.Anthropic(api_key=api_key)
    else:
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=api_base,
        )
