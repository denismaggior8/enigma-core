# handlers/rotor.py
from ..at_registry import at_command   # or from enigmacore import at_command if registry is there
from ..device_state import DeviceState
from ..bimap import BiMap

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
rotor_bimap.put("II", EnigmaM3RotorII)
rotor_bimap.put("III", EnigmaM3RotorIII)
rotor_bimap.put("IV", EnigmaM3RotorIV)
rotor_bimap.put("V", EnigmaM3RotorV)
rotor_bimap.put("VI", EnigmaM3RotorVI)
rotor_bimap.put("VII", EnigmaM3RotorVII)
rotor_bimap.put("VIII", EnigmaM3RotorVIII)
rotor_bimap.put("B", EnigmaM4RotorBeta)
rotor_bimap.put("G", EnigmaM4RotorGamma)

@at_command("ROTOR", "Set/Get rotor configuration: AT+ROTOR=<index>,<type>,<ring>,<pos>  AT+ROTOR=<index>?")
def  _rotor_cmd(params, is_query):
    
    """
    params: list of strings returned by parser
      SET: params = [index, type, ring, pos]
      QUERY: params = [index] and is_query=True
    Returns: (ok: bool, payload: str|None)
    """

    state = DeviceState()

    # if enigma machine has not been configured yet
    if state.enigma is None:
        return False, "ENIGMA NOT CONFIGURED"   

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

    # QUERY: AT+ROTOR=<index>?
    if is_query:

        # no query param, invalid query
        if len(params) != 1:
            return False, "INVALID QUERY"
        
        # get rotor at index
        rotor = state.enigma.rotors[idx]

        # if rotor at index is not set
        if rotor is None:
            # ESP-AT style: indicate NONE if not set
            return True, f"+ROTOR: {idx},NONE"
        
        return True, f"+ROTOR: {idx},{rotor_bimap.inverse_get(rotor.__class__)},{rotor.ring},{rotor.position}"

    # check number of params (should be 4 for SET)
    if len(params) != 4:
        return False, "NEED 4 PARAMS"

    rotor_type = params[1]
    # uppercase already enforced by parser; keep as-is
    try:
        ring = int(params[2])
        pos = int(params[3])
    except Exception:
        return False, "INVALID NUMERIC PARAM"
    
    # if index is negative
    if idx < 0:
        return False, "INVALID ROTOR INDEX"

    # if M3 machine type
    if isinstance(state.enigma, EnigmaM3):
        if idx > 2:
            return False, "INVALID ROTOR INDEX FOR M3"
        
        if rotor_type == "B" or rotor_type == "G":
            return False, "INVALID ROTOR FOR M3"
        
    # if M4 machine type
    elif isinstance(state.enigma, EnigmaM4):
        if idx > 3:
            return False, "INVALID ROTOR INDEX FOR M4"
        
    rotor = rotor_bimap.get(rotor_type)

    # if rotor type is unknown
    if rotor is None:
        return False, "UNKNOWN ROTOR TYPE"
        
    # everything is OK, set Enigma rotor and return True
    state.enigma.add_rotor(idx, rotor(ring,pos))  
    return True, None