{ pkgs ? import <nixpkgs> {} }:

let
  pythonPackages = pkgs.python3Packages;
in pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    pythonPackages.pip
    pythonPackages.virtualenv
    gcc
    stdenv.cc.cc.lib
    zlib
    glib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH
    export PYTHONPATH=${pythonPackages.numpy}/${pythonPackages.python.sitePackages}:$PYTHONPATH

    # Create a .venv virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
      python -m venv .venv
    fi
    
    # Activate the virtual environment
    source .venv/bin/activate

    # Modify PATH to prioritize the virtual environment
    export PATH="$PWD/.venv/bin:$PATH"

    # Install project dependencies (if you have a requirements.txt file)
    # pip install -r requirements.txt

    echo "Python environment ready!"
    echo "Python interpreter: $(which python)"
  '';
}