"""skip_list_reader.py -- Reads a schema's optional Chaikin skip-list CSV.

I/O only. A schema's skip list (if configured in SCHEMA_SKIP_LISTS) names
symbols Chaikin structurally cannot rate -- pattern established by P_300's
own WO-P300-E5.007 (data\\reference\\chaikin_skip_list.csv, columns
symbol/class/reason/evidence_date/evidence_source). Missing file or
unconfigured schema both return an empty dict (no filter), matching the
graceful fallback the prior P_300-local PowerShell version used. Built
against WO-P800-E4.001 (skip-list extension, 2026-08-12).

CHANGELOG:
  v1.0  2026-08-12  Initial version.
"""

import csv

from shared_resources.chaikin_enrichment.config import SCHEMA_SKIP_LISTS


def read_skip_list(schema_name: str) -> dict[str, str]:
    """Reads the skip-list symbols configured for one schema, if any.

    Args:
        schema_name: A key in SCHEMAS_ENABLED (e.g. "P115", "P300").

    Returns:
        Dict mapping symbol -> reason (empty string if the CSV has no
        'reason' column). Empty dict if the schema has no configured
        skip list, or the file doesn't exist yet -- both are legitimate,
        not errors (a schema without a skip list is the common case).
    """
    path = SCHEMA_SKIP_LISTS.get(schema_name)
    if path is None or not path.is_file():
        return {}

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {
            row["symbol"]: row.get("reason", "")
            for row in reader
            if row.get("symbol")
        }
