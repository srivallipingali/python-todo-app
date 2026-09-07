LIGHT = {
    "bg": "#F5F5F5",
    "fg": "#222222",
    "button": "#D8B4E2",
    "entry": "#FFFFFF",
}

DARK = {
    "bg": "#222222",
    "fg": "#F20059",
    "button": "#6C4A8E",
    "entry": "#333333",
}


def get_theme(dark_mode):
    return DARK if dark_mode else LIGHT
