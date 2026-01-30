# Trivesta Level

Three.js level design pipeline with Blender export tools.

## Architecture Docs

Reference `.claude/architecture/` for component context:

- `blender-extension.md` - Extension overview & structure
- `blender-operators.md` - Export operators (GLB, manifest)
- `blender-panels.md` - UI panels
- `blender-transforms.md` - Coordinate conversion utilities
- `blender-data-schemas.md` - JSON schemas & TypeScript types
- `reference-coastalworld.md` - CoastalWorld pipeline patterns (inspiration)

## Key Paths

- `blender_extension/` - Blender add-on source
- Exports to `//exports/` (relative to .blend file)

## Reference

- https://docs.blender.org/api/current/info_quickstart.html - when implement with bpy for API contract correctness and follow best practice.

## Context7 API Lookup (REQUIRED)

**ALWAYS** use Context7 MCP to verify Blender API usage before implementing:

```
Library ID: /websites/blender_api_current
```

Before writing or modifying any `bpy` code:
1. Query Context7 with the specific API you're using (e.g., "AssetShelf properties", "Operator bl_options")
2. Verify class attributes, method signatures, and available options
3. Check for version-specific features or deprecations

Example workflow:
```
# First: resolve-library-id if unsure of the library
# Then: query-docs with specific question
mcp__context7__query-docs(
  libraryId="/websites/blender_api_current",
  query="AssetShelf bl_default_show_names property"
)
```

This prevents incorrect API usage and ensures compatibility with current Blender versions.


## Development

Use `uv` exclusively for Python (no pip/poetry):
```bash
uv sync          # install deps
uv run script.py # run scripts
```

## Testing

Write tests in `tests/` directory, not in implementation files.

```bash
uv run pytest              # run all tests
uv run pytest tests/       # run specific directory
uv run pytest -v           # verbose output
uv run pytest -x           # stop on first failure
```

Example test structure:
```
tests/
  test_transforms.py      # tests for utils/transforms.py
  test_collections.py     # tests for utils/collections.py
```

## Linting & Type Checking

**Note**: `ruff` and `ty` are provided by the nix flake. Use them directly (not via `uv run`).

```bash
ruff check .        # check all files
ruff check --fix .  # auto-fix issues
ty check            # type checking
```

## Code Verification Rules

- **DO NOT** use `python3 -m py_compile` for syntax/type checking
- **ALWAYS** use `ruff check` for linting and code verification (provided by nix flake)
- **Use `ty check`** for type checking (Astral's fast type checker, provided by nix flake)

```bash
ruff check .   # linting
ty check       # type checking
```
