import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tools.compute_dosage_tool import compute_dosage

# --- Happy Path ---

def test_happy_path_below_max():
    result = compute_dosage(70, 5, 500)
    assert result["result"] == 350
    assert result["unit"] == "mg"

def test_happy_path_at_max():
    result = compute_dosage(70, 5, 350)
    assert result["result"] == 350
    assert result["unit"] == "mg"

def test_happy_path_capped_at_max():
    result = compute_dosage(100, 5, 400)
    assert result["result"] == 400
    assert result["unit"] == "mg"

# --- Edge Cases ---

def test_very_small_weight():
    result = compute_dosage(0.5, 10, 500)
    assert result["result"] == 5
    assert result["unit"] == "mg"

def test_very_large_weight():
    result = compute_dosage(300, 5, 500)
    assert result["result"] == 500
    assert result["unit"] == "mg"

def test_float_inputs():
    result = compute_dosage(70.5, 4.5, 500)
    assert result["result"] == pytest.approx(317.25)
    assert result["unit"] == "mg"

def test_int_inputs_accepted():
    result = compute_dosage(70, 5, 500)
    assert isinstance(result["result"], (int, float))

def test_detail_key_present():
    result = compute_dosage(70, 5, 500)
    assert "detail" in result
    assert isinstance(result["detail"], str)

# --- Type Errors ---

def test_weight_wrong_type():
    with pytest.raises(TypeError):
        compute_dosage("70", 5, 500)

def test_drug_wrong_type():
    with pytest.raises(TypeError):
        compute_dosage(70, None, 500)

def test_max_dose_wrong_type():
    with pytest.raises(TypeError):
        compute_dosage(70, 5, [500])

# --- Value Errors ---

def test_negative_weight():
    with pytest.raises(ValueError):
        compute_dosage(-70, 5, 500)

def test_zero_weight():
    with pytest.raises(ValueError):
        compute_dosage(0, 5, 500)

def test_negative_drug():
    with pytest.raises(ValueError):
        compute_dosage(70, -5, 500)

def test_zero_drug():
    with pytest.raises(ValueError):
        compute_dosage(70, 0, 500)

def test_negative_max_dose():
    with pytest.raises(ValueError):
        compute_dosage(70, 5, -500)

def test_zero_max_dose():
    with pytest.raises(ValueError):
        compute_dosage(70, 5, 0)


# --- Load Testing ---

def test_load_100_requests():
    """Simulate 100 concurrent dosage calculation requests"""
    results = []
    for i in range(100):
        weight = 50 + i  # Vary weights
        result = compute_dosage(weight, 5, 500)
        results.append(result)
    
    assert len(results) == 100
    for result in results:
        assert "result" in result
        assert "unit" in result
        assert "detail" in result


def test_load_1000_requests():
    """Simulate 1000 requests with varied parameters"""
    import time
    start = time.time()
    
    for i in range(1000):
        weight = 30 + (i % 100)
        drug_dose = 2 + (i % 10)
        max_dose = 300 + (i % 200)
        result = compute_dosage(weight, drug_dose, max_dose)
        assert result["result"] > 0
    
    elapsed = time.time() - start
    avg_time_ms = (elapsed / 1000) * 1000
    
    print(f"\n1000 requests completed in {elapsed:.3f}s (avg {avg_time_ms:.3f}ms per request)")
    assert avg_time_ms < 10  # Should be very fast
