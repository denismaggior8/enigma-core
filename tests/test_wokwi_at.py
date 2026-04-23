import subprocess
import time
import threading
import sys
import os

CIPHERTEXT = "QBHEWTDFEQITKUWFQUHLIQQGVYGRSDOHDCOBFMDHXSKOFPAODRSVBEREIQZVEDAXSHOHBIYMCIIZSKGNDLNFKFVLWWHZXZGQXWSSPWLSOQXEANCELJYJCETZTLSTTWMTOBW"
EXPECTED_PLAINTEXT = "KOMXBDMXUUUBOOTEYFXDXUUUAUSBILVUNYYZWOSECHSXUUUFLOTTXVVVUUURWODREISECHSVIERKKREMASKKMITUUVZWODREIFUVFYEWHSYUUUZWODREIFUNFZWOYUUFZWL"

wokwi_cmd = os.path.expanduser("~/bin/wokwi-cli")
p = subprocess.Popen([wokwi_cmd, "--interactive", "--timeout", "0", "."], 
                     stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

output_buffer = ""

def read_output(proc):
    global output_buffer
    while True:
        try:
            chunk = proc.stdout.read(1)
            if not chunk:
                break
            # We use a lock-free append since we're just searching strings
            try:
                char = chunk.decode("utf-8")
                output_buffer += char
                sys.stdout.write(char)
                sys.stdout.flush()
            except UnicodeDecodeError:
                pass
        except Exception:
            break

t = threading.Thread(target=read_output, args=(p,))
t.daemon = True
t.start()

def send_cmd(cmd):
    print(f"\n[HOST] Sending: {cmd}")
    p.stdin.write(f"{cmd}\r\n".encode("utf-8"))
    p.stdin.flush()
    time.sleep(0.5)

print("[HOST] Waiting for Wokwi Simulation to start...")
while "Starting simulation" not in output_buffer:
    time.sleep(0.5)

print("[HOST] Simulation started! Waiting 3 seconds for MicroPython boot...")
time.sleep(3)


# Force a clean state reset by switching model architectures
send_cmd("AT+ENIGMA=M3")
time.sleep(0.5)
send_cmd("AT+ENIGMA=M4")
time.sleep(0.5)

# Select the B-Reflector (Thin)
send_cmd("AT+REFLECTOR=BT")
time.sleep(0.5)

# Configure the 4 Rotors
send_cmd("AT+ROTOR=0,VIII,20,2")
time.sleep(0.5)
send_cmd("AT+ROTOR=1,III,2,6")
time.sleep(0.5)
send_cmd("AT+ROTOR=2,IV,0,12")
time.sleep(0.5)
send_cmd("AT+ROTOR=3,G,0,21")
time.sleep(0.5)

# Connect the Plugboard
plugs = ["C,H", "E,J", "N,V", "O,U", "T,Y", "L,G", "S,Z", "P,K", "D,I", "Q,B"]
for p_setting in plugs:
    send_cmd(f"AT+PLUGBOARD={p_setting}")
    time.sleep(0.2)

print("[HOST] Configuration applied successfully. Transmitting Ciphertext blocks...")

output_buffer = "" # Clear buffer before transmit

# Send ciphertext
for char in CIPHERTEXT:
    p.stdin.write(f"{char}\r\n".encode("utf-8"))
    p.stdin.flush()
    time.sleep(0.05)

print("[HOST] Waiting for simulation to finish processing...")
for _ in range(40):
    cleaned_output = "".join(output_buffer.replace("OK", "").replace("\r", "").replace("\n", "").split())
    if len(cleaned_output) >= len(EXPECTED_PLAINTEXT):
        break
    time.sleep(0.5)


if EXPECTED_PLAINTEXT in cleaned_output.upper():
    print(f"\n✅ VERIFIED: P1030700 decryption matches expected historical plaintext!")
else:
    print(f"\n❌ FAILED: Decryption mismatch.")
    print(f"EXPECTED: {EXPECTED_PLAINTEXT}")
    print(f"GOT: {cleaned_output}")
    p.terminate()
    sys.exit(1)

# Reset positions for reverse test
print("[HOST] Re-initializing rotor positions for reverse (encryption) verification...")
send_cmd("AT+ROTOR=0,VIII,20,2")
time.sleep(0.5)
send_cmd("AT+ROTOR=1,III,2,6")
time.sleep(0.5)
send_cmd("AT+ROTOR=2,IV,0,12")
time.sleep(0.5)
send_cmd("AT+ROTOR=3,G,0,21")
time.sleep(0.5)

output_buffer = "" # Clear buffer again

print("[HOST] Transmitting Plaintext blocks to verify encryption...")
for char in EXPECTED_PLAINTEXT:
    p.stdin.write(f"{char}\r\n".encode("utf-8"))
    p.stdin.flush()
    time.sleep(0.05)

print("[HOST] Waiting for simulation to finish processing...")
for _ in range(40):
    cleaned_reverse_output = "".join(output_buffer.replace("OK", "").replace("\r", "").replace("\n", "").split())
    if len(cleaned_reverse_output) >= len(CIPHERTEXT):
        break
    time.sleep(0.5)


if CIPHERTEXT in cleaned_reverse_output.upper():
    print(f"\n✅ VERIFIED: P1030700 encryption identically reproduces the historical ciphertext!")
else:
    print(f"\n❌ FAILED: Encryption mismatch.")
    print(f"EXPECTED: {CIPHERTEXT}")
    print(f"GOT: {cleaned_reverse_output}")
    p.terminate()
    sys.exit(1)

p.terminate()
print("[HOST] Wokwi Simulator Terminated Successfully.")
sys.exit(0)
