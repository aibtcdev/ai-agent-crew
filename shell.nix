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
     '';
   }
   