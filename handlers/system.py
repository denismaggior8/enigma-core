from at_registry import _COMMANDS, at_command

# ---------- Auto HELP ----------
@at_command("HELP", "Show this help")
def _help_cmd(params, is_query):
    lines = ["Available commands:"]
    lines.append("  AT - basic attention")
    for k in sorted(_COMMANDS.keys()):
        #if k == "HELP":
        #    continue
        h = _COMMANDS[k][1] or ""
        lines.append("  AT+{} - {}".format(k, h))
    return True, "\n".join(lines)