{
  pkgs,
  src,
}:
let
  lib = pkgs.lib;
  miseLock = builtins.fromTOML (builtins.readFile "${src}/mise.lock");

  # mise.lock keys each tool's release assets by mise's own platform names.
  misePlatform =
    {
      aarch64-darwin = "macos-arm64";
      # The musl builds are statically linked, so they run in the Nix sandbox
      # without patching the ELF interpreter.
      x86_64-linux = "linux-x64-musl";
    }
    .${pkgs.stdenv.hostPlatform.system};

  # Fetch the exact release binary mise pins, so lint checks match local runs.
  fetchMiseTool =
    name:
    let
      lock = lib.head miseLock.tools.${name};
      asset = lock."platforms.${misePlatform}";
    in
    pkgs.stdenvNoCC.mkDerivation {
      pname = name;
      inherit (lock) version;
      src = pkgs.fetchurl {
        inherit (asset) url;
        sha256 = lib.removePrefix "sha256:" asset.checksum;
      };
      sourceRoot = ".";
      installPhase = ''
        install -Dm755 */${name} "$out/bin/${name}"
      '';
    };
in
{
  ruff = fetchMiseTool "ruff";
  ty = fetchMiseTool "ty";
}
