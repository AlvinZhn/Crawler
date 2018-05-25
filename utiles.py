def escape(s):
    """
    Escape special characters.
    \ / : * ? " < > | ”
    """
    for old, new in [("\\", "_"), ("/", "_"), (":", "_"), ("?", "_"),
                     ("*", "_"), ("\"", "_"), ("<", "("), (">", ")"),
                     ("|", "_"), ("“", "'"), ("”", "'"), (" ", "")]:
        s = s.replace(old, new)
    return s