"""
Quick test runner for realized_return.py.
Run from ISE: python test_realized_quick.py
"""

import sys
from pathlib import Path

# Add python/ to path
project_root = Path(__file__).resolve().parent
python_dir = project_root / "python"
sys.path.insert(0, str(python_dir))

from domain.realized_return import compute_realized_returns, is_profitable

def test_positive_return():
    anchor, horizons = 100.0, {5: 105.0}
    result = compute_realized_returns(anchor, horizons)
    assert abs(result[5] - 0.05) < 0.0001, f'Expected 0.05, got {result[5]}'
    print('✓ Test 1: positive return (5%)')

def test_multiple_horizons():
    anchor, horizons = 100.0, {5: 103.42, 7: 105.10, 10: 106.21, 15: 107.55, 20: 108.91}
    result = compute_realized_returns(anchor, horizons)
    assert abs(result[5] - 0.0342) < 0.0001
    assert abs(result[7] - 0.0510) < 0.0001
    assert abs(result[10] - 0.0621) < 0.0001
    assert abs(result[15] - 0.0755) < 0.0001
    assert abs(result[20] - 0.0891) < 0.0001
    print('✓ Test 2: multiple horizons (5/7/10/15/20 days)')

def test_negative_return():
    anchor, horizons = 100.0, {5: 95.0}
    result = compute_realized_returns(anchor, horizons)
    assert abs(result[5] - (-0.05)) < 0.0001, f'Expected -0.05, got {result[5]}'
    print('✓ Test 3: negative return (-5%)')

def test_zero_return():
    anchor, horizons = 100.0, {5: 100.0}
    result = compute_realized_returns(anchor, horizons)
    assert result[5] == 0.0
    print('✓ Test 4: zero return (break-even)')

def test_is_profitable():
    assert is_profitable(0.05, 0.0) == True
    assert is_profitable(0.02, 0.05) == False
    assert is_profitable(0.0, 0.0) == True
    print('✓ Test 5: is_profitable logic')

def test_invalid_anchor():
    try:
        compute_realized_returns(0.0, {5: 100.0})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "anchor_close must be positive" in str(e)
        print('✓ Test 6: invalid anchor (zero) raises ValueError')

def test_fractional_prices():
    anchor = 234.567
    horizons = {5: 238.123}
    result = compute_realized_returns(anchor, horizons)
    expected = (238.123 - 234.567) / 234.567
    assert abs(result[5] - expected) < 0.000001
    print('✓ Test 7: fractional prices (realistic)')

if __name__ == "__main__":
    try:
        test_positive_return()
        test_multiple_horizons()
        test_negative_return()
        test_zero_return()
        test_is_profitable()
        test_invalid_anchor()
        test_fractional_prices()
        print('\n✅ All 7 tests passed')
    except AssertionError as e:
        print(f'\n❌ Test failed: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
