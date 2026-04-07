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
          beautifulsoup4
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.chromium
            pkgs.nodejs
            pythonEnv
          ];

          shellHook = ''
            echo "MkDocs/PDF dev shell ready. Run: mkdocs serve or scripts/build_pdf.sh"
          '';
        };
      });
}
