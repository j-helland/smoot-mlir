{
  systems = [ "x86_64-linux" ];

  # Preserve the previous CI build selection.
  onlyBuild = [
    "checks.x86_64-linux.backend"
    "checks.x86_64-linux.frontend"
    # Only the backend is currently a reusable build artifact.
    "packages.x86_64-linux.backend"
  ];
}
