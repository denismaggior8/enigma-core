# handlers/reflector.py

from at_registry import at_command 
from device_state import DeviceState
from bimap import BiMap

# Enigma reflector imports
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM4 import EnigmaM4
# M3 specific
from enigmapython.ReflectorUKWC import ReflectorUKWC
from enigmapython.ReflectorUKWB import ReflectorUKWB
# M4 specific
from enigmapython.ReflectorUKWBThin import ReflectorUKWBThin
from enigmapython.ReflectorUKWCThin import ReflectorUKWCThin


reflector_bimap = BiMap()
reflector_bimap.put("B", ReflectorUKWC)
reflector_bimap.put("C", ReflectorUKWB)
reflector_bimap.put("BT", ReflectorUKWBThin)
reflector_bimap.put("CT", ReflectorUKWCThin)

@at_command("REFLECTOR", "Set/Get reflector type: AT+REFLECTOR=<type> or AT+REFLECTOR?")
def _reflector_cmd(params, is_query):
    """
    Handle AT+REFLECTOR command.

    Usage:
      AT+REFLECTOR?           -> Query current reflector type
      AT+REFLECTOR=B          -> Set reflector type B (if allowed for the current model)
    """
    state = DeviceState()

    # if enigma machine has not been configured yet
    if state.enigma is None:
        return False, "ENIGMA NOT CONFIGURED"
    
    # parse presence / errors
    if params is None:
        return False, "PARSE ERROR"

    # QUERY mode
    if is_query:
        if state.enigma.reflector is None:
            # ESP-AT style: indicate NONE if not set
            return True, f"+REFLECTOR: NONE"
        
        return True, f"+REFLECTOR: {reflector_bimap.inverse_get(state.enigma.reflector.__class__)}"

    # SET mode
    if not params or len(params) != 1:
        return False, "NEED 1 PARAM"

    reflector_type = str(params[0]).upper()

    if isinstance(state.enigma, EnigmaM3) and reflector_type not in ("B", "C"):
        return False, "INVALID REFLECTOR TYPE"

    if isinstance(state.enigma, EnigmaM4) and reflector_type not in ("BT", "CT"):
        return False, "INVALID REFLECTOR TYPE"

    reflector = reflector_bimap.get(reflector_type)

    # everything is OK, set Enigma reflector and return True
    state.enigma.reflector= reflector() 
    return True, None