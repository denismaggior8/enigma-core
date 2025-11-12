from ..at_registry import at_command

# ---------- Example LED ----------
try:
    from machine import Pin
    try:
        _led = Pin("LED", Pin.OUT)
    except Exception:
        try:
            _led = Pin(2, Pin.OUT)
        except Exception:
            _led = None
except Exception:
    _led = None

@at_command("LED", "Control LED: AT+LED=0|1  AT+LED?")
def _led_cmd(params, is_query):
    if is_query:
        if _led is None:
            return False, "NO LED"
        val = _led.value() if hasattr(_led, "value") else None
        return True, "+LED: {}".format(1 if val else 0)
    if not params:
        return False, "NO PARAM"
    p = params[0].upper()
    if p in ("1", "ON", "TRUE"):
        if _led is not None:
            _led.value(1)
        return True, None
    if p in ("0", "OFF", "FALSE"):
        if _led is not None:
            _led.value(0)
        return True, None
    return False, "BAD PARAM"