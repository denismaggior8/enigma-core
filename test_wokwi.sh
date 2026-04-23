#!/bin/bash

# Ensure we have the compiled UF2 file
UF2_FILE=$(ls *firmware*RPI_PICO.uf2 2>/dev/null | head -n 1)
if [ -z "$UF2_FILE" ]; then
    echo "Error: Compiled firmware UF2 not found!"
    echo "Please run ./build-rp2040_frozen.sh first to generate the image."
    exit 1
fi

# Update wokwi.toml with the detected firmware
sed -i '' "s/firmware = .*/firmware = '${UF2_FILE}'/" wokwi.toml


echo "=========================================================="
echo " Starting Wokwi RP2040 Terminal Emulator                  "
echo "=========================================================="

if [ -z "${WOKWI_CLI_TOKEN}" ]; then
    echo ""
    echo "[!] Authentication Required"
    echo "Wokwi-CLI requires a free personal access token to stream the simulation to your terminal."
    echo ""
    echo "1. Get your token instantly at: https://wokwi.com/dashboard/ci"
    echo "2. Rerun this script by pasting your token like this:"
    echo "   WOKWI_CLI_TOKEN=\"your_token_here\" ./test_wokwi.sh   "
    echo ""
    echo "(Or simply install the Wokwi Extension in VS Code to run it 100% offline!)"
    echo "=========================================================="
    exit 1
fi

echo "Booting Raspberry Pi Pico..."
python3 tests/test_wokwi_at.py
