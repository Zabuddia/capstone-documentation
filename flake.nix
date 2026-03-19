{
  description = "Development shell for the Capstone MkDocs site";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          mkdocs
          mkdocs-material
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
          ];

          shellHook = ''
            echo "MkDocs dev shell ready. Run: mkdocs serve"
          '';
        };
      });
}
