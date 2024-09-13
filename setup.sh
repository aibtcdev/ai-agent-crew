#!/bin/bash

# set up environment
CLARINET_INSTALL_DIR="$HOME/.local/bin"
CLARINET_DEPS_DIR="./clarinet-deps/glibc-2.34"
CLARINET_CONFIG_FILE="./clarinet-deps/clarinet-config"
mkdir -p "$CLARINET_INSTALL_DIR"

# download and extract clarinet 2.8.0
curl -L -o "clarinet.tar.gz" "https://github.com/hirosystems/clarinet/releases/download/v2.8.0/clarinet-linux-x64-glibc.tar.gz"
tar -xzf "clarinet.tar.gz" -C "$CLARINET_INSTALL_DIR"
rm "clarinet.tar.gz"
chmod +x "$CLARINET_INSTALL_DIR/clarinet"
echo "Clarinet installed to $CLARINET_INSTALL_DIR/clarinet"

# patch clarinet to use glibc 2.34
# replit defaults to the newer 2.39
# this is a workaround to use the older version
patchelf --set-interpreter "$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" "$CLARINET_INSTALL_DIR/clarinet"
patchelf --set-rpath "$CLARINET_DEPS_DIR" "$CLARINET_INSTALL_DIR/clarinet"
echo "Clarinet patched to use custom GLIBC"

# source the configuration file
source "$CLARINET_CONFIG_FILE"

# print debug information
echo "1. Custom GLIBC version for Clarinet:"
"$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" --version
echo "2. Clarinet binary information:"
file "$CLARINET_INSTALL_DIR/clarinet"
echo "3. Clarinet library dependencies:"
LD_LIBRARY_PATH="$CLARINET_DEPS_DIR:/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH" ldd "$CLARINET_INSTALL_DIR/clarinet"
echo "4. Attempting to run Clarinet:"
clarinet_env --version
echo "5. Usage:"
echo "source $CLARINET_CONFIG_FILE && clarinet --version"
