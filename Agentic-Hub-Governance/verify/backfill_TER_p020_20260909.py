import sys
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub")
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")

result_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\backfill_TER_p020_result.txt"

lines = []
try:
    from shared_resources.python_utils.p020_order_writer import submit_order

    orders = [
        ("15107400037",),
        ("15107399897",),
    ]

    for (schwab_order_id,) in orders:
        p020_id = submit_order(
            account_id="AJZ6348",
            symbol="TER",
            side="long",
            qty=3,
            why_code="P_300",
            planned_entry_price=380.61,
            planned_stop_price=350.9399276855796,
            planned_target_price=444.170013427734,
            schwab_order_id=schwab_order_id,
            council_verdict="APPROVED",
            source_project="P400",
            trade_mode="PAPER",
        )
        lines.append(f"schwab_order_id={schwab_order_id} -> p020_order_id={p020_id}")

    with open(result_path, "w") as f:
        f.write("PASS\n" + "\n".join(lines) + "\n")
except Exception as e:
    with open(result_path, "w") as f:
        f.write("FAIL: " + repr(e) + "\n" + "\n".join(lines) + "\n")
    sys.exit(1)
