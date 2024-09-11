import streamlit as st
from utils.session import get_crew_class


def render_execution_tab(crew_selection):
    crew_class = get_crew_class(crew_selection)

    if crew_class is None:
        st.warning(
            f"No crew found for {crew_selection}. Please check your crew definitions."
        )
        return

    try:
        # Create an instance of the crew class and call its render_crew method
        crew_instance = crew_class()
        crew_instance.render_crew()
    except AttributeError:
        st.error(
            f"The selected crew '{crew_selection}' doesn't have a render_crew method."
        )
    except Exception as e:
        st.error(f"An error occurred while rendering the crew: {str(e)}")
