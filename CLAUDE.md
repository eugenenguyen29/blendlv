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

## Linting

```bash
uv run ruff check .        # check all files
uv run ruff check --fix .  # auto-fix issues
```
