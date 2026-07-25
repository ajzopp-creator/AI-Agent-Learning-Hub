# P300 Extraction Workflow Technical Spec v2.7

## 1. Objective

Build Pipeline A, the write-side extraction workflow, to ingest VantagePoint historical symbol files into the shared SQLite catalog, normalize pattern windows for cross-symbol comparison, compute forward labels at 5, 7, 10, 15, and 20 days, and tag large-move outcomes where absolute percent return is at least 15 percent.

## 2. Pipeline boundary

This spec covers Pipeline A only.

- Pipeline A = Add Pattern, write-side catalog growth.
- Pipeline B = Daily Evaluate, read-only candidate scoring and BUY/WATCH/PASS output.

Do not merge the two pipelines into one script.

## 3. Inputs

Each source file should provide:

- Symbol.
- Source filename.
- Source path.
- Date coverage.
- Export type.
- Import timestamp.
- Optional hold-day context.

Accepted source type:

- VantagePoint history-grid export or equivalent derived symbol file.

## 4. Catalog tables

The extraction workflow writes into the following tables.

| Table | Purpose | Key fields |
|---|---|---|
| `symbols` | Symbol registry | `symbolid`, `symbol` |
| `sourcefiles` | File provenance | `sourcefileid`, `filename`, `symbol`, `holddays`, `importedat` |
| `patternbars` | Normalized bar data | `patternbarid`, `patterninstanceid`, `baroffset`, `bardate`, normalized OHLC/volume fields |
| `featuresets` | Feature version control | `featuresetid`, `featureversion` |
| `patterninstances` | Anchored pattern windows | `patterninstanceid`, `symbolid`, `sourcefileid`, `anchordate`, `featuresetid`, `windowlength` |
| `patternfeatures` | Feature vector storage | `patternfeatureid`, `patterninstanceid`, `featurename`, `featurevalue` |
| `forwardlabels` | Forward outcome labels | `forwardlabelid`, `patterninstanceid`, `holddays`, `absolutereturn`, `percentreturn`, `direction`, `profitable` |

## 5. Validation rules

Reject or quarantine a record when:

- Symbol metadata is missing.
- Symbol-date bars are duplicated.
- The window does not have enough prior bars.
- Forward bars are missing for a requested horizon.
- A field is non-numeric where numeric data is required.
- The feature count does not match the approved version.
- The forward label count does not match the approved horizon list.
- The catalog schema does not match the expected version.

## 6. Processing flow

### Step 1: Catalog check-out

Confirm the SQLite catalog exists, open it, and record baseline counts for core tables.

### Step 2: Register source file

Insert a row into `sourcefiles` and ensure the symbol exists in `symbols`.

### Step 3: Normalize bars

Parse the source file into bar rows, coerce numeric fields, standardize dates, and compute normalized columns.

### Step 4: Build pattern windows

For each anchor date, collect a lookback window of length `windowlength` and create one `patterninstances` row.

### Step 5: Store pattern bars

Insert one `patternbars` row per bar in the anchored window.

### Step 6: Generate features

Insert one `patternfeatures` row per feature in the approved feature set.

### Step 7: Compute forward labels

For each horizon in `[5, 7, 10, 15, 20]`, compute absolute return, percent return, direction, and profitable flag, then store the result in `forwardlabels`.

### Step 8: Apply 15 percent tag

Set `significantmove15 = 1` when `abs(percentreturn) >= 15`, otherwise `0`.

### Step 9: Validate totals

Confirm row counts reconcile across pattern instances, pattern bars, features, and labels.

### Step 10: Commit atomically

Write the batch into the SQLite catalog only after validation passes.

### Step 11: Catalog check-in

Write a run summary and confirm post-operation counts.

## 7. Pseudocode

```text
for each source_file in source_files:
    open catalog
    check_out_catalog()
    ensure_symbol_exists(source_file.symbol)
    sourcefile_id = register_source_file(source_file)
    bars = parse_and_normalize(source_file)
    bars = deduplicate_and_validate(bars)

    for each anchor_date in eligible_anchor_dates(bars, windowlength):
        window = build_window(bars, anchor_date, windowlength)
        if not window_complete(window):
            continue

        patterninstance_id = insert_pattern_instance(
            symbol_id,
            sourcefile_id,
            anchor_date,
            featureset_id,
            windowlength
        )

        insert_pattern_bars(patterninstance_id, window)
        features = compute_features(window, featureversion)
        insert_pattern_features(patterninstance_id, features)

        for holddays in [5, 7, 10, 15, 20]:
            label = compute_forward_label(bars, anchor_date, holddays)
            if label is valid:
                label.significantmove15 = 1 if abs(label.percentreturn) >= 15 else 0
                insert_forward_label(patterninstance_id, holddays, label)

    validate_batch_counts()
    commit_if_valid()
    check_in_catalog()
```

## 8. Output artifacts

The workflow should produce:

- SQLite updates.
- Run summary report.
- Rejected-row log.
- Per-symbol counts.
- Optional review CSV for threshold-passing rows.

## 9. Implementation notes

- Keep window logic, labeling logic, and threshold logic in the domain layer.
- Keep file parsing and SQLite access in the infrastructure layer.
- Keep orchestration in the application layer.
- Keep thresholds, paths, and horizon lists in config.
- Keep persisted row models in schema definitions.