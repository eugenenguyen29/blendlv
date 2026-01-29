{
  description = "Trivesta Level - Blender to Three.js level design pipeline";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Python tooling
            uv
            python314
            ruff
            ty

            # Node.js for viewer (when needed)
            nodejs_22
            nodePackages.pnpm
          ];

          shellHook = ''
            echo "Trivesta Level dev environment"
            echo "  - uv: $(uv --version)"
            echo "  - node: $(node --version)"
            echo "  - blender: $(blender --version | head -1)"
          '';
        };
      }
    );
}
