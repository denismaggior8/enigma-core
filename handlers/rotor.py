# handlers/rotor.py
from at_registry import at_command   # or from enigmacore import at_command if registry is there
from device_state import DeviceState
from bimap import BiMap

# Enigma rotor imports
from enigmapython.Rotor import Rotor
# M3 specific
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM3RotorI import EnigmaM3RotorI
from enigmapython.EnigmaM3RotorII import EnigmaM3RotorII
from enigmapython.EnigmaM3RotorIII import EnigmaM3RotorIII
from enigmapython.EnigmaM3RotorIV import EnigmaM3RotorIV
from enigmapython.EnigmaM3RotorV import EnigmaM3RotorV
from enigmapython.EnigmaM3RotorVI import EnigmaM3RotorVI
from enigmapython.EnigmaM3RotorVII import EnigmaM3RotorVII
from enigmapython.EnigmaM3RotorVIII import EnigmaM3RotorVIII
# M4 specific
from enigmapython.EnigmaM4 import EnigmaM4
from enigmapython.EnigmaM4RotorBeta import EnigmaM4RotorBeta
from enigmapython.EnigmaM4RotorGamma import EnigmaM4RotorGamma

rotor_bimap = BiMap()
rotor_bimap.put("I", EnigmaM3RotorI)

@at_command("ROTOR", "Set/Get rotor configuration: AT+ROTOR=<index>,<type>,<ring>,<pos>  AT+ROTOR=<index>?")
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
    
    # if enigma machine has not configured before
    if state.enigma is None:
        return False, "ENIGMA NOT CONFIGURED"   
    # everything is OK so far, store rotor in DeviceState
    elif isinstance(state.enigma, EnigmaM3):
        print("rotor: {} type: {}, ring: {}, pos: {}".format(idx, rotor_type, ring, pos))
        #rotor = rotor_bimap.get(rotor_type)(pos,ring)  # validate rotor type
        #print(rotor)
    #    pass
    #elif isinstance(state.enigma, EnigmaM4):
    #    pass
    

    #state.enigma.rotors[idx] = (rotor_type, ring, pos)

    return True, None