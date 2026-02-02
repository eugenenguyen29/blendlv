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

            # Node.js for level_tester
            nodejs_24
            nodePackages.pnpm

            # TypeScript/JS LSP and linting daemons
            vtsls
            eslint_d
            prettierd
          ];

          # BLENDER_EXE: Environment variable for E2E tests
          # E2E tests use this to locate Blender: $BLENDER_EXE --background --python tests/e2e/__init__.py
          # Falls back to "blender" if not found in PATH (tests will fail gracefully)
          shellHook = ''
            export BLENDER_EXE=$(which blender 2>/dev/null || echo "blender")

            echo "Trivesta Level dev environment"
            echo "  - uv: $(uv --version)"
            echo "  - node: $(node --version)"

            # Inform user about Blender configuration
            if command -v blender &>/dev/null; then
              echo "  - blender: $(blender --version 2>/dev/null | head -1)"
              echo "  - BLENDER_EXE: $BLENDER_EXE"
            else
              echo "  - blender: not found in PATH"
              echo "  Warning: Blender not found. E2E tests require Blender."
              echo "  Set BLENDER_EXE manually or install Blender to run E2E tests."
            fi
          '';
        };
      }
    );
}
