import pytest
import numpy as np
from app.services.ahp_service import (
    validate_matrix_input,
    compute_priority_vector,
    compute_consistency_ratio,
    run_ahp,
    CRITERIA
)

def test_validate_matrix_valid():
    """Test ma trận 4x4 hợp lệ"""
    matrix = [
        [1, 3, 5, 7],
        [1/3, 1, 3, 5],
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ]
    mat = validate_matrix_input(matrix)
    assert isinstance(mat, np.ndarray)
    assert mat.shape == (4, 4)

def test_validate_matrix_invalid_shape():
    """Test kích thước không vuông hoặc không đủ 4 biến"""
    matrix = [
        [1, 3, 5],
        [1/3, 1, 3],
        [1/5, 1/3, 1]
    ]
    mat = validate_matrix_input(matrix)
    assert mat.shape == (3, 3)

def test_validate_matrix_not_reciprocal():
    """Test vi phạm tính nghịch đảo qua đường chéo"""
    matrix = [
        [1, 3, 5, 7],
        [1/4, 1, 3, 5],  # 1/4 != 1/3
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ]
    with pytest.raises(ValueError, match="Vi phạm reciprocal property"):
        validate_matrix_input(matrix)

def test_validate_matrix_diagonal_not_one():
    """Test đường chéo chính không bằng 1"""
    matrix = [
        [1, 3, 5, 7],
        [1/3, 2, 3, 5],  # Đường chéo = 2
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ]
    with pytest.raises(ValueError, match="Đường chéo chính phải = 1"):
        validate_matrix_input(matrix)

def test_compute_priority_vector():
    """Tính toán vector trọng số bằng độ trung bình nhân (Geometric Mean)"""
    matrix = np.array([
        [1, 3, 5, 7],
        [1/3, 1, 3, 5],
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ])
    pv = compute_priority_vector(matrix)
    # Tổng các trọng số phải bằng 1
    assert pytest.approx(pv.sum(), 0.0001) == 1.0
    # Thứ bậc phải giảm dần do C1 > C2 > C3 > C4
    assert pv[0] > pv[1] > pv[2] > pv[3]

def test_compute_consistency_ratio():
    """Kiểm tra tính CR và các thành phần: lambda_max, CI, RI, CR"""
    matrix = np.array([
        [1, 3, 5, 7],
        [1/3, 1, 3, 5],
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ])
    pv = compute_priority_vector(matrix)
    cr_dict = compute_consistency_ratio(matrix, pv)
    
    assert "lambda_max" in cr_dict
    assert "ci" in cr_dict
    assert "ri" in cr_dict
    assert "cr" in cr_dict
    # Đối với ma trận nhất quán (perfect or near-perfect consistency like above), CR sẽ < 0.1
    assert cr_dict["cr"] < 0.1

def test_run_ahp_strict_mode_pass():
    """Test run_ahp() vượt qua strict mode (CR < 0.1)"""
    matrix = [
        [1, 3, 5, 7],
        [1/3, 1, 3, 5],
        [1/5, 1/3, 1, 3],
        [1/7, 1/5, 1/3, 1]
    ]
    result = run_ahp(matrix, strict=True)
    assert result["is_consistent"] is True
    assert result["consistency"]["cr"] < 0.1
    assert len(result["weights"]) == 4

def test_run_ahp_strict_mode_fail():
    """Test run_ahp() ném ValueError nếu ma trận không nhất quán (CR >= 0.1)"""
    # Ma trận này bị lỗi consistency mạnh: C1 rất lớn hơn C2, C2 rất lớn so với C3, nhưng C1 lại bằng C3
    matrix = [
        [1, 9, 1, 1],
        [1/9, 1, 9, 1],
        [1, 1/9, 1, 9],
        [1, 1, 1/9, 1]
    ]
    with pytest.raises(ValueError, match="vượt ngưỡng 0.1"):
        run_ahp(matrix, strict=True)
