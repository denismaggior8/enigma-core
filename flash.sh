export ESPPORT=/dev/tty.usbserial-0001 # Should be valid on Mac but double check to match yours
export MICROPYTHON_BIN=ESP32_GENERIC-20250911-v1.26.1.bin

# (Optionally) re-build the application
./build.sh

# Erase the board flash
python -m esptool --chip esp32 erase_flash    

# Upload MicroPython firmware
python -m esptool --baud 460800 write_flash 0x1000 $MICROPYTHON_BIN # Download the MicroPython binary from https://micropython.org/download/

# Upload Enigma Core (this may take a while)
echo "Transferring Enigma Core..."
cd dist                                                                                                                                  
find . -type d -exec ampy --port $ESPPORT mkdir {} \; 2>/dev/null
find . -type f -exec ampy --port $ESPPORT put {} {} \;
cd ..