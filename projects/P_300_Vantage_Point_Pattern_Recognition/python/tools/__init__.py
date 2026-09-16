"""P_300 diagnostic/analysis tools package.

Split out of utilities/ (WO-P300-E5.001 Batch 2) -- these scripts read
FROM domain/ and infrastructure/ (mining calibration, walk-forward
audits, integrity checks), so they sit above those layers, not below
them as true primitives do. utilities/ keeps only the true leaves
(db_connect, db_utils, archive_*_file, intelliscan_reader,
inspect_pattern) that infrastructure/application import FROM and that
import nothing back.
"""
