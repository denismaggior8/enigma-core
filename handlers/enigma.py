from at_registry import at_command

@at_command("ENIGMA", "Set/Get the Enigma machine model: AT+ENIGMA=M3|M4  AT+ENIGMA?")
def _enigma_cmd(params, is_query):
    global _enigma, _plugboard, _rotor1, _rotor2, _rotor3, _reflector
    if is_query:
        if _enigma is None:
            return True, "+ENIGMA: NONE"
        else:
            return True, "+ENIGMA: M3"
    if not params:
        return False, "NO PARAM"
    p = params[0].upper()
    if p == "M3":
        _enigma = EnigmaM3(_plugboard, _rotor1, _rotor2, _rotor3, _reflector, _etw)
        return True, None
    else:
        return False, "BAD PARAM"