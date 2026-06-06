"""
Tests for domain/realized_return.py.

Regression tests for realized return computation.
Mirrors expected behavior of labeler.py.
"""

import pytest
from domain.realized_return import compute_realized_returns, is_profitable


class TestComputeRealizedReturns:
    """Tests for compute_realized_returns()."""
    
    def test_positive_return_single_horizon(self):
        """Basic positive return: anchor=100, h5=105."""
        anchor = 100.0
        horizons = {5: 105.0}
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(0.05)  # 5%
    
    def test_negative_return_single_horizon(self):
        """Basic negative return: anchor=100, h5=95."""
        anchor = 100.0
        horizons = {5: 95.0}
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(-0.05)  # -5%
    
    def test_multiple_horizons(self):
        """Test all five horizons with realistic returns."""
        anchor = 100.0
        horizons = {
            5: 103.42,   # +3.42%
            7: 105.10,   # +5.10%
            10: 106.21,  # +6.21%
            15: 107.55,  # +7.55%
            20: 108.91,  # +8.91%
        }
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(0.0342, abs=0.0001)
        assert result[7] == pytest.approx(0.0510, abs=0.0001)
        assert result[10] == pytest.approx(0.0621, abs=0.0001)
        assert result[15] == pytest.approx(0.0755, abs=0.0001)
        assert result[20] == pytest.approx(0.0891, abs=0.0001)
    
    def test_zero_return(self):
        """Zero return: anchor == horizon close."""
        anchor = 100.0
        horizons = {5: 100.0}
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(0.0)
    
    def test_large_positive_return(self):
        """Large positive return: +50%."""
        anchor = 100.0
        horizons = {5: 150.0}
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(0.50)
    
    def test_large_negative_return(self):
        """Large negative return: -30%."""
        anchor = 100.0
        horizons = {5: 70.0}
        result = compute_realized_returns(anchor, horizons)
        
        assert result[5] == pytest.approx(-0.30)
    
    def test_invalid_anchor_zero(self):
        """Invalid: anchor_close == 0."""
        with pytest.raises(ValueError, match="anchor_close must be positive"):
            compute_realized_returns(0.0, {5: 100.0})
    
    def test_invalid_anchor_negative(self):
        """Invalid: anchor_close < 0."""
        with pytest.raises(ValueError, match="anchor_close must be positive"):
            compute_realized_returns(-100.0, {5: 100.0})
    
    def test_empty_horizons(self):
        """Empty horizons dict."""
        result = compute_realized_returns(100.0, {})
        assert result == {}
    
    def test_fractional_prices(self):
        """Realistic fractional prices."""
        anchor = 234.567
        horizons = {5: 238.123}
        result = compute_realized_returns(anchor, horizons)
        
        expected = (238.123 - 234.567) / 234.567
        assert result[5] == pytest.approx(expected)


class TestIsProfitable:
    """Tests for is_profitable()."""
    
    def test_profitable_above_threshold(self):
        """Return > threshold."""
        assert is_profitable(0.05, min_threshold=0.0) is True
        assert is_profitable(0.05, min_threshold=0.02) is True
    
    def test_profitable_equals_threshold(self):
        """Return == threshold."""
        assert is_profitable(0.05, min_threshold=0.05) is True
    
    def test_not_profitable_below_threshold(self):
        """Return < threshold."""
        assert is_profitable(0.02, min_threshold=0.05) is False
    
    def test_negative_return(self):
        """Negative return is not profitable (above 0.0)."""
        assert is_profitable(-0.03, min_threshold=0.0) is False
        assert is_profitable(-0.03, min_threshold=-0.05) is True
    
    def test_zero_return_zero_threshold(self):
        """Break-even."""
        assert is_profitable(0.0, min_threshold=0.0) is True
