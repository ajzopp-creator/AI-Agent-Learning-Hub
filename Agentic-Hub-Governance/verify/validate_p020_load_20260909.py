import sys
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub")

result_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\validate_p020_load_result.txt"

try:
    # Simulate P_400 already having its own 'config' loaded, same as cli.py does
    import importlib
    sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
    import config as p400_config
    assert not hasattr(p400_config, "DATABASE_DIR"), "unexpected: P_400 config now has DATABASE_DIR"

    from shared_resources.python_utils.p020_order_writer import _load_p020
    schemas, get_connection, insert_order = _load_p020()

    # P_400's own config module must be untouched after the call
    import config as p400_config_after
    assert not hasattr(p400_config_after, "DATABASE_DIR"), "P_400 config got polluted with DATABASE_DIR"
    assert p400_config_after is p400_config, "P_400 config module identity changed"

    with open(result_path, "w") as f:
        f.write("PASS: _load_p020() succeeded, P_400 config untouched\n")
except Exception as e:
    with open(result_path, "w") as f:
        f.write("FAIL: " + repr(e) + "\n")
    sys.exit(1)
