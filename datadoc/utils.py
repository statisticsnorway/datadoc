def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook"""
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False
