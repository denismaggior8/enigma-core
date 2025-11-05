# atcore.py
# Portable AT command handler: works on CPython (macOS) and MicroPython (USB CDC / stdin)
# Drop on board as main.py or import as a module.

import sys
import time

IS_MICROPY = sys.implementation.name == "micropython"

def is_real_board():
    if not IS_MICROPY:
        return False
    try:
        import machine
        return hasattr(machine, "reset") or hasattr(machine, "freq")
    except Exception:
        return False

IS_BOARD = is_real_board()

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

_enigma = None
_etw = None
_plugboard = None
_rotor1 = None
_rotor2 = None
_rotor3 = None
_reflector = None

# Try uselect (MicroPython) or select (CPython)
_uselect = None
try:
    import uselect as _uselect
except Exception:
    try:
        import select as _uselect
    except Exception:
        _uselect = None

# MicroPython compatibility for time functions
try:
    ticks_ms = time.ticks_ms
    ticks_diff = time.ticks_diff
except Exception:
    def ticks_ms(): return int(time.time() * 1000)
    def ticks_diff(a, b): return a - b

# ---------- Output helpers ----------
def send_line(s):
    try:
        sys.stdout.write(str(s) + "\r\n")
    except Exception:
        try:
            sys.stdout.buffer.write((str(s) + "\r\n").encode())
        except Exception:
            pass

def send_ok(payload=None):
    if payload is not None:
        send_line(payload)
    send_line("OK")

def send_err(msg=None):
    if msg:
        send_line("ERROR: " + str(msg))
    else:
        send_line("ERROR")

# ---------- Parameter parsing ----------
def _split_params(s):
    s = s.strip()
    if not s:
        return []
    res = []
    cur = []
    in_q = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '"':
            in_q = not in_q
            i += 1
            continue
        if ch == ',' and not in_q:
            res.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    if cur:
        res.append("".join(cur).strip())
    out = []
    for p in res:
        if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            out.append(p[1:-1])
        else:
            out.append(p)
    return out

# ---------- AT parsing ----------
def parse_at_line(line):
    if not line:
        return None, None, None
    s = line.strip()
    if len(s) < 2 or s[:2].upper() != "AT":
        return None, None, None
    tail = s[2:].strip()
    if not tail:
        return "", [], False
    if tail.startswith("+"):
        tail = tail[1:].strip()
    if tail.endswith("?"):
        cmd = tail[:-1].strip().upper()
        return cmd, [], True
    if "=" in tail:
        left, right = tail.split("=", 1)
        cmd = left.strip().upper()
        params = _split_params(right)
        return cmd, params, False
    cmd = tail.split()[0].strip().upper()
    return cmd, [], False

# ---------- Registry ----------
_COMMANDS = {}
def at_command(name, help_text=""):
    def deco(fn):
        _COMMANDS[name.upper()] = (fn, help_text)
        return fn
    return deco

def unregister(name):
    _COMMANDS.pop(name.upper(), None)

# ---------- Input detection ----------
def has_input_stdin():
    if _uselect is None:
        return False
    try:
        if hasattr(_uselect, "poll"):
            p = _uselect.poll()
            p.register(sys.stdin, _uselect.POLLIN)
            ev = p.poll(0)
            try:
                p.unregister(sys.stdin)
            except Exception:
                pass
            return bool(ev)
        else:
            r, _, _ = _uselect.select([sys.stdin], [], [], 0)
            return bool(r)
    except Exception:
        return False

def read_line_stdin_blocking():
    try:
        raw = sys.stdin.readline()
        if raw is None:
            return ""
        return raw.rstrip("\r\n")
    except Exception:
        try:
            b = sys.stdin.buffer.readline()
            return b.decode().rstrip("\r\n")
        except Exception:
            return ""

# ---------- Dispatcher ----------
def _dispatch_at(cmd, params, is_query):
    if cmd == "":
        send_ok()
        return
    entry = _COMMANDS.get(cmd)
    if entry:
        handler, _help = entry
        try:
            ok, payload = handler(params, is_query)
        except Exception as e:
            send_err("EX:" + str(e))
            return
        if payload:
            send_line(payload)
        if ok:
            send_line("OK")
        else:
            send_line("ERROR")
        return
    send_err()

# ---------- Auto HELP ----------
@at_command("HELP", "Show this help")
def _help_cmd(params, is_query):
    lines = ["Available commands:"]
    lines.append("  AT - basic attention")
    for k in sorted(_COMMANDS.keys()):
        if k == "HELP":
            continue
        h = _COMMANDS[k][1] or ""
        lines.append("  AT+{} {}".format(k, h))
    return True, "\n".join(lines)

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

# ---------- process_line() for unittest ----------
def process_line(line: str) -> str:
    """Process a single input line and return CRLF-terminated string."""
    out = []

    def cap_send(s):
        out.append(str(s))

    old_send = send_line
    old_ok = send_ok
    old_err = send_err
    try:
        globals()['send_line'] = lambda s: cap_send(s)
        globals()['send_ok'] = lambda payload=None: (cap_send(payload) if payload else None) or cap_send("OK")
        globals()['send_err'] = lambda msg=None: cap_send("ERROR: " + str(msg) if msg else "ERROR")

        line = line.strip()
        if not line:
            return ""
        if line.upper().startswith("AT"):
            cmd, params, is_query = parse_at_line(line)
            if cmd is None:
                cap_send("ERROR")
            else:
                _dispatch_at(cmd, params, is_query)
        else:
            cap_send("DATA RX: " + line)

        return "\r\n".join(out)

    finally:
        globals()['send_line'] = old_send
        globals()['send_ok'] = old_ok
        globals()['send_err'] = old_err

# ---------- Main loop ----------
def run_loop(poll_interval=0.01, blocking_fallback_ok=True):
    send_line("Enigma Core is ready to accept inputs")
    while True:
        try:
            got = None
            if has_input_stdin():
                got = read_line_stdin_blocking()
            else:
                if _uselect is None and blocking_fallback_ok:
                    got = read_line_stdin_blocking()
            if got is not None and got != "":
                line = got.strip()
                if not line:
                    continue
                if line.upper().startswith("AT"):
                    cmd, params, is_query = parse_at_line(line)
                    if cmd is None:
                        send_err()
                    else:
                        _dispatch_at(cmd, params, is_query)
                else:
                    send_line("DATA RX: " + line)
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            if IS_BOARD:
                continue
            else:
                print("EXIT")
                break
        except Exception as e:
            try:
                send_line("LOOP ERROR: " + str(e))
            except Exception:
                pass

# ---------- If run as script ----------
if __name__ == "__main__":
    # Start the main loop (infinite on MCU, Ctrl-C allowed on desktop)
    run_loop()