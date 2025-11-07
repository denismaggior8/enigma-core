from at_registry import at_command
from device_state import DeviceState

# Enigma machine imports
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM4 import EnigmaM4
from enigmapython.EtwPassthrough import EtwPassthrough
from enigmapython.PlugboardPassthrough import PlugboardPassthrough


@at_command("ENIGMA", "Set/Get the Enigma machine model: AT+ENIGMA=M3|M4  AT+ENIGMA?")
def _enigma_cmd(params, is_query):
    state = DeviceState.get()
    if is_query:
        if state.enigma is None:
            return True, "+ENIGMA: NONE"
        elif isinstance(state.enigma, EnigmaM3) :
            return True, "+ENIGMA: M3"
        elif isinstance(state.enigma, EnigmaM4) :
            return True, "+ENIGMA: M4"
    if not params:
        return False, "NO PARAM"
    p = params[0].upper()
    if p == "M3" and not isinstance(state.enigma, EnigmaM3):
        state.enigma = EnigmaM3(plugboard=PlugboardPassthrough(), rotor1=None, rotor2=None, rotor3=None, reflector=None, etw=EtwPassthrough(), auto_increment_rotors=True)
        return True, None
    if p == "M4" and not isinstance(state.enigma, EnigmaM4):
        state.enigma = EnigmaM4(plugboard=PlugboardPassthrough(), rotor1=None, rotor2=None, rotor3=None, rotor4=None, reflector=None, etw=EtwPassthrough(), auto_increment_rotors=True)
        return True, None
    else:
        return False, "BAD PARAM"