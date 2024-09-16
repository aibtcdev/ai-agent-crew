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
    echo "Error: Could not find project root directory" >&2
    return 1
}

# find the project root
PROJECT_ROOT=$(find_project_root)
if [ $? -ne 0 ]; then
    exit 1
fi

# set up environment
CLARINET_SETUP_DIR="$PROJECT_ROOT/clarinet"
CLARINET_BIN_DIR="$CLARINET_SETUP_DIR/bin"
CLARINET_DEPS_DIR="$CLARINET_SETUP_DIR/glibc-2.34"
CLARINET_CONFIG_FILE="$CLARINET_SETUP_DIR/clarinet-config"

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
if command -v patchelf >/dev/null 2>&1; then
    echo "Patching Clarinet to use custom GLIBC 2.34..."
    patchelf --set-interpreter "$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" "$CLARINET_BIN_DIR/clarinet"
    patchelf --set-rpath "$CLARINET_DEPS_DIR" "$CLARINET_BIN_DIR/clarinet"
    echo "Clarinet patched to use custom GLIBC 2.34"
else
    echo "patchelf not found. Skipping Clarinet patching."
fi

# create configuration file
cat > "$CLARINET_CONFIG_FILE" << EOL
#!/bin/bash
export CLARINET_SETUP_DIR="$CLARINET_SETUP_DIR"
export CLARINET_BIN_DIR="$CLARINET_BIN_DIR"
export CLARINET_DEPS_DIR="$CLARINET_DEPS_DIR"
export LD_LIBRARY_PATH="$CLARINET_DEPS_DIR:/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH"
export PATH="$CLARINET_BIN_DIR:\$PATH"
EOL
echo "Configuration file created at $CLARINET_CONFIG_FILE"

# create a run script
cat > "$CLARINET_SETUP_DIR/run-clarinet.sh" << EOL
#!/bin/bash
source "$CLARINET_CONFIG_FILE"
clarinet "\$@"
EOL
chmod +x "$CLARINET_SETUP_DIR/run-clarinet.sh"
echo "Run script created at $CLARINET_SETUP_DIR/run-clarinet.sh"

# uncomment to print debug information
#echo "1: Custom paths set by script:"
#echo "  CLARINET_SETUP_DIR=$CLARINET_SETUP_DIR"
#echo "  CLARINET_BIN_DIR=$CLARINET_BIN_DIR"
#echo "  CLARINET_DEPS_DIR=$CLARINET_DEPS_DIR"
#echo "  CLARINET_CONFIG_FILE=$CLARINET_CONFIG_FILE"
#echo "2. Custom GLIBC version for Clarinet:"
#"$CLARINET_DEPS_DIR/ld-linux-x86-64.so.2" --version
#echo "3. Clarinet binary information:"
#file "$CLARINET_BIN_DIR/clarinet"
#echo "4. Clarinet library dependencies:"
#LD_LIBRARY_PATH="$CLARINET_DEPS_DIR:/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH" ldd "$CLARINET_BIN_DIR/clarinet"
#echo "5. Attempting to run Clarinet:"
#clarinet --version
#echo "6. Usage:"
#echo "source $CLARINET_CONFIG_FILE && clarinet --version"

echo "Clarinet setup complete!"
echo "To use Clarinet, run: source $CLARINET_CONFIG_FILE && clarinet [command]"
echo "Or use the run script: $CLARINET_SETUP_DIR/run-clarinet.sh [command]"