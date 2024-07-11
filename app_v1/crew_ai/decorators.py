from functools import wraps


def ui_class(name):
    def decorator(cls):
        cls.ui_name = name
        return cls

    return decorator


def ui_method(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.ui_name = name
        return wrapper

    return decorator
