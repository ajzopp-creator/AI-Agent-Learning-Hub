import sys
sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts')
from obsidian_writers.domain.validator import validate
from obsidian_writers.domain.filename_builder import build_filepath
from datetime import datetime

packet = {
    'signal_id': 'TEST-001',
    'signal_timestamp': datetime.utcnow().isoformat() + 'Z',
    'signal_source': 'P_115',
    'strategy': 'dip_buy',
    'symbol': 'TEST',
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
    validated = validate('P400SIG', packet)
    print('✓ Test 4a PASS: Packet validates')
    path = build_filepath('P400SIG', validated)
    print('✓ Test 4b PASS: JSON path built:', str(path)[-50:])
except Exception as e:
    print(f'✗ Test 4 FAIL: {e}')
    import traceback
    traceback.print_exc()
