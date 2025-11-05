
# ---------- Registry ----------
_COMMANDS = {}
def at_command(name, help_text=""):
    def deco(fn):
        _COMMANDS[name.upper()] = (fn, help_text)
        return fn
    return deco