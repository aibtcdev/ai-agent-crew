#!/bin/bash

set -e

# helper to find the project root
# so this works locally and on replit
find_project_root() {
    local current_dir
    current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    while [ "$current_dir" != "/" ]; do
        if [ -d "$current_dir/ai-agent-crew" ]; then
            echo "$current_dir/ai-agent-crew"
            return 0
        elif [ -d "$current_dir/aibtc-v1" ]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done
    return 1
}

# guessing the project root
echo "Guessing the project root a different way..."
echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# find the project root
PROJECT_ROOT=$(find_project_root)
if [ $? -ne 0 ]; then
    echo "Error: Could not find project root directory" >&2
    exit 1
fi
echo "Project root found at $PROJECT_ROOT"

# set up environment
CLARINET_SETUP_DIR="$PROJECT_ROOT/clarinet"
CLARINET_BIN_DIR="$CLARINET_SETUP_DIR/bin"
CLARINET_DEPS_DIR="$CLARINET_SETUP_DIR/glibc-2.34"
CLARINET_CONFIG_FILE="$CLARINET_SETUP_DIR/clarinet-config"

# create directories
mkdir -p "$CLARINET_SETUP_DIR"
mkdir -p "$CLARINET_BIN_DIR"
mkdir -p "$CLARINET_DEPS_DIR"

# download and extract clarinet 2.9.0
curl -L -o "clarinet.tar.gz" "https://github.com/hirosystems/clarinet/releases/download/v2.9.0/clarinet-linux-x64-glibc.tar.gz"
tar -xzf "clarinet.tar.gz" -C "$CLARINET_BIN_DIR"
rm "clarinet.tar.gz"
chmod +x "$CLARINET_BIN_DIR/clarinet"
echo "Clarinet installed to $CLARINET_BIN_DIR/clarinet"

# check if REPL_ID env var is set
if [ -z "$REPL_ID" ]; then
    echo "REPL_ID environment variable not set. Skipping Clarinet patching."
    exit 0
fi

# patch clarinet to use glibc 2.34
# replit defaults to the newer 2.39
# this is a workaround to use the older version
if command -v patchelf >/dev/null 2>&1; then
    echo "Patching Clarinet to use custom GLIBC 2.34..."
    patchelf --set-interpreter "$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" "$CLARINET_BIN_DIR/clarinet"
    patchelf --set-rpath "$CLARINET_DEPS_DIR" "$CLARINET_BIN_DIR/clarinet"
    echo "Clarinet patched to use custom GLIBC 2.34"
else
    echo "patchelf not found. Skipping Clarinet patching."
fi
