# Trivesta Level

Three.js level design pipeline with Blender export tools.

## MANDATORY: Code Quality Gate (Agents & Subagents)

**ALL agents and subagents MUST ensure the following pass before completing ANY task:**

```bash
ruff check .                           # Linting - MUST be clean
ty check                               # Type checking - MUST be clean
uv run pytest                          # Unit tests - ALL must pass
uv run python tests/e2e/find_blender.py  # E2E tests - ALL must pass
```

### Rules

1. **Zero tolerance for errors** - No linting errors, type errors, or failing tests
2. **Fix pre-existing issues** - If you encounter errors that existed before your changes, YOU MUST FIX THEM before completing the task
3. **No exceptions** - Do not mark a task complete, sign off, or report success if any check fails
4. **Run all checks** - Always run the full verification suite, not just checks on modified files

### Verification Workflow

Before completing any task:
```bash
# 1. Linting (fix any issues)
ruff check . --fix
ruff check .

# 2. Type checking (fix any issues)
ty check

# 3. Unit tests (fix any failures)
uv run pytest -x -v

# 4. E2E tests (fix any failures)
uv run python tests/e2e/find_blender.py
```

**If ANY check fails, the task is NOT complete. Fix all issues first.**

---

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

Two-tier strategy:
- **Unit tests**: `uv run pytest` (mocked bpy, fast)
- **E2E tests**: Real Blender process (requires Blender installed)

```bash
uv run pytest              # all unit tests
uv run pytest -x -v        # stop on fail, verbose
```

### E2E Tests (IMPORTANT for subagents)

**ALWAYS use the helper script** to run E2E tests - it automatically finds Blender:

```bash
# Recommended: Uses find_blender.py to locate Blender automatically
uv run python tests/e2e/find_blender.py

# Alternative if BLENDER_EXE is set:
$BLENDER_EXE --background --factory-startup --python tests/e2e/__init__.py
```

The helper script searches for Blender in:
1. `BLENDER_EXE` environment variable
2. Common installation paths (snap, flatpak, system packages)
3. System PATH

If Blender is not found, it prints helpful installation instructions.

### STRICT Testing Rules

1. you **MUST** read @.claude/skills/blender-testing.md
2. **NEVER `import bpy`** in test files - conftest.py pre-mocks it via `pytest_configure`
3. **Import module under test INSIDE test methods**, not at module level
4. **Use fixtures**: `mock_bpy_module`, `mock_context`, `mock_object`
5. **NEVER define operators/panels in test files** - import from `blender_extension/`
6. Add new mocks to `tests/mocks/`, never inline

### Test Template

```python
"""Tests for operator_name."""
from unittest.mock import MagicMock

class TestOperatorName:
    def test_execute_success(self, mock_bpy_module: MagicMock) -> None:
        # Import INSIDE the test method
        from blender_extension.operators.module import NAMESPACE_OT_op

        mock_ctx = MagicMock()
        mock_ctx.object = MagicMock()

        op = NAMESPACE_OT_op()
        assert op.execute(mock_ctx) == {"FINISHED"}

    def test_poll_no_object(self, mock_bpy_module: MagicMock) -> None:
        from blender_extension.operators.module import NAMESPACE_OT_op

        mock_ctx = MagicMock()
        mock_ctx.object = None
        assert NAMESPACE_OT_op.poll(mock_ctx) is False
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
