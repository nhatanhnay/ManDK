# -*- coding: utf-8 -*-
"""
Common utilities module - Centralized functions used across the codebase.
Eliminates code duplication and provides consistent behavior.
"""

import os
import sys
import yaml
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource file.

    Args:
        relative_path: Relative path to the resource

    Returns:
        Absolute path to the resource
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)

    # Running as normal Python script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_button_colors() -> Dict[str, Any]:
    """
    Load button colors from config.yaml file.

    Returns:
        Dictionary containing button color configuration
    """
    config_path = resource_path('config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('ButtonColors', {})
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        return {}
    except Exception as e:
        print(f"Error loading button colors: {e}")
        return {}


def load_config(config_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from config.yaml file.

    Args:
        config_key: Specific configuration section to load (optional)

    Returns:
        Configuration dictionary or specific section
    """
    config_path = resource_path('config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config_key:
            return config.get(config_key, {})
        return config

    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def safe_file_operation(operation_func, *args, **kwargs):
    """
    Safely execute file operations with proper error handling.

    Args:
        operation_func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (success: bool, result: Any, error: str)
    """
    try:
        result = operation_func(*args, **kwargs)
        return True, result, ""
    except FileNotFoundError as e:
        return False, None, f"File not found: {e}"
    except PermissionError as e:
        return False, None, f"Permission denied: {e}"
    except Exception as e:
        return False, None, f"Operation failed: {e}"


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path exists and is accessible.

    Args:
        file_path: Path to validate

    Returns:
        True if path is valid and accessible
    """
    try:
        return os.path.exists(file_path) and os.access(file_path, os.R_OK)
    except Exception:
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        return False


class FiringTableInterpolator:
    """Nội suy bảng bắn để tìm góc tầm và các lượng sửa cho một khoảng cách."""
    
    def __init__(self, ranges: np.ndarray, angles: np.ndarray, 
                 z_data: Optional[np.ndarray] = None,
                 delta_zwhz: Optional[np.ndarray] = None,
                 delta_zwbez: Optional[np.ndarray] = None,
                 delta_zwhx: Optional[np.ndarray] = None,
                 delta_zwbe: Optional[np.ndarray] = None,
                 delta_xwhx: Optional[np.ndarray] = None,
                 delta_xwhz: Optional[np.ndarray] = None,
                 delta_xwbex: Optional[np.ndarray] = None,
                 delta_xkacn: Optional[np.ndarray] = None,
                 delta_xh: Optional[np.ndarray] = None,
                 delta_xt: Optional[np.ndarray] = None,
                 delta_xtsz: Optional[np.ndarray] = None,
                 delta_xtbic: Optional[np.ndarray] = None):
        """
        Khởi tạo interpolator với dữ liệu bảng bắn.
        
        Args:
            ranges: Mảng khoảng cách (X)
            angles: Mảng góc tầm (P) bằng ly giác
            z_data: Mảng giá trị Z
            delta_zwhz: Lượng sửa Z do gió hướng Z
            delta_zwbez: Lượng sửa Z do gió bên Z
            delta_zwhx: Lượng sửa Z do gió hướng X
            delta_zwbe: Lượng sửa Z do gió bên
            delta_xwhx: Lượng sửa X do gió hướng X
            delta_xwhz: Lượng sửa X do gió hướng Z
            delta_xwbex: Lượng sửa X do gió bên X
            delta_xkacn: Lượng sửa X do không khí chuyển động ngang
            delta_xh: Lượng sửa X do độ cao
            delta_xt: Lượng sửa X do nhiệt độ
            delta_xtsz: Lượng sửa X do nhiệt độ liều sử dụng
            delta_xtbic: Lượng sửa X do nhiệt độ bi có
        """
        if len(ranges) != len(angles):
            raise ValueError("Số lượng khoảng cách và góc tầm phải bằng nhau.")
        
        self.ranges = np.array(ranges)
        self.angles = np.array(angles)

        # Lưu các cột lượng sửa (nếu có)
        self.z_data = np.array(z_data) if z_data is not None else None
        self.delta_zwhz = np.array(delta_zwhz) if delta_zwhz is not None else None
        self.delta_zwbez = np.array(delta_zwbez) if delta_zwbez is not None else None
        self.delta_zwhx = np.array(delta_zwhx) if delta_zwhx is not None else None
        self.delta_zwbe = np.array(delta_zwbe) if delta_zwbe is not None else None
        self.delta_xwhx = np.array(delta_xwhx) if delta_xwhx is not None else None
        self.delta_xwhz = np.array(delta_xwhz) if delta_xwhz is not None else None
        self.delta_xwbex = np.array(delta_xwbex) if delta_xwbex is not None else None
        self.delta_xkacn = np.array(delta_xkacn) if delta_xkacn is not None else None
        self.delta_xh = np.array(delta_xh) if delta_xh is not None else None
        self.delta_xt = np.array(delta_xt) if delta_xt is not None else None
        self.delta_xtsz = np.array(delta_xtsz) if delta_xtsz is not None else None
        self.delta_xtbic = np.array(delta_xtbic) if delta_xtbic is not None else None
        
        # Đảm bảo các khoảng cách được sắp xếp tăng dần
        sort_indices = np.argsort(self.ranges)
        self.ranges = self.ranges[sort_indices]
        self.angles = self.angles[sort_indices]
        
        # Sắp xếp lại tất cả các mảng delta theo thứ tự của ranges
        if self.z_data is not None:
            self.z_data = self.z_data[sort_indices]
        if self.delta_zwhz is not None:
            self.delta_zwhz = self.delta_zwhz[sort_indices]
        if self.delta_zwbez is not None:
            self.delta_zwbez = self.delta_zwbez[sort_indices]
        if self.delta_zwhx is not None:
            self.delta_zwhx = self.delta_zwhx[sort_indices]
        if self.delta_zwbe is not None:
            self.delta_zwbe = self.delta_zwbe[sort_indices]
        if self.delta_xwhx is not None:
            self.delta_xwhx = self.delta_xwhx[sort_indices]
        if self.delta_xwhz is not None:
            self.delta_xwhz = self.delta_xwhz[sort_indices]
        if self.delta_xwbex is not None:
            self.delta_xwbex = self.delta_xwbex[sort_indices]
        if self.delta_xkacn is not None:
            self.delta_xkacn = self.delta_xkacn[sort_indices]
        if self.delta_xh is not None:
            self.delta_xh = self.delta_xh[sort_indices]
        if self.delta_xt is not None:
            self.delta_xt = self.delta_xt[sort_indices]
        if self.delta_xtsz is not None:
            self.delta_xtsz = self.delta_xtsz[sort_indices]
        if self.delta_xtbic is not None:
            self.delta_xtbic = self.delta_xtbic[sort_indices]

    def _interpolate_value(self, target_range: float, data_array: np.ndarray) -> float:
        """Helper method để nội suy một mảng giá trị."""
        if data_array is None:
            return 0.0
            
        if target_range < self.ranges[0] or target_range > self.ranges[-1]:
            # Ngoại suy tuyến tính cho các giá trị ngoài cùng
            if target_range < self.ranges[0]:
                return np.interp(target_range, self.ranges[:2], data_array[:2])
            else:
                return np.interp(target_range, self.ranges[-2:], data_array[-2:])
        else:
            return np.interp(target_range, self.ranges, data_array)

    def interpolate_angle(self, target_range: float) -> float:
        """Nội suy góc tầm cho một khoảng cách mục tiêu.
        
        Returns:
            Góc tầm tính bằng độ (degrees)
        """
        angle_mils = self._interpolate_value(target_range, self.angles)
        # Quy đổi từ ly giác sang độ: 1 ly giác = 0.05625 độ
        angle_degrees = angle_mils * 0.05625
        return angle_degrees
    
    def interpolate_z(self, target_range: float) -> float:
        """Nội suy giá trị Z cho một khoảng cách."""
        return self._interpolate_value(target_range, self.z_data)
    
    def interpolate_delta_zwhz(self, target_range: float) -> float:
        """Nội suy lượng sửa Z do gió hướng Z (ly giác)."""
        return self._interpolate_value(target_range, self.delta_zwhz)
    
    def interpolate_delta_zwbez(self, target_range: float) -> float:
        """Nội suy lượng sửa Z do gió bên Z (ly giác)."""
        return self._interpolate_value(target_range, self.delta_zwbez)
    
    def interpolate_delta_zwhx(self, target_range: float) -> float:
        """Nội suy lượng sửa Z do gió hướng X (ly giác)."""
        return self._interpolate_value(target_range, self.delta_zwhx)
    
    def interpolate_delta_zwbe(self, target_range: float) -> float:
        """Nội suy lượng sửa Z do gió bên (ly giác)."""
        return self._interpolate_value(target_range, self.delta_zwbe)
    
    def interpolate_delta_xwhx(self, target_range: float) -> float:
        """Nội suy lượng sửa X do gió hướng X (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xwhx)
    
    def interpolate_delta_xwhz(self, target_range: float) -> float:
        """Nội suy lượng sửa X do gió hướng Z (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xwhz)
    
    def interpolate_delta_xwbex(self, target_range: float) -> float:
        """Nội suy lượng sửa X do gió bên X (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xwbex)
    
    def interpolate_delta_xkacn(self, target_range: float) -> float:
        """Nội suy lượng sửa X do không khí chuyển động ngang (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xkacn)
    
    def interpolate_delta_xh(self, target_range: float) -> float:
        """Nội suy lượng sửa X do độ cao (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xh)
    
    def interpolate_delta_xt(self, target_range: float) -> float:
        """Nội suy lượng sửa X do nhiệt độ (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xt)
    
    def interpolate_delta_xtsz(self, target_range: float) -> float:
        """Nội suy lượng sửa X do nhiệt độ liều sử dụng (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xtsz)
    
    def interpolate_delta_xtbic(self, target_range: float) -> float:
        """Nội suy lượng sửa X do nhiệt độ bi có (ly giác)."""
        return self._interpolate_value(target_range, self.delta_xtbic)


def load_firing_table(csv_path: str = "table1.csv"):
    """Đọc bảng bắn từ file CSV và tạo interpolator.
    
    Args:
        csv_path: Đường dẫn đến file CSV (mặc định: "table1.csv")
        
    Returns:
        FiringTableInterpolator instance hoặc None nếu lỗi
    """
    try:
        # Đọc file CSV
        full_path = resource_path(csv_path)
        df = pd.read_csv(full_path)
        
        # Kiểm tra các cột cần thiết (X là khoảng cách, P là góc tầm)
        if 'X' not in df.columns or 'P' not in df.columns:
            raise ValueError("File CSV phải có cột 'X' và 'P'")
        
        # Chuyển đổi sang numpy array (X là range, P là angle)
        range_data = df['X'].values
        angle_data = df['P'].values
        
        # Đọc các cột lượng sửa (nếu có trong file CSV)
        z_data = df['Z'].values if 'Z' in df.columns else None
        delta_zwhz = df['delta_Zwhz'].values if 'delta_Zwhz' in df.columns else None
        delta_zwbez = df['delta_Zwbez'].values if 'delta_Zwbez' in df.columns else None
        delta_zwhx = df['delta_Zwhx'].values if 'delta_Zwhx' in df.columns else None
        delta_zwbe = df['delta_Zwbe'].values if 'delta_Zwbe' in df.columns else None
        delta_xwhx = df['delta_Xwhx'].values if 'delta_Xwhx' in df.columns else None
        delta_xwhz = df['delta_Xwhz'].values if 'delta_Xwhz' in df.columns else None
        delta_xwbex = df['delta_Xwbex'].values if 'delta_Xwbex' in df.columns else None
        delta_xkacn = df['delta_Xkacn'].values if 'delta_Xkacn' in df.columns else None
        delta_xh = df['delta_XH'].values if 'delta_XH' in df.columns else None
        delta_xt = df['delta_XT'].values if 'delta_XT' in df.columns else None
        delta_xtsz = df['delta_XTsz'].values if 'delta_XTsz' in df.columns else None
        delta_xtbic = df['delta_XTbic'].values if 'delta_XTbic' in df.columns else None
        
        # Đếm số cột lượng sửa đã load
        delta_columns_loaded = sum([
            z_data is not None,
            delta_zwhz is not None,
            delta_zwbez is not None,
            delta_zwhx is not None,
            delta_zwbe is not None,
            delta_xwhx is not None,
            delta_xwhz is not None,
            delta_xwbex is not None,
            delta_xkacn is not None,
            delta_xh is not None,
            delta_xt is not None,
            delta_xtsz is not None,
            delta_xtbic is not None
        ])
        
        return FiringTableInterpolator(
            ranges=range_data,
            angles=angle_data,
            z_data=z_data,
            delta_zwhz=delta_zwhz,
            delta_zwbez=delta_zwbez,
            delta_zwhx=delta_zwhx,
            delta_zwbe=delta_zwbe,
            delta_xwhx=delta_xwhx,
            delta_xwhz=delta_xwhz,
            delta_xwbex=delta_xwbex,
            delta_xkacn=delta_xkacn,
            delta_xh=delta_xh,
            delta_xt=delta_xt,
            delta_xtsz=delta_xtsz,
            delta_xtbic=delta_xtbic
        )
        
    except FileNotFoundError:
        print(f"Không tìm thấy file {csv_path}")
        return None
    except Exception as e:
        print(f"Lỗi đọc file CSV: {e}")
        return None


# Khởi tạo interpolator global để dùng chung
_firing_table_interpolator = None


def get_firing_table_interpolator():
    """Lấy hoặc tạo interpolator singleton."""
    global _firing_table_interpolator
    if _firing_table_interpolator is None:
        _firing_table_interpolator = load_firing_table()
    return _firing_table_interpolator


class SlopeCorrection2DTable:
    """Bảng tra 2D cho lượng sửa chênh tà (P).
    
    Tra cứu dựa trên:
    - Góc tà (góc tạ mục tiêu) - theo hàng
    - Ly giác hiện tại (góc tầm) - theo cột
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Khởi tạo bảng tra 2D.
        
        Args:
            df: DataFrame với cột đầu tiên là góc tà, các cột còn lại là ly giác
        """
        self.df = df
        
        # Lấy tên cột đầu tiên làm index (góc tà)
        self.slope_angle_col = df.columns[0]
        
        # Các cột còn lại là ly giác (góc tầm)
        self.elevation_cols = [col for col in df.columns if col != self.slope_angle_col]
        
        # Chuyển các tên cột ly giác thành số
        try:
            self.elevation_values = np.array([float(col) for col in self.elevation_cols])
        except ValueError:
            raise ValueError("Tên cột phải là số (ly giác)")
        
        # Lấy các giá trị góc tà
        self.slope_angles = df[self.slope_angle_col].values
        
        print(f"Đã load bảng tra 2D: {len(self.slope_angles)} góc tà × {len(self.elevation_values)} ly giác")
    
    def lookup(self, slope_angle: float, current_elevation_mils: float) -> float:
        """
        Tra cứu giá trị P (chênh tà) từ bảng 2D.
        
        Args:
            slope_angle: Góc tà mục tiêu (độ)
            current_elevation_mils: Ly giác hiện tại (ly giác)
            
        Returns:
            Giá trị P (chênh tà) - đơn vị ly giác
        """
        # Tìm hàng gần nhất với góc tà
        slope_idx = np.argmin(np.abs(self.slope_angles - slope_angle))
        
        # Tìm cột gần nhất với ly giác hiện tại
        elev_idx = np.argmin(np.abs(self.elevation_values - current_elevation_mils))
        
        # Lấy tên cột tương ứng
        col_name = self.elevation_cols[elev_idx]
        
        # Tra giá trị
        value = self.df.iloc[slope_idx][col_name]
        
        return float(value)
    
    def interpolate(self, slope_angle: float, current_elevation_mils: float) -> float:
        """
        Nội suy 2D giá trị P (chênh tà) từ bảng.
        
        Args:
            slope_angle: Góc tà mục tiêu (độ)
            current_elevation_mils: Ly giác hiện tại (ly giác)
            
        Returns:
            Giá trị P (chênh tà) nội suy - đơn vị ly giác
        """
        from scipy.interpolate import interp2d
        
        # Tạo lưới dữ liệu
        data_matrix = self.df[self.elevation_cols].values
        
        # Tạo hàm nội suy 2D
        f = interp2d(self.elevation_values, self.slope_angles, data_matrix, kind='linear')
        
        # Nội suy
        result = f(current_elevation_mils, slope_angle)
        
        return float(result[0])


def load_slope_correction_table(csv_path: str = "table2.csv"):
    """Đọc bảng tra chênh tà từ file CSV.
    
    Args:
        csv_path: Đường dẫn đến file CSV (mặc định: "table2.csv")
        
    Returns:
        SlopeCorrection2DTable instance hoặc None nếu lỗi
    """
    try:
        # Đọc file CSV
        full_path = resource_path(csv_path)
        df = pd.read_csv(full_path)
        
        if len(df.columns) < 2:
            raise ValueError("File CSV phải có ít nhất 2 cột (góc tà + ly giác)")
        
        print(f"Đã đọc bảng tra chênh tà từ {csv_path}")
        return SlopeCorrection2DTable(df)
        
    except FileNotFoundError:
        print(f"Không tìm thấy file {csv_path}")
        return None
    except Exception as e:
        print(f"Lỗi đọc file CSV: {e}")
        return None


# Khởi tạo bảng tra chênh tà global
_slope_correction_table = None


def get_slope_correction_table():
    """Lấy hoặc tạo bảng tra chênh tà singleton."""
    global _slope_correction_table
    if _slope_correction_table is None:
        _slope_correction_table = load_slope_correction_table()
    return _slope_correction_table