{
  description = "A flake that provides tools needed to hack on replit-py";

  inputs.nixpkgs.url = "github:nixos/nixpkgs";

  outputs = { self, nixpkgs }: let
    mkPkgs = system: import nixpkgs {
      inherit system;
    };
    mkDevShell = system:
    let
      pkgs = mkPkgs system;
    in
    pkgs.mkShell {
      packages = [
        pkgs.python312
        pkgs.poetry
        pkgs.uv
      ];
    };
  in
  {
    devShells.aarch64-darwin.default = mkDevShell "aarch64-darwin";
    devShells.x86_64-linux.default = mkDevShell "x86_64-linux";
  };
}
