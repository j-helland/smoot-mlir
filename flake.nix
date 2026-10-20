{
  description = "MLIR units demo dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    rust-overlay.inputs.nixpkgs.follows = "nixpkgs";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      rust-overlay,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
    }:
    let
      lib = nixpkgs.lib;
      systems = [
        "aarch64-darwin"
        "x86_64-linux"
      ];

      forAllSystems = lib.genAttrs systems;

      mkSystemOutputs =
        system:
        import ./nix {
          src = self.outPath;
          inherit pyproject-nix uv2nix pyproject-build-systems;
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ (import rust-overlay) ];
          };
        };

      perSystem = forAllSystems mkSystemOutputs;
    in
    {
      packages = lib.mapAttrs (_system: outputs: outputs.packages) perSystem;
      checks = lib.mapAttrs (_system: outputs: outputs.checks) perSystem;
      devShells = lib.mapAttrs (_system: outputs: outputs.devShells) perSystem;
    };
}
