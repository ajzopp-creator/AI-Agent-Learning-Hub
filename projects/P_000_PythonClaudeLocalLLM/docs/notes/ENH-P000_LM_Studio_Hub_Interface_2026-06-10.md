# ENH-P000 -- Publish LM Studio status as a Hub interface; remove external-service check from consumer application layers

**Type:** Enhancement proposal (P_300 -> P_000)
**Originator:** P_300 (Claude, architect) -- 2026-06-10
**Owner (proposed):** P_000 (Hub infrastructure: `integrations/`, `shared_resources/`, editable install)
**For P_000 to:** convert into a Work Order
**Relates to:** WO-P000-E2.003 (sys.path side-channel removal)

---

## WHY

P_300's read-side orchestrator reaches an external service through another component's
internals, gated inside the application layer. Three findings, on disk, 2026-06-10:

1. **Application-layer external-service check (Process Boundary violation).**
   `projects/P_300_.../python/application/daily_evaluate_pipeline.py` line 487:
   `if not lm_studio_check(clean=args.clean):` -- inside `main()`. The application
   layer is performing an external-service status check. The P_300 SKILL already names
   this exact file as the canonical violation: "`_check_lm_studio()` in
   `daily_evaluate_pipeline.py` -- LMS status is infrastructure, not orchestration."
   The v1.11 refactor moved the check out of an inline helper but left the application
   layer still calling it.

2. **Reach into integration internals; no Hub interface.**
   Line 133: `from integrations.lm_studio.infrastructure.lm_studio_status import check`.
   This imports the integration's *infrastructure* sublayer directly. There is no
   published Hub interface for LM Studio status. `shared_resources/python_utils/`
   holds `vault_interface.py` (Obsidian), `signal_schemas.py`, `xml_parser.py` --
   nothing for LM Studio. This is the M-038 pattern: the Obsidian cross-project reach
   was given a published interface (`vault_interface.write_to_vault`); the LM Studio
   reach never was.

3. **sys.path side-channel (the WO-P000-E2.003 row).**
   Lines 113-117 insert the Hub root at runtime so `integrations.lm_studio` resolves.
   E2.003 lists this insert (and three `integrations/lm_studio/infrastructure/*.py`
   inserts) as "now redundant via editable install." It is not -- the editable install
   covers `hub_lib*`, `shared_resources*`, and (after E2.003) `obsidian_writers*`.
   `integrations` is not in package discovery. Removing the insert without further work
   breaks the import (re-introduces the v1.9 ModuleNotFoundError). Adding `integrations`
   to the install would fix resolution but would still leave findings (1) and (2) intact
   -- a clean-looking import wrapping the same boundary breach.

**Net:** removing the sys.path insert alone launders the mechanism and leaves the layer
crossing. The three findings resolve together only with a Hub interface plus moving the
check out of the application layer.

---

## WHY P_000 SCOPE (and why now)

- `integrations/lm_studio` and `shared_resources/python_utils` are Hub-owned. Publishing
  an interface and adjusting the editable install (`pyproject.toml`) is P_000
  infrastructure, not a P_300 edit.
- P_300 is currently the **only** consumer of the LM Studio interface. Defining the Hub
  interface now -- before any second consumer couples to the integration internals --
  is the cheap moment. After a second consumer exists, the same fix touches more files.

---

## RECOMMENDED DESIGN (for P_000 to spec into the WO)

1. **Publish `shared_resources/python_utils/lm_studio_interface.py`** -- a thin Hub
   interface mirroring `vault_interface.py`. Exposes one stable status entry point
   (e.g. `lm_studio_status(clean: bool = False) -> StatusResult`) that wraps
   `integrations.lm_studio.infrastructure.lm_studio_status.check`. Consumers import the
   interface; never the integration internals (M-038). Ship a short README beside it,
   same as `VAULT_INTERFACE_README.md`.

2. **Decide editable-install coverage.** Preferred: keep `integrations` *behind* the
   shared_resources interface, so consumers never need `integrations` on the path at all.
   Then the E2.003 sys.path rows for `integrations/lm_studio/infrastructure/*.py` and for
   this P_300 file resolve through the install with no insert. (Alternative: add
   `integrations*` to the Hub pyproject include -- cleaner imports but exposes internals
   to every consumer; not recommended.)

3. **Move the status check out of P_300's application layer.** Orchestration should not
   gate on an external-service check. The narrator is already post-decision and optional
   (`--no-narrator`, `NARRATOR_ENABLED`), so the orchestrator arguably should not hard-gate
   on LM Studio at all. Two options for P_000 to weigh:
   - (a) an infrastructure-layer pre-flight that the CLI entrypoint runs *before* calling
     the orchestrator; the orchestrator stays unaware of LM Studio status; or
   - (b) the narrator infrastructure performs its own readiness check and degrades
     gracefully (narration skipped, signal unaffected).
   Either keeps `application/` doing orchestration only.

4. **Update the consumer** (`daily_evaluate_pipeline.py`) to import the Hub interface,
   then remove the lines 113-117 `_HUB_ROOT` insert and verify. The intra-project
   `_PYTHON_DIR` sibling insert (lines 109-111) stays -- out of scope, not a boundary
   violation.

---

## RELATIONSHIP TO WO-P000-E2.003

This enhancement **blocks** the E2.003 rows for:
- `projects/P_300/.../application/daily_evaluate_pipeline.py` line 117 (`_HUB_ROOT`)
- `integrations/lm_studio/infrastructure/lm_studio_api.py`
- `integrations/lm_studio/infrastructure/lm_studio_launcher.py`
- `integrations/lm_studio/infrastructure/lm_studio_status.py`

Recommend E2.003 mark those four rows **BLOCKED -- pending ENH-P000 LM Studio interface**
(or strike them and re-list under the new WO). The remaining E2.003 rows (P_115, P_805,
P_800 tests, vault_interface.py) are unaffected and proceed as written.

---

## VERIFY (for the eventual WO -- OWNER_DONE gate)

- `shared_resources/python_utils/lm_studio_interface.py` imports clean via the editable
  install in a fresh p140 interpreter, **eager execution** (not a bare import -- lazy
  imports do not prove resolution).
- No `integrations.*` import remains in any consumer **application-layer** module.
- P_300 `daily-evaluate` runs end-to-end with the `_HUB_ROOT` insert removed and the
  status check relocated.
- **NFR-1:** determinism replay vs a pre-change run -- BUY/WATCH/PASS output byte-identical
  (narration is post-decision; relocating its readiness check must not move any signal).
- Completion-gate checklist (WO-P000-E3.001) satisfied: path standards, downstream
  notification, no new sys.path side-channels, P_000_SYSTEM_DOCUMENTATION Document Index
  updated with the new interface, consumer CLAUDE.md references updated.

---

## OUT OF SCOPE

- The CE BUY gate work (Enhancement 2) -- unrelated.
- P_300's intra-project `_PYTHON_DIR` sibling-import insert (lines 109-111) -- stays.
- Any change to LM Studio model selection, the launcher, or narrator prompts -- this is
  interface + layer placement only.

---

**End of ENH-P000 -- LM Studio Hub Interface**
