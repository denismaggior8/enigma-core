from at_decorators import at_command
from device_state import DeviceState

@at_command("REFLECTOR", help="Set/Get reflector type: AT+REFLECTOR=<type> or AT+REFLECTOR?")
def handle_reflector(params, is_query):
    """
    Handle AT+REFLECTOR command.

    Usage:
      AT+REFLECTOR?           -> Query current reflector type
      AT+REFLECTOR=B          -> Set reflector type B (if allowed for the current model)
    """
    state = DeviceState()

    # allowed reflectors depending on machine type
    model_reflectors = {
        "M3": ["UKW-B", "UKW-C"],
        "M4": ["UKW-B", "UKW-C", "UKW-Thin"],
    }

    # ensure we have a known machine type
    if state.enigma is None

    allowed = model_reflectors.get(model.upper(), [])

    # QUERY mode
    if is_query:
        current = getattr(state, "reflector", None)
        if current:
            print(f"+REFLECTOR:{current}")
        else:
            print("+REFLECTOR:NONE")
        return "OK"

    # SET mode
    if not params or len(params) != 1:
        return "ERROR: Invalid syntax"

    reflector_type = str(params[0]).upper()

    # accept both shorthand (B, C) and full names (UKW-B)
    if reflector_type in ("B", "C"):
        reflector_type = "UKW-" + reflector_type

    if reflector_type not in allowed:
        return f"ERROR: Reflector {reflector_type} not valid for {model}"

    state.reflector = reflector_type
    return "OK"