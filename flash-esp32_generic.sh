export ESPPORT=/dev/tty.usbserial-0001 # Should be valid on Mac but double check to match yours
export MICROPYTHON_BIN=ESP32_GENERIC-20250911-v1.26.1.bin

# (Optionally) re-build the application
./build.sh

# Erase the board flash
python -m esptool --chip esp32 --baud 9600 --port $ESPPORT erase-flash    

# Upload MicroPython firmware
python -m esptool --baud 460800 --port $ESPPORT write-flash 0x1000 $MICROPYTHON_BIN # Download the MicroPython binary from https://micropython.org/download/

# Wait for reset to be completed
sleep 10

./copy.sh