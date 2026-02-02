# Trivesta Level

Three.js level design pipeline with Blender export tools.

## MANDATORY: Quality Gate

**Run ALL before completing any task:**
```bash
ruff check . --fix && ruff check .      # Linting
ty check                                 # Types
uv run pytest -x -v                      # Unit tests
uv run python tests/e2e/find_blender.py # E2E tests
```
Zero tolerance. Fix pre-existing issues. No exceptions.

## Architecture

**READ before modifying, UPDATE when changing architecture:**

| Document | Scope |
|----------|-------|
| `.claude/architecture/blender-extension.md` | Extension structure |
| `.claude/architecture/blender-operators.md` | Export operators |
| `.claude/architecture/blender-panels.md` | UI panels |
| `.claude/architecture/blender-transforms.md` | Coordinate conversion |
| `.claude/architecture/blender-data-schemas.md` | JSON schemas & TypeScript types |

**If your changes affect component design, data flow, or APIs: update the relevant doc.**

## Key Paths

- `blender_extension/` - Add-on source
- `level_tester/` - Three.js test viewer
- `//exports/` - Export directory (relative to .blend)

## Commit Rules

**Keep code and tests together in the same commit:**

| Component | Test Location | Commit Together |
|-----------|---------------|-----------------|
| `blender_extension/` | `tests/` | Yes - always |
| `level_tester/` | `level_tester/**/*.test.*` | Yes - always |

Never separate implementation changes from their corresponding test changes.

## Context7 (REQUIRED for bpy code)

Query before writing/modifying any `bpy` code:
```
mcp__context7__query-docs(libraryId="/websites/blender_api_current", query="...")
```

## Development

```bash
uv sync          # deps
uv run script.py # run
ruff check .     # lint (nix flake)
ty check         # types (nix flake)
```

## Testing

**READ `.claude/skills/blender-testing.md` before writing tests.**

**Rules:**
1. Never `import bpy` in test files (conftest.py pre-mocks it)
2. Import module under test INSIDE test methods
3. Use fixtures: `mock_bpy_module`, `mock_context`, `mock_object`
4. Add mocks to `tests/mocks/`, never inline
