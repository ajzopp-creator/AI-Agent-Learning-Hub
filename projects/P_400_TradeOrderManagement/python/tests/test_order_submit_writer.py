"""Tests for infrastructure.order_submit_writer -- the P_400-to-P_020
order-submit bridge (WO-P400-E6.001). No sys.path setup here -- this
project's conftest.py already puts python\\ on sys.path; a local
sys.path.insert() is forbidden by WO_COMPLETION_GATE (see conftest.py's
own docstring).
"""

from infrastructure.order_submit_writer import write_order_to_p020


def _submit(monkeypatch, fake_submit_order):
    monkeypatch.setattr(
        "shared_resources.python_utils.p020_order_writer.submit_order",
        fake_submit_order,
    )
    return write_order_to_p020(
        symbol="MSTR",
        order_id="123456",
        verdict="APPROVED",
        entry_price=100.0,
        stop_price=95.0,
        target_1=110.0,
        position_size=10,
        signal_source="P_115",
        trade_mode_value="REAL",
    )


def test_write_order_to_p020_always_sends_side_long(monkeypatch):
    """Every P_400 structure today is a debit position -- side must
    always be 'long', never derived from council_verdict or symbol."""
    received = {}

    def fake_submit_order(**kwargs):
        received.update(kwargs)
        return 42

    result = _submit(monkeypatch, fake_submit_order)

    assert result == 42
    assert received["side"] == "long"
    assert received["schwab_order_id"] == "123456"
    assert received["source_project"] == "P400"


def test_write_order_to_p020_returns_none_on_exception(monkeypatch):
    """A P_020-side failure must never raise -- the vault write is
    independent and must not be blocked by this."""
    def fake_submit_order(**kwargs):
        raise RuntimeError("P_020 write failed")

    result = _submit(monkeypatch, fake_submit_order)

    assert result is None
