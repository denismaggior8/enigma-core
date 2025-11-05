# Enigma Core

**Enigma Core** is a standalone, embedded-ready AT command framework written in pure Python / MicroPython.  
It is designed to run both on desktop (CPython) and on microcontrollers such as ESP32 and RP2040, with identical behavior.

Its primary purpose is to host a fully configurable Enigma machine emulator on low-resource devices.

## ✨ Features

- 🧠 **Write once, run everywhere**  
  Same code runs on macOS/Linux (Python 3.x) and on ESP32/RP2040 (MicroPython)

- 🔌 **AT command interface**  
  Send commands via USB serial / UART like classic modem firmware

- 🧩 **Handler-based architecture**  
  Commands are implemented as standalone modules inside `handlers/`

- 🚀 **Unit-test friendly**  
  Full input/output logic can be tested using `process_line()` (no serial required)

- ♻️ **Runtime-loaded handlers**  
  Just drop a new `.py` file in `handlers/` and it becomes a new AT command

- 🔒 **Device state singleton**  
  Centralized in-memory state, resettable for tests

- 🧹 **Automatic memory cleanup**  
  Optional GC hook after state changes (for low-RAM boards)


## 📦 Repository Structure

```
enigma-core/
│
├── main.py             # Main entrypoint (loop, AT parsing, dispatcher)
├── at_registry.py      # @at_command decorator + registry
├── device_state.py     # DeviceState singleton
│
├── handlers/           # AT command implementations
│   ├── system.py
│   ├── led.py
|   ...
│   └── enigma.py       # (work in progress)
│
├── tests/              # Unittests (run under CPython)
│   ├── test_help.py
|   ...
│   └── test_enigma.py
│
└── README.md
```

## 🛠️ Running on PC (CPython)

```bash
$ echo "AT+HELP" | python3 main.py
```

Expected output:

```
Enigma Core is ready to accept inputs
Available commands:
  AT - basic attention
  AT+ENIGMA - Set/Get the Enigma machine model: AT+ENIGMA=M3|M4  AT+ENIGMA?
  AT+HELP - Show this help
  ...
OK
```

Press CTRL-C to exit.