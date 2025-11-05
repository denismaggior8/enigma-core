# handlers/rotor.py
from at_registry import at_command   # or from enigmacore import at_command if registry is there
from device_state import DeviceState

@at_command("ROTOR")
def  _rotor_cmd(params, is_query):
    """
    params: list of strings returned by parser
      SET: params = [index, type, ring, pos]
      QUERY: params = [index] and is_query=True
    Returns: (ok: bool, payload: str|None)
    """
    # parse presence / errors
    if params is None:
        return False, "PARSE ERROR"

    # must have at least index
    if not params or len(params) < 1:
        return False, "MISSING INDEX"

    # index must be numeric
    try:
        idx = int(params[0])
    except Exception:
        return False, "BAD INDEX"

    state = DeviceState()

    # QUERY: AT+ROTOR=<index>?
    if is_query:
        if len(params) != 1:
            return False, "INVALID QUERY"
        rotors = getattr(state, "rotors", None) or {}
        cfg = rotors.get(idx)
        if cfg is None:
            # ESP-AT style: indicate NONE if not set
            return True, f"+ROTOR: {idx},NONE"
        # cfg stored as tuple (type, ring, pos)
        rotor_type, ring, pos = cfg
        return True, f"+ROTOR: {idx},{rotor_type},{ring},{pos}"

    # SET: expect exactly 4 params total (index + 3 others?) <-- we agreed fixed 4 params after index, but earlier you specified index + 3 or +4?
    # You told earlier "fixed 4" after index; here we expect index + 3 values? adjust to index + 4 if needed.
    # According to last definition: AT+ROTOR=<index>,<type>,<ring>,<position> -> that's 4 total including index? index + 3 body.
    # We'll follow: index + 3 body (type, ring, position)
    if len(params) != 4:
        # If you meant index + 3, change to len(params) != 4 -> adjust comment. Current expects index + 3 body values -> len==4
        return False, "NEED 4 PARAMS"

    rotor_type = params[1]
    # uppercase already enforced by parser; keep as-is
    try:
        ring = int(params[2])
        pos = int(params[3])
    except Exception:
        return False, "INVALID NUMERIC PARAM"

    # store in DeviceState.rotors dict
    if not hasattr(state, "rotors") or state.rotors is None:
        state.rotors = {}
    state.rotors[idx] = (rotor_type, ring, pos)

    return True, None