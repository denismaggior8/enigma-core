# main.py

import sys
import time

from device_state import DeviceState
from at_registry import _COMMANDS, at_command
import handlers  # triggers auto-import
from enigmapython.EnigmaM3 import EnigmaM3
from enigmapython.EnigmaM4 import EnigmaM4

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

# ---------- import AT handlers ----------
def load_handlers():
    import handlers

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
def _split_params(s: str):
    """
    Split comma-separated parameters, supporting bareword tokens (no quotes).
    Rejects spaces, quoted params and lowercase tokens (we require uppercase).
    e.g. '1,VI,0,0' -> ['1','VI','0','0']
    """
    if s is None:
        return []
    s = s.strip()
    if s == "":
        return []

    res = []
    cur = []
    in_quotes = False
    i = 0
    while i < len(s):
        ch = s[i]
        # reject spaces anywhere
        if ch == " ":
            raise ValueError("SPACES_NOT_ALLOWED")
        # disallow quotes entirely (option B)
        if ch == '"':
            raise ValueError("QUOTES_NOT_ALLOWED")
        if ch == ',' and not in_quotes:
            token = "".join(cur).strip()
            if token == "":
                # empty token not allowed
                raise ValueError("EMPTY_PARAM")
            res.append(token)
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    if cur:
        token = "".join(cur).strip()
        if token == "":
            raise ValueError("EMPTY_PARAM")
        res.append(token)

    # Validate uppercase and no surrounding quotes (quotes already rejected)
    for t in res:
        if t != t.upper():
            raise ValueError("LOWERCASE_NOT_ALLOWED")
    return res


# ---------- AT parsing ----------
def parse_at_line(line: str):
    """
    Returns (cmd, params_list, is_query)
    - requires commands uppercase and no spaces inside
    - supports:
        AT
        AT+CMD
        AT+CMD?
        AT+CMD=arg1,arg2,...         -> set
        AT+CMD=arg1,arg2?            -> query with args (e.g. AT+ROTOR=1?)
    - For other commands parser behavior is unchanged.
    """
    if not line:
        return None, None, None
    s = line.strip()
    if len(s) < 2 or s[:2].upper() != "AT":
        return None, None, None

    tail = s[2:].strip()
    if not tail:
        return "", [], False

    # must start with '+' for extended commands
    if tail.startswith("+"):
        body = tail[1:]
    else:
        # bare AT or invalid
        # if it's plain "AT" we handled earlier; otherwise treat as invalid
        if tail == "":
            return "", [], False
        # treat "ATFOO" as invalid
        return None, None, None

    # Reject spaces inside body (we require no spaces at all in command)
    if " " in body:
        return None, None, None

    # Case: contains '='
    if "=" in body:
        left, right = body.split("=", 1)
        left = left.strip().upper()
        right = right.strip()
        # Support query-with-equals e.g. AT+ROTOR=1?  -> right endswith '?'
        if right.endswith("?"):
            raw = right[:-1]
            # if raw is empty, treat as test syntax (not used here) -> return empty params and query True
            if raw == "":
                return left, [], True
            try:
                params = _split_params(raw)
            except ValueError:
                return left, None, None  # signal parse error
            return left, params, True
        else:
            # normal assignment
            try:
                params = _split_params(right)
            except ValueError:
                return left, None, None
            return left, params, False

    # No '=' present
    # Classic query: AT+CMD?
    if body.endswith("?"):
        cmd = body[:-1].strip().upper()
        return cmd, [], True

    # Bare command name
    cmd = body.strip().upper()
    return cmd, [], False

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
            cypher(line)
        
        return "\r\n".join(out)

    finally:
        globals()['send_line'] = old_send
        globals()['send_ok'] = old_ok
        globals()['send_err'] = old_err

# ---------- Main loop ----------
def run_loop(poll_interval=0.01, blocking_fallback_ok=True):
    load_handlers()
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
                    if not cypher(line):
                        continue
                    

                    
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

def cypher(line):
    state = DeviceState.get()
    enigma = state.enigma

    # if enigma is None
    if enigma is None or enigma.reflector is None or (isinstance(enigma,EnigmaM3) and len(enigma.rotors) < 3) or (isinstance(enigma,EnigmaM4) and len(enigma.rotors) < 4):
        send_line("ENIGMA NOT SET UP FOR DATA\r\nERROR")
        return False
    send_line(enigma.input_string(line))
    send_line("OK")
    return True

# ---------- If run as script ----------
if __name__ == "__main__":
    # Start the main loop (infinite on MCU, Ctrl-C allowed on desktop)
    run_loop()