#!/bin/bash

# set up environment
CLARINET_SETUP_DIR="$HOME/ai-agent-crew/clarinet-deps"
CLARINET_BIN_DIR="$CLARINET_DIR/bin"
CLARINET_DEPS_DIR="$CLARINET_DIR/glibc-2.34"
CLARINET_CONFIG_FILE="$CLARINET_DIR/clarinet-config"

# create directories
mkdir -p "$CLARINET_SETUP_DIR"
mkdir -p "$CLARINET_BIN_DIR"
mkdir -p "$CLARINET_DEPS_DIR"

# download and extract clarinet 2.8.0
curl -L -o "clarinet.tar.gz" "https://github.com/hirosystems/clarinet/releases/download/v2.8.0/clarinet-linux-x64-glibc.tar.gz"
tar -xzf "clarinet.tar.gz" -C "$CLARINET_BIN_DIR"
rm "clarinet.tar.gz"
chmod +x "$CLARINET_BIN_DIR/clarinet"
echo "Clarinet installed to $CLARINET_BIN_DIR/clarinet"

# patch clarinet to use glibc 2.34
# replit defaults to the newer 2.39
# this is a workaround to use the older version
patchelf --set-interpreter "$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" "$CLARINET_BIN_DIR/clarinet"
patchelf --set-rpath "$CLARINET_DEPS_DIR" "$CLARINET_BIN_DIR/clarinet"
echo "Clarinet patched to use custom GLIBC 2.34"

# source the configuration file
source "$CLARINET_CONFIG_FILE"

# print debug information
echo "1: Custom paths set by script:"
echo "  CLARINET_SETUP_DIR=$CLARINET_SETUP_DIR"
echo "  CLARINET_BIN_DIR=$CLARINET_BIN_DIR"
echo "  CLARINET_DEPS_DIR=$CLARINET_DEPS_DIR"
echo "  CLARINET_CONFIG_FILE=$CLARINET_CONFIG_FILE"
echo "2. Custom GLIBC version for Clarinet:"
"$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" --version
echo "3. Clarinet binary information:"
file "$CLARINET_BIN_DIR/clarinet"
echo "4. Clarinet library dependencies:"
LD_LIBRARY_PATH="$CLARINET_DEPS_DIR:/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH" ldd "$CLARINET_BIN_DIR/clarinet"
echo "5. Attempting to run Clarinet:"
clarinet --version
echo "6. Usage:"
echo "source $CLARINET_CONFIG_FILE && clarinet --version"
