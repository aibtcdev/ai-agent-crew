import os
import yaml
from dotenv import load_dotenv

model_filename = "aibtcdev_model_settings.yaml"


# Get model settings from file and env
def get_model_settings():
    load_dotenv()
    settings = load_model_settings()
    for provider, provider_settings in settings.items():
        for key, value in provider_settings.items():
            env_var = f"{provider.upper()}_{key}"
            if env_var in os.environ:
                settings[provider][key] = os.environ[env_var]
    return settings


# Load model settings from YAML file
def load_model_settings():
    with open(model_filename, "r") as file:
        return yaml.safe_load(file)


# Save model settings to YAML file
def save_model_settings(settings):
    with open(model_filename, "w") as file:
        yaml.dump(settings, file)
