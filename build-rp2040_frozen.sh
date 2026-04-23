#!/bin/bash
set -e

# --- Configuration ---
MICROPYTHON_VERSION="v1.26.1"
ENIGMA_PYTHON_VERSION="3.1.2"
VERSION=""
BOARD="RPI_PICO"

WORKSPACE_DIR=$(pwd)
BUILD_DIR="${WORKSPACE_DIR}/.build"
TOOLS_DIR="${BUILD_DIR}/tools"

# Toolchain URLs (macOS ARM64 Apple Silicon)
CMAKE_URL="https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3-macos-universal.tar.gz"
ARM_GCC_URL="https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz"

echo "=========================================================="
echo " Building Custom RP2040-Zero MicroPython Image"
echo " MicroPython Version: ${MICROPYTHON_VERSION} (Wait, ignoring ESP32_GENERIC prefix as it's an RP2040 build)"
echo " Board: ${BOARD}"
echo "=========================================================="

mkdir -p "${TOOLS_DIR}"

# --- 1. Fetch CMake ---
CMAKE_BIN=$(find "${TOOLS_DIR}" -type f -path "*/CMake.app/Contents/bin/cmake" | head -n 1)
if [[ -z "$CMAKE_BIN" && ! -x "$(command -v cmake)" ]]; then
    echo "Downloading CMake..."
    curl -L "${CMAKE_URL}" -o "${TOOLS_DIR}/cmake.tar.gz"
    tar -xzf "${TOOLS_DIR}/cmake.tar.gz" -C "${TOOLS_DIR}"
    CMAKE_BIN=$(find "${TOOLS_DIR}" -type f -path "*/CMake.app/Contents/bin/cmake" | head -n 1)
fi
if [[ -n "$CMAKE_BIN" ]]; then
    export PATH="$(dirname "${CMAKE_BIN}"):$PATH"
fi

# --- 2. Fetch ARM GNU Toolchain ---
GCC_BIN=$(find "${TOOLS_DIR}" -type f -path "*/bin/arm-none-eabi-gcc" | head -n 1)
if [[ -z "$GCC_BIN" && ! -x "$(command -v arm-none-eabi-gcc)" ]]; then
    echo "Downloading ARM GCC Toolchain..."
    curl -L "${ARM_GCC_URL}" -o "${TOOLS_DIR}/arm-gcc.tar.xz"
    tar -xf "${TOOLS_DIR}/arm-gcc.tar.xz" -C "${TOOLS_DIR}"
    GCC_BIN=$(find "${TOOLS_DIR}" -type f -path "*/bin/arm-none-eabi-gcc" | head -n 1)
fi
if [[ -n "$GCC_BIN" ]]; then
    export PATH="$(dirname "${GCC_BIN}"):$PATH"
fi

# Verify Toolchains
cmake --version | head -n 1
arm-none-eabi-gcc --version | head -n 1

# --- 3. Prep Source Code ---
echo "Cloning MicroPython (${MICROPYTHON_VERSION}) and dependencies..."
cd "${BUILD_DIR}"

if [ ! -d "micropython" ]; then
    git clone https://github.com/micropython/micropython.git
fi
cd micropython
git fetch origin
# Make sure to handle if v1.26.1 tag doesn't exist, fallback to master
if git rev-parse "${MICROPYTHON_VERSION}" >/dev/null 2>&1; then
    git checkout tags/${MICROPYTHON_VERSION}
else
    echo "WARNING: Tag ${MICROPYTHON_VERSION} not found. Attempting to use master."
    git checkout master
fi

cd "${BUILD_DIR}"
if [ ! -d "enigma-python" ]; then
    git clone https://github.com/denismaggior8/enigma-python.git
fi
cd enigma-python
git checkout "tags/v${ENIGMA_PYTHON_VERSION}" || git checkout "tags/${ENIGMA_PYTHON_VERSION}" || git checkout master
cd ..

# --- 4. Prepare Custom Manifest ---

# Avoid hyphen bugs in MicroPython freeze variable generation by copying to a safe path
rm -rf "${BUILD_DIR}/safe_freeze"
mkdir -p "${BUILD_DIR}/safe_freeze"
cp -r "${WORKSPACE_DIR}/src" "${BUILD_DIR}/safe_freeze/local_src"
cp -r "${BUILD_DIR}/enigma-python/src/enigma/enigmapython" "${BUILD_DIR}/safe_freeze/enigmapython"

MANIFEST_PATH="${BUILD_DIR}/manifest_enigma.py"
cat <<EOF > "${MANIFEST_PATH}"
# Include standard RP2040 boards manifest
include("\$(PORT_DIR)/boards/manifest.py")

# Require micropython-lib standard implementations
require("copy")
require("logging")

# Freeze user modules directly from source
freeze("${BUILD_DIR}/safe_freeze/local_src")
freeze("${BUILD_DIR}/safe_freeze", "enigmapython")
EOF

echo "Custom Manifest Prepared at ${MANIFEST_PATH}"

# --- 5. Compile ---
echo "Building mpy-cross..."
cd "${BUILD_DIR}/micropython"
make -C mpy-cross -j4 CFLAGS_EXTRA="-Wno-error"

echo "Building RP2040 Firmware for ${BOARD}..."
cd ports/rp2
make submodules
rm -rf "build-${BOARD}"
make BOARD=${BOARD} FROZEN_MANIFEST="${MANIFEST_PATH}" -j4

# --- 6. Extract Artifacts ---
echo "Extracting final firmware images..."

if [ -n "$VERSION" ]; then
    OUT_PREFIX="enigma-core_firmware_v${VERSION}_${BOARD}"
else
    OUT_PREFIX="enigma-core_firmware_${BOARD}"
fi

cp "build-${BOARD}/firmware.bin" "${WORKSPACE_DIR}/${OUT_PREFIX}.bin"
cp "build-${BOARD}/firmware.uf2" "${WORKSPACE_DIR}/${OUT_PREFIX}.uf2"

echo "Done! check ${OUT_PREFIX}.bin and ${OUT_PREFIX}.uf2 in your project root."

