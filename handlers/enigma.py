from at_registry import at_command
from device_state import DeviceState

# Enigma machine imports
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM3RotorI import EnigmaM3RotorI
from enigmapython.EnigmaM3RotorII import EnigmaM3RotorII
from enigmapython.EnigmaM3RotorIII import EnigmaM3RotorIII
from enigmapython.EnigmaM3RotorIV import EnigmaM3RotorIV
from enigmapython.EnigmaM3RotorV import EnigmaM3RotorV
from enigmapython.EnigmaM3RotorVI import EnigmaM3RotorVI
from enigmapython.EnigmaM3RotorVII import EnigmaM3RotorVII
from enigmapython.EnigmaM3RotorVIII import EnigmaM3RotorVIII

@at_command("ENIGMA", "Set/Get the Enigma machine model: AT+ENIGMA=M3|M4  AT+ENIGMA?")
def _enigma_cmd(params, is_query):
    state = DeviceState.get()
    if is_query:
        if state.enigma is None:
            return True, "+ENIGMA: NONE"
        elif isinstance(state.enigma, EnigmaM3) :
            return True, "+ENIGMA: M3"
    if not params:
        return False, "NO PARAM"
    p = params[0].upper()
    if p == "M3":
        state.enigma = EnigmaM3(plugboard=None, rotor1=None, rotor2=None, rotor3=None, reflector=None, etw=None)
        return True, None
    else:
        return False, "BAD PARAM"