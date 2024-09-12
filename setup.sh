# download and install clarinet
if ! command -v clarinet &> /dev/null
then
    echo "Clarinet not found. Downloading and installing..."
    # download and install clarinet
    wget -nv https://github.com/hirosystems/clarinet/releases/download/v2.8.0/clarinet-linux-x64-glibc.tar.gz -O clarinet-linux-x64.tar.gz
    tar -xf clarinet-linux-x64.tar.gz
    chmod +x ./clarinet
    sudo mv ./clarinet /usr/local/bin
    echo "Clarinet installed successfully."
else
    echo "Clarinet is already installed."
fi

# initalize submodule
git submodule update --init
cd agent-tools-ts
npm install
cd ..