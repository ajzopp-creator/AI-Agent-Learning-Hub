import sys
sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts')
from obsidian_writers.application.write_handler import handle_write
from datetime import datetime
from pathlib import Path

packet = {
    'signal_id': 'TEST-001',
    'signal_timestamp': datetime.utcnow().isoformat() + 'Z',
    'signal_source': 'P_115',
    'strategy': 'dip_buy',
    'symbol': 'TESTFILE',
    'guideline_entry': 100.0,
    'guideline_stop': 95.0,
    'guideline_target': 110.0,
    'signal_horizon': '3-5 days',
    'confidence_level': 'HIGH',
    'context': {
        'close_at_signal': 99.50,
        'trailing_volume_30d': 1000000,
        'signal_rationale': 'Test signal',
        'atm_at_signal': 1.50
    },
    'signal_metadata': {
        'p115_session_date': '2026-06-02',
        'p115_chart_timeframe': '1D',
        'signal_source_link': 'test/path'
    }
}

try:
    result = handle_write('P400SIG', packet, overwrite=True)
    if result:
        print('✓ Test 5 PASS: JSON written to disk')
        from obsidian_writers.config import SIGNALS_DIR
        expected = SIGNALS_DIR / '2026-06-02_TESTFILE_signal.json'
        if expected.exists():
            size = expected.stat().st_size
            print(f'✓ File exists: {expected.name} ({size} bytes)')
            with open(expected) as f:
                import json
                data = json.load(f)
                print(f'✓ Valid JSON with {len(data)} fields')
        else:
            print(f'✗ Expected file not found: {expected}')
    else:
        print('✗ handle_write returned False')
except Exception as e:
    print(f'✗ Test 5 FAIL: {e}')
    import traceback
    traceback.print_exc()
