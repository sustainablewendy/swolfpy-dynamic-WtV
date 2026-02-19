# PRD: swolfpy Background LCI Upgrade — ecoinvent 3.5 → 3.11/3.12

**Type:** Data Engineering + Software
**Status:** Draft
**Owner:** WENDY.LAB
**Created:** 2026-02-19
**Depends on:** Phase 1 (Brightway 2.5 upgrade, ✅ complete), ecoinvent license

---

## 1. Problem Statement

swolfpy's entire background LCI dataset was built against **ecoinvent 3.5 (released 2018)**.
Since then:

- ecoinvent has released 3.6 through 3.11 (3.12 in active development) with updated
  processes for electricity, materials, transport, and manufacturing.
- The elementary flow (biosphere3) UUIDs have changed across versions.  We've patched 11
  stale UUIDs via `uuid_migration.py` (Phase 1), but this is a workaround, not a
  principled update.
- Two swolfpy LCIA methods are explicitly named `"Ecoinvent V3.5"` — a methodological
  liability for published research.
- The carbon intensity of electricity grids, steel, cement, and plastics in ecoinvent has
  changed substantially since 2018, materially affecting LCA results.
- **Premise (Phase 3 dependency) requires ecoinvent 3.9+ as its starting database.**

Without updating the background data, swolfpy produces results that reflect a 6-year-old
world.  For a tool used in waste management policy and carbon accounting, this is a
measurable accuracy issue.

---

## 2. Scope

### In Scope

- Regenerate `Technosphere_LCI.csv` from ecoinvent 3.11 (1752 rows × 68 background
  processes)
- Update all biosphere3 UUID references across the full data layer
- Update LCIA characterization factor (CF) files to current method versions
- Patch `keys.csv` (1752 entries) to match the ecoinvent 3.11 biosphere3
- Patch process model data files (UUID corrections in `swolfpy_inputdata`)
- Add a reproducible data pipeline script so upgrades to 3.12+ can be scripted

### Out of Scope

- Changing process model logic (LF, WTE, AD, Comp, etc. remain unchanged)
- Replacing TRACI 2.1 or CML 4.4 with newer impact methods (separate decision)
- Desktop UI overhaul
- Full ecoinvent technosphere import into swolfpy — the pre-calculated LCI architecture
  is intentional (performance; no license required at runtime)

---

## 3. Data Architecture (current state)

| Asset | Location | ecoinvent dependency | Size |
|-------|----------|----------------------|------|
| `Technosphere_LCI.csv` | `swolfpy_inputdata` | Pre-calc'd LCI from 68 ecoinvent 3.5 processes | 1755 rows × 69 cols |
| `Technosphere_References.csv` | `swolfpy_inputdata` | ecoinvent 3.5 activity names + UUIDs | 68 rows |
| `keys.csv` | `swolfpy_inputdata` | 1752 biosphere3 flow keys (ecoinvent 3.5 UUIDs) | 1753 rows |
| `lcia_methods/*.csv` | `swolfpy_inputdata` | 13 CF files; 2 explicitly named "Ecoinvent V3.5" | ~1617 CFs |
| `LF_Leachate_Quality.csv` | `swolfpy_inputdata` | Direct biosphere3 UUID refs | ~50 rows |
| `LF_Gas_emission_factors.csv` | `swolfpy_inputdata` | Direct biosphere3 UUID refs (all valid) | 50 rows |
| `Reprocessing_Input.csv` | `swolfpy_inputdata` | Direct biosphere3 UUID refs | 427 rows |
| `Required_keys.py` | **this repo** | 1752-entry Python list mirroring `keys.csv` | 1752 entries |

---

## 4. Work Streams

### WS-1: Environment Setup *(Prerequisite)*

- Acquire **ecoinvent 3.11 license** and download ecospold2 files from ecoinvent.ch
- Set up a dedicated Brightway2 project with the full ecoinvent 3.11 database imported via
  `bw2io.SingleOutputEcospold2Importer`
- Verify clean import (zero unlinked exchanges)
- **Deliverable:** `scripts/setup_ecoinvent.py` — reproducible project builder

### WS-2: biosphere3 UUID Reconciliation

- Diff ecoinvent 3.11 biosphere3 UUIDs against the current `keys.csv`
- Identify all stale, renamed, merged, or split flows
- Extend `swolfpy/uuid_migration.py` with any new remappings discovered
- Re-validate all 1752 `Required_keys.py` entries against ecoinvent 3.11 biosphere3
- **Deliverable:**
  - Updated `uuid_migration.py`, `Required_keys.py`, `keys.csv`
  - `scripts/validate_biosphere_keys.py` — automated validation script

### WS-3: Technosphere LCI Regeneration *(largest work stream)*

For each of the **68 background processes** in `Technosphere_References.csv`:

1. Map the old ecoinvent 3.5 activity name/UUID to its ecoinvent 3.11 equivalent
   (handling renames, restructures, and regional variants)
2. Run a unit-process LCA calculation in Brightway2 using the ecoinvent 3.11 database
3. Extract the per-unit biosphere inventory vector (1752 elementary flows)
4. Populate the corresponding column in the new `Technosphere_LCI.csv`

Key process groups requiring careful mapping:
- Electricity production/consumption (grid mixes change every version)
- Transport (heavy/medium duty truck, rail, barge, cargo ship)
- Fuels (diesel, gasoline, LPG, CNG, residual fuel oil)
- Materials (HDPE, PET, steel, aluminum, concrete, asphalt)
- Chemicals and utilities (heat/steam, water treatment)

**Deliverable:**
- Reproducible pipeline: `scripts/regenerate_technosphere.py`
- Updated `Technosphere_LCI.csv` (date-stamped 2025, ecoinvent 3.11)
- Activity matching audit log: `docs/technosphere_activity_mapping.csv`

### WS-4: LCIA Method Update

The 13 CF files in `swolfpy_inputdata/data/lcia_methods/`:

| Current method | Action |
|---------------|--------|
| `('IPCC 2007, Ecoinvent V3.5', 'climate change', 'GWP 100a, bioCO2=0')` | Replace with IPCC AR6 GWP100 (CH₄: 25→29.8, N₂O: 298→273 for fossil) |
| `('IPCC 2007, Ecoinvent V3.5', 'climate change', 'GWP 100a, bioCO2=1')` | Replace with IPCC AR6 GWP100 biogenic |
| `('IPCC 2013, Ecoinvent V3.5', ...)` × 4 variants | Replace with IPCC AR6 variants |
| `('TRACI (2.1) SwolfPy', ...)` × 3 | UUID remapping only; CF values stable |
| `('CML (v4.4) SwolfPy', ...)` | UUID remapping only; CF values stable |
| `('SwolfPy_*Cost', ...)` × 3 | No ecoinvent dependency; no change |

**Deliverable:**
- Updated CF CSV files
- Method names updated to remove "Ecoinvent V3.5" suffix
- Migration notes for users who have stored results with old method names

### WS-5: Process Model Data Files *(in `swolfpy_inputdata`)*

Files with direct biosphere3 UUID references:

| File | Stale UUIDs | Current workaround |
|------|------------|-------------------|
| `LF_Leachate_Quality.csv` | 1 (Nickel II) | `uuid_migration.py` runtime remap |
| `Reprocessing_Input.csv` | 2 (Sulfate, HCl) | `uuid_migration.py` runtime remap |

Options:
- **(A) Fork** `swolfpy_inputdata` → `wendy-inputdata`; apply patches; publish
- **(B) PR upstream** to the original `swolfpy_inputdata` repo
- **(C) Keep runtime patching** via `uuid_migration.py` (current; acceptable short-term)

**Deliverable:** Decision + either PR or fork with corrected data files

### WS-6: Reproducibility & CI

- All data regeneration scripts are deterministic and checked into `scripts/data_pipeline/`
- GitHub Actions workflow: verify UUID validity on every push (`validate_biosphere_keys.py`
  checks `keys.csv` and `Required_keys.py` against bw2io-bundled biosphere3)
- Add `@pytest.mark.data_integrity` tests that don't require an ecoinvent license
- Document the full data pipeline in `docs/data_pipeline.md`

**Deliverable:** `scripts/data_pipeline/`, `.github/workflows/data_integrity.yml`,
data integrity tests

---

## 5. Dependencies & Blockers

| Dependency | Type | Owner | Status |
|------------|------|--------|--------|
| ecoinvent 3.11 license | Hard blocker for WS-1, WS-2, WS-3, WS-4 | Institution | ❌ Not acquired |
| `bw2io` ecoinvent 3.11 importer | Soft dependency | Brightway team | ✅ Available in bw2io 0.9.x |
| Premise encryption key | Required for Phase 3 (prospective LCA) | PSI @ psi.ch (free) | ❌ Not requested |
| `swolfpy_inputdata` maintainer access | For WS-5 option B | Upstream maintainer | Unknown |

---

## 6. Non-Goals / Deferred

- TRACI 2.2 or ReCiPe 2016 — out of scope; can be added as a follow-on PRD
- Dynamic characterization factors (relevant to Phase 2 dynamic LCA integration)
- Full ecoinvent technosphere import into swolfpy (intentionally out of scope for
  performance and license-portability reasons)
- Updating process model engineering parameters (LF gas collection efficiency, WTE boiler
  efficiency, etc.) — separate research update

---

## 7. Success Criteria

| Criterion | Metric |
|-----------|--------|
| Zero stale UUID warnings in test run | 0 `UserWarning` from `uuid_migration` or `swolfpy_method` |
| All 68 technosphere processes matched in ecoinvent 3.11 | 68/68 match in activity audit log |
| Technosphere LCI regenerated | `Technosphere_LCI.csv` date-stamped 2025, all 68 columns non-zero |
| LCIA methods updated | Method names no longer contain "Ecoinvent V3.5"; AR6 GWP100 values present |
| CI data integrity check | GitHub Actions `validate_biosphere_keys.py` passes on every push |
| Existing tests still pass | `pytest tests/test_swolfpy.py -v` green |
| Premise integration unlocked | Phase 3 can import ecoinvent 3.11 via Premise |

---

## 8. Effort Estimate

| Work Stream | Estimated Days | Primary Blocker |
|-------------|---------------|-----------------|
| WS-1: Environment setup | 1–2 | ecoinvent license |
| WS-2: UUID reconciliation | 1–2 | bw2io + ecoinvent license |
| WS-3: Technosphere LCI regeneration | **10–15** | ecoinvent license; bulk of effort |
| WS-4: LCIA method update | 2–3 | None (biosphere3 only) |
| WS-5: Process model data files | 1–2 | Decision on fork vs PR |
| WS-6: Reproducibility + CI | 2–3 | None |
| **Total** | **~17–27 days** | |

---

## 9. Relationship to Active Roadmap

```
Phase 1 (✅ complete)
  Brightway 2.5 upgrade

Phase 2 (next)
  dynamic_lca.py — Temporalis integration
  (no ecoinvent dependency)

Phase 3 (blocked on ecoinvent license)
  prospective_lca.py — Premise integration
  Premise requires ecoinvent 3.9+ as input database
       ↑
       └── This PRD (ecoinvent 3.11 upgrade) DIRECTLY ENABLES Phase 3
           WS-1 and Phase 3 share the same license prerequisite
           and can be executed in parallel once the license is obtained.

Phase 4 – FastAPI bridge
Phase 5 – MCP server
Phase 6 – Railway deploy + ChatGPT Developer Mode
```

The Premise-generated prospective databases (Phase 3) will serve as the scenario layer
on top of the ecoinvent 3.11 baseline established by this PRD.

---

## 10. Open Questions

1. **Target version: 3.11 or 3.12?**
   3.11 is the current stable release; 3.12 is in beta. Recommend 3.11 for stability,
   with the regeneration pipeline designed to re-run against 3.12 when it stabilizes.

2. **IPCC AR5 → AR6 GWP100 values?**
   Switching from AR5 to AR6 changes CH₄ GWP100 from 28 → 29.8 and N₂O from 265 → 273
   (fossil), affecting final results.  Does this require a versioned method name cutover
   (keeping old methods for backward compatibility) or a clean replacement?

3. **swolfpy_inputdata ownership**
   Does WENDY.LAB want to maintain a fork with continuous updates, or contribute
   upstream to the original package?

4. **Automation scope**
   Should WS-3 be a one-time manual effort, or a fully automated data pipeline
   (rerunnable against any future ecoinvent version with a single command)?
   Automating it is ~3× more effort upfront but pays off for 3.12 and beyond.
