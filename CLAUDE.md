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

## Critical Gotchas

**Terrain coordinates are WORLD-SPACE:** Terrain GLBs contain absolute world positions. Do NOT apply `Island.world_position` as a transform to terrain's parent group - this causes double-transformation. See `.claude/architecture/blender-data-schemas.md` section "CRITICAL: Terrain Coordinate Rules".

## Code Style

**Write expressive code. Comments are a last resort.**

| Practice | Example |
|----------|---------|
| Name functions by what they do | `calculate_island_bounds()` not `process()` |
| Name variables by what they hold | `active_npcs` not `data` or `tmp` |
| Extract complex logic to named functions | `if is_within_spawn_radius()` not `if dist < r * 0.8` |
| Use type hints as documentation | `def load(path: Path) -> Manifest:` |

**Comments allowed only for:**
- Non-obvious business rules or domain knowledge
- Workarounds with linked issue/bug references
- Legal/license headers

**Never comment:**
- What the code does (make the code say it)
- Obvious operations
- Section dividers or TODOs

## Tree Shaking Rules

**Use `import.meta.env.DEV` to exclude dev-only code from production builds:**

```typescript
// ✅ Good - entire block eliminated in production
if (import.meta.env.DEV) {
  console.log('debug:', data);
  showCollisionBoxes();
}

// ✅ Good - dynamic import for larger dev modules
if (import.meta.env.DEV) {
  const { DevTools } = await import('./dev/DevTools');
  DevTools.init();
}

// ❌ Bad - dev code always bundled
console.log('debug:', data);
debugVisualize(mesh);
```

**Rules:**
1. Wrap all debug logs, dev UI, and diagnostic code in `if (import.meta.env.DEV)` blocks
2. Use dynamic imports for larger dev-only modules to ensure complete elimination
3. Never call dev functions outside of DEV guards

## Commit Rules

**Keep code and tests together in the same commit:**

| Component | Test Location | Commit Together |
|-----------|---------------|-----------------|
| `blender_extension/` | `tests/` | Yes - always |
| `level_tester/` | `level_tester/**/*.test.*` | Yes - always |

Never separate implementation changes from their corresponding test changes.

## Subagent Rules

**Use the correct subagent type - skills are auto-loaded via `skills` field in agent config:**

| Task Domain | Subagent Type | Auto-loaded Skills |
|-------------|---------------|-------------------|
| Three.js / React / R3F | `react-specialist` | `react`, `threejs-react`, `browser-defensive` |
| Browser TypeScript (UI, menus, storage) | `react-specialist` | `browser-defensive` |
| Blender tests | `python-pro` | `blender-testing` |

**Note:** Skills defined in `~/.claude/agents/<agent>.md` frontmatter are automatically injected into subagent context. No need to include "Read skill file first" in prompts.

**MCP tools (Context7) require foreground mode** - background subagents cannot use MCP.

## Agent Workflow (MANDATORY)

**All coding tasks MUST follow this workflow:**

1. **Delegate** - Spawn coding agents for implementation (never code directly)
2. **Review** - `code-reviewer` agent checks every completed task
3. **Verify** - All tests must pass before sign-off:
   - Unit tests: `uv run pytest -x -v` (Python) / `npm test` (TS)
   - E2E tests: `uv run python tests/e2e/find_blender.py`
4. **Iterate** - On test failure: spawn new agent to fix, repeat until green

**No exceptions. No partial completions. Green CI or iterate.**

## Context7 (REQUIRED)

**Query before writing/modifying code in these domains:**

| Domain | Library IDs |
|--------|-------------|
| Blender (`bpy`) | `/websites/blender_api_current` |
| React Three Fiber | `/pmndrs/react-three-fiber` |
| Drei helpers | `/pmndrs/drei` |
| Three.js core | `/mrdoob/three.js` |

```
mcp__context7__query-docs(libraryId="...", query="...")
```

## Development

```bash
uv sync          # deps
uv run script.py # run
ruff check .     # lint (nix flake)
ty check         # types (nix flake)
```

## Testing

**READ `.claude/skills/blender-testing/SKILL.md` before writing tests.**

**Rules:**
1. Never `import bpy` in test files (conftest.py pre-mocks it)
2. Import module under test INSIDE test methods
3. Use fixtures: `mock_bpy_module`, `mock_context`, `mock_object`
4. Add mocks to `tests/mocks/`, never inline
