"""
Cấu hình ngưỡng thông số cho các module trong hệ thống.
Định nghĩa khoảng giá trị bình thường cho từng loại thông số.
"""

# Ngưỡng cho các thông số module
MODULE_THRESHOLDS = {
    "Điện áp": {
        "min_normal": 7,    # V - Giá trị tối thiểu bình thường
        "max_normal": 10,   # V - Giá trị tối đa bình thường
        "unit": "V"
    },
    
    "Dòng điện": {
        "min_normal": 1,    # A - Giá trị tối thiểu bình thường
        "max_normal": 3,    # A - Giá trị tối đa bình thường
        "unit": "A"
    },
    
    "Công suất": {
        "min_normal": 5,    # W - Giá trị tối thiểu bình thường
        "max_normal": 10,   # W - Giá trị tối đa bình thường
        "unit": "W"
    },
    
    "Điện trở": {
        "min_normal": 40,   # Ω - Giá trị tối thiểu bình thường
        "max_normal": 60,   # Ω - Giá trị tối đa bình thường
        "unit": "Ω"
    }
}

# Ngưỡng riêng cho từng loại module (nếu cần)
MODULE_TYPE_THRESHOLDS = {
    "Module 1": {
        "Điện áp": {"min_normal": 6, "max_normal": 9, "unit": "V"},
        "Dòng điện": {"min_normal": 0.5, "max_normal": 2.5, "unit": "A"},
        "Công suất": {"min_normal": 3, "max_normal": 8, "unit": "W"},
        "Điện trở": {"min_normal": 35, "max_normal": 55, "unit": "Ω"}
    },
    
    "Module 2": {
        "Điện áp": {"min_normal": 7, "max_normal": 11, "unit": "V"},
        "Dòng điện": {"min_normal": 1, "max_normal": 4, "unit": "A"},
        "Công suất": {"min_normal": 5, "max_normal": 12, "unit": "W"},
        "Điện trở": {"min_normal": 40, "max_normal": 65, "unit": "Ω"}
    },
    
    "Module 3": {
        "Điện áp": {"min_normal": 8, "max_normal": 12, "unit": "V"},
        "Dòng điện": {"min_normal": 1.5, "max_normal": 4.5, "unit": "A"},
        "Công suất": {"min_normal": 6, "max_normal": 14, "unit": "W"},
        "Điện trở": {"min_normal": 45, "max_normal": 70, "unit": "Ω"}
    },
    
    "Module 4": {
        "Điện áp": {"min_normal": 7.5, "max_normal": 10.5, "unit": "V"},
        "Dòng điện": {"min_normal": 1.2, "max_normal": 3.8, "unit": "A"},
        "Công suất": {"min_normal": 4, "max_normal": 11, "unit": "W"},
        "Điện trở": {"min_normal": 42, "max_normal": 62, "unit": "Ω"}
    }
}


def get_threshold_for_parameter(module_name, parameter_name):
    """
    Lấy ngưỡng cho thông số cụ thể của module.
    
    Args:
        module_name (str): Tên module (ví dụ: "Module 1")
        parameter_name (str): Tên thông số (ví dụ: "Điện áp")
    
    Returns:
        dict: Dictionary chứa min_normal, max_normal, unit
    """
    # Ưu tiên ngưỡng riêng của module trước
    if module_name in MODULE_TYPE_THRESHOLDS:
        if parameter_name in MODULE_TYPE_THRESHOLDS[module_name]:
            return MODULE_TYPE_THRESHOLDS[module_name][parameter_name]
    
    # Fallback về ngưỡng chung
    if parameter_name in MODULE_THRESHOLDS:
        return MODULE_THRESHOLDS[parameter_name]
    
    # Mặc định nếu không tìm thấy
    return {"min_normal": 0, "max_normal": 100, "unit": ""}


def is_parameter_normal(module_name, parameter_name, value):
    """
    Kiểm tra xem thông số có nằm trong khoảng bình thường không.
    
    Args:
        module_name (str): Tên module
        parameter_name (str): Tên thông số
        value (float): Giá trị cần kiểm tra
    
    Returns:
        bool: True nếu bình thường, False nếu cao/thấp
    """
    threshold = get_threshold_for_parameter(module_name, parameter_name)
    return threshold["min_normal"] <= value <= threshold["max_normal"]
