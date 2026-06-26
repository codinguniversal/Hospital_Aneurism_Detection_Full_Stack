import importlib

def load_class_dynamically(class_path: str):
    """Resolves a string path into a live Python class object."""
    try:
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Failed to dynamically load class at '{class_path}': {e}")