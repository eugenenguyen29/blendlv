# Trivesta Level

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/eugenenguyen29/blendlv?utm_source=oss&utm_medium=github&utm_campaign=eugenenguyen29%2Fblendlv&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

Three.js level design pipeline with Blender export tools.

## Overview

- **blender_extension/** - Blender add-on for exporting levels
- **level_tester/** - Three.js viewer for testing exported levels

## Setup

### Blender Extension

```bash
uv sync
```

### Level Tester

```bash
cd level_tester
pnpm install
pnpm run dev
```

## Development

```bash
# Linting
ruff check . --fix

# Type checking
ty check

# Tests
uv run pytest -x -v                      # Python unit tests
uv run python tests/e2e/find_blender.py  # E2E tests
cd level_tester && pnpm test             # TypeScript tests
```
