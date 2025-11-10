from at_registry import at_command
from device_state import DeviceState

@at_command("PLUGBOARD", "Swap characters in the Enigma plugboard: AT+PLUGBOARD=<char to substitute>,<replacement char>  AT+PLUGBOARD?")
def _plugboard_cmd(params, is_query):
    """
    AT+PLUGBOARD=<pair>     → sets a plugboard pair (e.g. a,z)
    AT+PLUGBOARD?           → queries current plugboard configuration
    """

    state = DeviceState.get()

    if state.enigma is None:
        return False, "ENIGMA NOT CONFIGURED"

    if is_query:
        return True, "+PLUGBOARD: {}".format(state.enigma.plugboard.wiring)

    # --- SET MODE ---
    if not params or len(params) != 2:
        return False, "INVALID CHAR PAIR"
    
    a = params[0].lower()
    b = params[1].lower()
    
     # Validate characters
    if a not in state.enigma.alphabet_list or b not in state.enigma.alphabet_list:
        return False, "INVALID CHAR/S"

    # swap chars
    state.enigma.plugboard.swap(a, b)

    return True, None