from at_registry import at_command
from device_state import DeviceState

@at_command("PLUGBOARD")
def handle_plugboard(params, is_query):
    state = DeviceState()

    # --- Query Mode ---
    if is_query:
        if not state.plugboard:
            send_err("No plugboard connections set")
            return
        pairs = []
        used = set()
        for k, v in state.plugboard.items():
            if k not in used:
                pairs.append(f"{k}-{v}")
                used.add(k)
                used.add(v)
        send_ok(",".join(pairs))
        return

    # --- Set Mode ---
    if not params or len(params) != 1:
        send_err("Invalid parameters")
        return

    pairs_str = params[0]
    try:
        pairs = [p.strip().upper() for p in pairs_str.split(",") if p.strip()]
    except Exception:
        send_err("Bad format")
        return

    new_mapping = {}
    used_letters = set()

    for pair in pairs:
        if len(pair) != 3 or pair[1] != '-':
            send_err(f"Invalid pair '{pair}'")
            return
        a, b = pair[0], pair[2]
        if a in used_letters or b in used_letters:
            send_err(f"Duplicate letter in pair '{pair}'")
            return
        new_mapping[a] = b
        new_mapping[b] = a
        used_letters.update([a, b])

    # store
    state.plugboard = new_mapping
    send_ok("Plugboard updated")