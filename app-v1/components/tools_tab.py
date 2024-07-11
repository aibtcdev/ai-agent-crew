import importlib
import inspect
import streamlit as st


def get_tool_classes():
    import aibtcdev_tools

    importlib.reload(aibtcdev_tools)

    all_attributes = dir(aibtcdev_tools)

    tool_classes = [
        getattr(aibtcdev_tools, attr)
        for attr in all_attributes
        if isinstance(getattr(aibtcdev_tools, attr), type)
        and getattr(aibtcdev_tools, attr).__module__ == "aibtcdev_tools"
        and hasattr(getattr(aibtcdev_tools, attr), "ui_friendly_name")
    ]

    return tool_classes


def get_type_name(field_type):
    if field_type is None:
        return "Any"
    try:
        return field_type.__name__
    except AttributeError:
        return str(field_type)


def render_tools_tab():
    tool_classes = get_tool_classes()

    for tool_class in tool_classes:
        st.subheader(getattr(tool_class, "ui_friendly_name", tool_class.__name__))

        for name, method in tool_class.__dict__.items():
            if isinstance(method, staticmethod):
                tool_object = method.__func__

                if hasattr(tool_object, "name") and hasattr(tool_object, "description"):
                    with st.expander(f"{tool_object.name}"):
                        st.write(f"**Description:** {tool_object.description}")

                        if (
                            hasattr(tool_object, "args_schema")
                            and tool_object.args_schema.__fields__
                        ):
                            st.write("**Arguments:**")
                            for (
                                field_name,
                                field,
                            ) in tool_object.args_schema.__fields__.items():
                                type_name = get_type_name(field.type_)
                                st.write(f"- {field_name}: {type_name}")
                        else:
                            st.write("**Arguments:** No arguments")

                        if hasattr(tool_object, "func"):
                            try:
                                source = inspect.getsource(tool_object.func)
                                bun_run_line = next(
                                    (
                                        line
                                        for line in source.split("\n")
                                        if "bun_run" in line
                                    ),
                                    None,
                                )
                                if bun_run_line:
                                    st.write("**BunScriptRunner command:**")
                                    st.code(bun_run_line.strip(), language="python")
                            except Exception as e:
                                st.write("Unable to extract BunScriptRunner command.")
                else:
                    st.write(f"**{name}** - No tool information available.")
