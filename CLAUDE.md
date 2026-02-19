# CLAUDE.md — swolfpy-dynamic-WtV

This file is the central orchestration document for Claude Code working on this project.
Read it fully before taking any action.

---

## Project Overview

**swolfpy** (Solid Waste Optimization Life-cycle Framework in Python) is an open-source
Python LCA engine for municipal and industrial solid waste management. It uses
[Brightway2](https://brightway.dev) as the underlying LCA computation backend and exposes
process-based models for waste collection, sorting, treatment (gasification, anaerobic
digestion, pyrolysis, landfill, WTE), and disposal.

This fork (`swolfpy-dynamic-WtV`) extends the upstream with:
- **Waste-to-Value (WtV)** process models
- **Dynamic LCA** via Temporalis (time-explicit carbon accounting)
- **Prospective LCA** via Premise (IAM-backed future climate scenarios)
- **Dual-native product layer** following the Yapplify architecture (human web UI + MCP agent interface)

**Lab context:** WENDY.LAB — applied AI in engineering sustainability / carbon intelligence.

---

## Target Architecture

```
yapplify.config.ts
    ├── Human Layer    →  Next.js web app (scenario builder, GWP dashboard, MC plots)
    ├── Agent Layer    →  MCP Server (SSE/HTTP, ChatGPT Developer Mode compatible)
    ├── Data Layer     →  PostgreSQL + Prisma (feedstock, process, impact, scenario, job)
    └── Context Optimizer → swolfpy DataFrame outputs → LLM-optimized markdown

swolfpy Python package (this repo)
    ├── swolfpy/           — existing LCA engine (Brightway2-backed)
    ├── swolfpy/dynamic_lca.py      — NEW: Temporalis dynamic LCA module
    ├── swolfpy/prospective_lca.py  — NEW: Premise prospective LCA module
    └── api/               — NEW: FastAPI bridge exposing compute endpoints
```

---

## Development Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code (always run before committing)
black swolfpy/ --line-length 100
isort swolfpy/ --profile black --line-length 100

# Lint
pylint swolfpy/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=swolfpy --cov-report=term-missing

# Pre-commit (runs black, isort, flake8 automatically)
pre-commit run --all-files
```

---

## Code Conventions

Sourced from `pyproject.toml` — **follow exactly**:

| Convention | Rule |
|-----------|------|
| Line length | 100 characters (black) |
| Imports | isort with black profile |
| Function names | `snake_case` |
| Class names | `PascalCase` |
| Constants | `UPPER_CASE` |
| Docstrings | Required on all public methods; use NumPy/Sphinx style (matching existing code) |
| Type hints | Required on all new functions and class signatures |
| Module size | Max 1000 lines per module (split if larger) |
| Max function args | 5 (use dataclasses or config objects for more) |

**Single Responsibility Principle**: each module handles exactly one concern.

### Docstring format (match existing style)

```python
def my_function(param1: str, param2: int) -> pd.DataFrame:
    """
    Brief one-line description.

    :param param1: Description of param1
    :type param1: str

    :param param2: Description of param2
    :type param2: int

    :return: Description of return value
    :rtype: pd.DataFrame
    """
```

---

## Module Map

| File | Purpose |
|------|---------|
| `swolfpy/Project.py` | Main orchestrator — creates Brightway2 project, writes databases, runs LCA |
| `swolfpy/LCA_matrix.py` | Constructs tech/bio matrices from process model reports |
| `swolfpy/Monte_Carlo.py` | Parallel Monte Carlo simulation (multiprocessing) |
| `swolfpy/Optimization.py` | Waste flow optimization (scipy-based) |
| `swolfpy/Parameters.py` | Manages waste routing fractions (parameters) |
| `swolfpy/ProcessDB.py` | Translates process model reports → Brightway2 database format |
| `swolfpy/Technosphere.py` | Sets up Brightway2 technosphere structure |
| `swolfpy/swolfpy_method.py` | Imports LCIA methods from CSV files |
| `swolfpy/UI/` | PySide2 desktop GUI — can be improved; still uses `brightway2` imports that need BW2.5 migration |

### Files to create (upcoming work)

| File | Purpose |
|------|---------|
| `swolfpy/dynamic_lca.py` | `DynamicLCA` class — Temporalis integration |
| `swolfpy/prospective_lca.py` | `ProspectiveLCA` class — Premise integration |
| `api/main.py` | FastAPI app — compute bridge |
| `api/routes/compute.py` | LCA, dynamic LCA, prospective LCA endpoints |
| `api/routes/jobs.py` | Async job polling |
| `api/cache.py` | Premise database disk cache |
| `tests/test_dynamic_lca.py` | Tests for dynamic LCA module |
| `tests/test_prospective_lca.py` | Tests for prospective LCA module |

---

## Key Dependencies

```
brightway25>=1.0     # Brightway 2.5 meta-package (replaces old brightway2==2.4.1)
bw2data>=4.0         # Core database API — bd.Database, bd.get_node, bd.projects
bw2calc>=2.0         # LCA computation — bc.LCA, bc.MultiLCA, bd.prepare_lca_inputs
bw2io>=0.9           # Import/export — bw2io.bw2setup, SingleOutputEcospold2Importer
bw2parameters>=1.1.0 # Parameter management
bw_temporalis>=1.0   # Dynamic LCA (requires bw2data>=4.0)
premise              # Prospective LCA via IAM scenarios
```

**Prerequisites before Premise work:**
1. Obtain an **ecoinvent 3 license** from ecoinvent.ch (paid)
2. Request **Premise encryption key** via email to `premise@psi.ch` (free)

---

## Brightway 2.5 Migration Notes (✅ Complete for core modules)

All core swolfpy modules have been migrated from `brightway2==2.4.1` to `bw2data>=4.0` /
`bw2calc>=2.0`. The following API changes were applied:

| Old (BW2) | New (BW2.5) |
|-----------|-------------|
| `from brightway2 import X` | `import bw2data as bd; import bw2calc as bc` |
| `projects.set_current()` | `bd.projects.set_current()` |
| `Database(name)` | `bd.Database(name)` |
| `get_activity((db, code))` | `bd.get_node(database=db, code=code)` |
| `LCA(fu, method)` | `fu, data_objs, _ = bd.prepare_lca_inputs(fu, method=m); bc.LCA(demand=fu, data_objs=data_objs)` |
| `lca.reverse_dict()` | `lca.remap_inventory_dicts()` → `lca.dicts.activity.reversed` |
| `lca.tech_params` / `lca.bio_params` | `lca.technosphere_matrix.tocoo()` / `lca.biosphere_matrix.tocoo()` |
| `lca.rebuild_technosphere_matrix(arr)` | `LCA_matrix.rebuild_technosphere_matrix(arr)` (COO-based) |
| `lca.activity_dict` | `lca.dicts.activity` (after `remap_inventory_dicts()`) |
| `MultiLCA(setups, methods)` | `bc.MultiLCA(demands=..., method_config=..., data_objs=...)` |
| `methods.flush()` | Removed — internal to `Method.write()` |

**Remaining BW2.5 migration needed:**
- `swolfpy/UI/PySWOLF_run.py` — still imports `brightway2`; migrate when UI work begins

---

## Testing Strategy

- **Unit tests**: every new public method in `dynamic_lca.py` and `prospective_lca.py`
  must have a corresponding test in `tests/`
- **Integration tests**: full LCA run using small synthetic waste stream (not full ecoinvent)
- **Do not** commit code that breaks existing tests
- Test coverage target: ≥80% on new modules
- Use `pytest.mark.slow` for tests that require Premise DB generation (>30s)

```python
# Mark slow tests so CI can skip them
@pytest.mark.slow
def test_premise_db_generation():
    ...
```

---

## Git Workflow

This project follows **GitHub Flow**: every change goes through a branch → commit → push →
PR → review → merge cycle. **Never commit directly to `master`.**

### Step-by-step for every change

**1. Create a feature branch**
```bash
git checkout master
git pull origin master
git checkout -b feature/<short-description>   # or fix/<issue>, chore/<task>
```

Branch naming examples:
- `feature/brightway25-upgrade`
- `feature/dynamic-lca-temporalis`
- `feature/premise-prospective-lca`
- `fix/monte-carlo-seed-collision`
- `chore/update-dependencies`

**2. Write tests first (TDD)**

Before writing implementation code, write the test:
```bash
# Create test file for the feature
touch tests/test_<feature>.py
# Write failing tests that describe the expected behaviour
pytest tests/test_<feature>.py -v   # should fail (red)
```

**3. Implement the change**

- Follow all conventions in the Code Conventions section above
- Keep each commit atomic — one logical change per commit
- Run the linter and formatter before every commit:

```bash
black swolfpy/ api/ mcp/ --line-length 100
isort swolfpy/ api/ mcp/ --profile black --line-length 100
pylint swolfpy/
pre-commit run --all-files
```

**4. Verify tests pass**
```bash
pytest tests/ -v --cov=swolfpy --cov-report=term-missing
# Coverage on new module must be ≥80%
# Zero existing tests may be broken
```

**5. Commit**

Commit messages must use imperative present tense and be descriptive:
```bash
git add <files>
git commit -m "Add DynamicLCA class with Temporalis backend"
```

Good commit messages:
- `Add DynamicLCA class with Temporalis temporal distribution support`
- `Upgrade brightway2 imports to Brightway 2.5 API`
- `Fix Monte Carlo seed collision in parallel workers`

Bad commit messages:
- `fix stuff`, `wip`, `changes`, `updated code`

**6. Push the branch**
```bash
git push -u origin feature/<short-description>
```

**7. Open a Pull Request**

Every PR must include:
- **Title**: same style as commit message (imperative, descriptive)
- **Summary**: what changed and why (not just what — the "why" matters)
- **Test plan**: list of tests added or modified and what they verify
- **Checklist** before requesting review:
  - [ ] Tests written and passing
  - [ ] Coverage ≥80% on new code
  - [ ] `black`, `isort`, `pylint` all pass
  - [ ] `CLAUDE.md` updated if architecture changed
  - [ ] No direct commits to `master`

**8. Code Review**

- All PRs require at least one review before merge
- Reviewer checks: logic correctness, test coverage, adherence to conventions
- Address all review comments before merging
- **Do not merge your own PR** without review (exception: trivial chores like dependency bumps)

**9. Merge**

- Use **squash merge** for feature branches (clean history on master)
- Use **merge commit** for release branches
- Delete the branch after merge

### Quick reference

```bash
# Full cycle in one flow
git checkout master && git pull origin master
git checkout -b feature/my-feature
# ... write tests, implement, lint ...
pytest tests/ -v
git add . && git commit -m "Add my feature with tests"
git push -u origin feature/my-feature
# → open PR on GitHub → request review → merge after approval
```

---

## MCP / API Design Principles

All MCP tools exposed to AI agents must:
- Have a `readOnlyHint: true` annotation on compute tools (they retrieve data, not mutate)
- Use `destructiveHint: true` only on tools that create/modify scenarios
- Include "Use this when..." in the description field
- Accept minimum required inputs only — no full chat transcripts, no GPS coordinates
- Return LLM-optimized markdown (not raw DataFrames or nested JSON)

### ChatGPT Developer Mode requirements
- MCP transport: **SSE or streaming HTTP** (not stdio)
- Server must expose: `GET /.well-known/openai-apps-challenge`
- Must be hosted on a **public domain** (Railway or Fly.io recommended)
- Authentication: no-auth for demo tier; OAuth for production

---

## ARIA Workflow (How Claude Should Work Here)

This project follows the ARIA (Automated Research Intelligence Assistant) framework:

1. **Spec first**: capture intent in this CLAUDE.md before touching code
2. **Small modules**: each file has one responsibility — never mix LCA logic with API logic
3. **Dependencies explicit**: update this document when adding new dependencies or modules
4. **Tests before merge**: no module ships without passing tests
5. **Repair loops**: if `mypy` or `pylint` fail, fix immediately before proceeding
6. **Audit trail**: every significant design decision lives in this file

### Before starting any task
1. Re-read the relevant section of this file
2. Check that existing tests still pass: `pytest tests/ -v`
3. Create a feature branch

### Before finishing any task
1. Run `black`, `isort`, `pylint` — fix all issues
2. Run `pytest` — all tests must pass
3. Update this CLAUDE.md if the architecture changed
4. Open a PR — never push directly to master

---

## docs/ — Design Documents & PRDs

Design documents and PRDs live at the **workspace level**: `../docs/` (i.e.,
`/wendylab-swolfpy/docs/`, one directory above this repo).
**Always check that directory before starting a task** — an open PRD may constrain
your approach.  When a task completes or the architecture changes, update or close
the relevant document.

| File | Description | Status |
|------|-------------|--------|
| `../docs/PRD_ecoinvent_upgrade.md` | Upgrade background LCI from ecoinvent 3.5 → 3.11/3.12 | Draft — blocked on ecoinvent license |

### Rules for docs/

- Create a new `PRD_<feature>.md` in `../docs/` whenever a non-trivial feature is scoped
  (more than ~2 days of work, or involving external data/licenses)
- Update the table above whenever a doc is added, closed, or its status changes
- Use the status values: **Draft**, **In Progress**, **Complete**, **Superseded**

---

## Current Work Context

**Active roadmap** (ordered by dependency):

- [x] **Phase 1**: Brightway 2.5 upgrade — all core modules migrated; UI migration deferred to UI work
- [ ] **Phase 2**: Temporalis integration — `swolfpy/dynamic_lca.py` + `tests/test_dynamic_lca.py`
- [ ] **Phase 3**: Premise integration — `swolfpy/prospective_lca.py` *(needs ecoinvent license)*
- [ ] **Phase 4**: FastAPI compute bridge — `api/main.py` + `api/routes/`
- [ ] **Phase 5**: MCP server (SSE transport) + ChatGPT Developer Mode deploy
- [ ] **Phase 6**: Yapplify config + Next.js human layer
- [ ] **Data upgrade**: ecoinvent 3.5 → 3.11/3.12 — see `docs/PRD_ecoinvent_upgrade.md`

**Do not skip phases** — each phase depends on the previous passing tests.

### UI Migration Scope (when UI work is started)

`swolfpy/UI/PySWOLF_run.py` still uses the old `brightway2` API. When making UI improvements:
- Replace `import brightway2 as bw` with `import bw2data as bd; import bw2calc as bc`
- Apply the same migration patterns from the table in the Brightway 2.5 Migration Notes section above
- PySide2 dependency (`PySide2==5.15.2.1`) is Python 3.9 max; consider upgrading to PySide6 for Python 3.10+
