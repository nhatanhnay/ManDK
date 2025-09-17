"""
Cấu hình ngưỡng thông số cho các module trong hệ thống.
Định nghĩa khoảng giá trị bình thường cho từng loại thông số.
"""

# Default ngưỡng cho các thông số module
DEFAULT_THRESHOLDS = {
    "Điện áp": {"min_normal": 8.0, "max_normal": 15.0, "unit": "V"},
    "Dòng điện": {"min_normal": 0.5, "max_normal": 8.0, "unit": "A"},
    "Công suất": {"min_normal": 1.0, "max_normal": 50.0, "unit": "W"},
    "Điện trở": {"min_normal": 10.0, "max_normal": 100.0, "unit": "Ω"}
}

# Ngưỡng động cho từng loại module (sẽ được cập nhật qua UI)
MODULE_TYPE_THRESHOLDS = {}


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
    
    # Fallback về ngưỡng mặc định
    if parameter_name in DEFAULT_THRESHOLDS:
        return DEFAULT_THRESHOLDS[parameter_name]

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

def update_module_parameter(node_id, module_name, parameter, value):
    """
    Cập nhật giá trị thông số của module.
    
    Args:
        node_id (str): ID của node chứa module
        module_name (str): Tên module
        parameter (str): Tên thông số
        value (float): Giá trị mới
    
    Returns:
        dict: Cấu trúc dữ liệu đã cập nhật
    """
    from data_management import module_manager
    
    if node_id in module_manager.modules:
        if module_name in module_manager.modules[node_id]:
            if parameter in module_manager.modules[node_id][module_name]:
                module_manager.modules[node_id][module_name][parameter] = value
                return module_manager.modules[node_id]
    
    raise ValueError(f"Không tìm thấy {module_name} hoặc {parameter} trong node {node_id}")

def update_module_threshold(node_id, module_name, parameter, min_normal=None, max_normal=None):
    """
    Cập nhật ngưỡng cho thông số của module.

    Args:
        node_id (str): ID của node chứa module
        module_name (str): Tên module
        parameter (str): Tên thông số
        min_normal (float, optional): Giá trị min mới
        max_normal (float, optional): Giá trị max mới

    Returns:
        dict: Cấu trúc dữ liệu đã cập nhật
    """
    # Cập nhật ngưỡng trong MODULE_TYPE_THRESHOLDS
    if module_name not in MODULE_TYPE_THRESHOLDS:
        MODULE_TYPE_THRESHOLDS[module_name] = {}

    if parameter not in MODULE_TYPE_THRESHOLDS[module_name]:
        # Lấy default từ DEFAULT_THRESHOLDS nếu có
        default_threshold = DEFAULT_THRESHOLDS.get(parameter, {"min_normal": 0, "max_normal": 100, "unit": ""})
        MODULE_TYPE_THRESHOLDS[module_name][parameter] = default_threshold.copy()

    # Cập nhật giá trị mới
    if min_normal is not None:
        MODULE_TYPE_THRESHOLDS[module_name][parameter]['min_normal'] = min_normal
    if max_normal is not None:
        MODULE_TYPE_THRESHOLDS[module_name][parameter]['max_normal'] = max_normal

    # Cũng cập nhật trong module_manager nếu có
    try:
        from data_management import module_manager

        if hasattr(module_manager, 'modules') and node_id in module_manager.modules:
            if module_name in module_manager.modules[node_id]:
                thresholds = module_manager.modules[node_id][module_name].setdefault('thresholds', {})
                if parameter not in thresholds:
                    thresholds[parameter] = {"min_normal": 0, "max_normal": 100, "unit": ""}
                if min_normal is not None:
                    thresholds[parameter]['min_normal'] = min_normal
                if max_normal is not None:
                    thresholds[parameter]['max_normal'] = max_normal
    except ImportError:
        pass  # module_manager không có sẵn

    # Force recheck status of all modules after threshold update
    refresh_all_module_statuses()

    return MODULE_TYPE_THRESHOLDS[module_name]


def refresh_all_module_statuses():
    """
    Làm mới status của tất cả modules sau khi thay đổi ngưỡng.
    """
    try:
        from data_management.module_data_manager import module_manager

        for node_modules in module_manager.modules.values():
            for module in node_modules.values():
                # Force recheck status with new thresholds
                module._check_status()

    except ImportError:
        pass  # module_manager không có sẵn


def save_thresholds_to_config():
    """Lưu ngưỡng vào file config (có thể implement sau)."""
    # TODO: Implement saving to config file
    pass


def load_thresholds_from_config():
    """Tải ngưỡng từ file config (có thể implement sau)."""
    # TODO: Implement loading from config file
    pass