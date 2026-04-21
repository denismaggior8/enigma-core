from enigmacore.device_state import DeviceState
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM4 import EnigmaM4
from enigmapython.EtwPassthrough import EtwPassthrough
from enigmapython.SwappablePlugboard import SwappablePlugboard
from enigmacore.at_registry import at_command

@at_command("ENIGMA", "Set/Get the Enigma machine model: AT+ENIGMA=M3|M4  AT+ENIGMA?")
def _enigma_cmd(params, is_query):
    state = DeviceState.get()
    if is_query:
        if state.enigma is None: return True, "+ENIGMA: NONE"
        elif isinstance(state.enigma, EnigmaM3): return True, "+ENIGMA: M3"
        elif isinstance(state.enigma, EnigmaM4): return True, "+ENIGMA: M4"
    if not params: return False, "NO PARAM"
    p = params[0].upper()
    try:
        if p == "M3":
            from enigmapython.EnigmaM3RotorVIII import EnigmaM3RotorVIII
            state.enigma = EnigmaM3(plugboard=SwappablePlugboard(), rotor1=EnigmaM3RotorVIII(), rotor2=EnigmaM3RotorVIII(), rotor3=EnigmaM3RotorVIII(), reflector=None, etw=EtwPassthrough(), auto_increment_rotors=True)
            return True, None
        elif p == "M4":
            from enigmapython.EnigmaM3RotorVIII import EnigmaM3RotorVIII
            from enigmapython.EnigmaM3RotorIII import EnigmaM3RotorIII
            from enigmapython.EnigmaM3RotorIV import EnigmaM3RotorIV
            from enigmapython.EnigmaM4RotorGamma import EnigmaM4RotorGamma
            state.enigma = EnigmaM4(plugboard=SwappablePlugboard(), rotor1=EnigmaM3RotorVIII(), rotor2=EnigmaM3RotorIII(), rotor3=EnigmaM3RotorIV(), rotor4=EnigmaM4RotorGamma(), reflector=None, etw=EtwPassthrough(), auto_increment_rotors=True)
            return True, None
    except Exception as e:
        return False, f"INIT ERR: {e}"
    return False, "BAD PARAM"
