#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script cho Webhook API
============================
Script test tất cả các endpoint của webhook system.
"""

import requests
import json
import time
import sys

# Cấu hình
JETSON1_URL = "http://172.18.254.230:5001"
JETSON_LEFT_URL = "http://192.0.0.101:5000"
JETSON_RIGHT_URL = "http://192.0.0.102:5000"
TIMEOUT = 5

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """In header với màu sắc"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(test_name):
    """In tên test"""
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 Test: {test_name}{Colors.RESET}")

def print_success(message):
    """In thông báo thành công"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """In thông báo lỗi"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    """In cảnh báo"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message):
    """In thông tin"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")

def print_json(data):
    """In JSON với format đẹp"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


# =============================================================================
# Test Functions - Jetson1 Endpoints
# =============================================================================

def test_target_endpoint():
    """Test endpoint nhận dữ liệu mục tiêu từ Jetson3"""
    print_test("POST /api/target - Nhận dữ liệu mục tiêu (distance + direction)")
    
    test_cases = [
        {"distance": 1500.5, "direction": 45.0, "desc": "Mục tiêu ở 1500m, 45°"},
        {"distance": 2000.0, "direction": 90.0, "desc": "Mục tiêu ở 2000m, 90°"},
        {"distance": 800.0, "direction": 180.0, "desc": "Mục tiêu ở 800m, 180°"},
        {"distance": 3000.0, "direction": 270.0, "desc": "Mục tiêu ở 3000m, 270°"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  {Colors.YELLOW}Case {i}: {test['desc']}{Colors.RESET}")
        try:
            payload = {
                "distance": test["distance"],
                "direction": test["direction"]
            }
            response = requests.post(
                f"{JETSON1_URL}/api/target",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Response: {response.status_code}")
                print_info("Kết quả tính toán:")
                print_json(data)
            else:
                print_error(f"Response: {response.status_code}")
                print_json(response.json())
                
        except requests.exceptions.ConnectionError:
            print_error(f"Không thể kết nối đến {JETSON1_URL}")
            print_warning("Đảm bảo webhook_receiver đang chạy trên Jetson1")
            return False
        except Exception as e:
            print_error(f"Lỗi: {e}")
            return False
    
    return True


def test_ammo_status_endpoint():
    """Test endpoint nhận trạng thái đạn từ Jetson Left/Right"""
    print_test("POST /api/ammo/status - Nhận trạng thái đạn")
    
    test_cases = [
        {
            "side_code": 0x01,  # Left
            "ammo_status": [True, True, True, False, False, True, True, True,
                          True, False, True, True, True, True, False, True,
                          True, True],
            "desc": "Giàn trái - 15/18 viên sẵn sàng"
        },
        {
            "side_code": 0x02,  # Right
            "ammo_status": [True, True, True, True, True, True, True, True,
                          True, True, True, True, True, True, True, True,
                          False, False],
            "desc": "Giàn phải - 16/18 viên sẵn sàng"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  {Colors.YELLOW}Case {i}: {test['desc']}{Colors.RESET}")
        try:
            payload = {
                "side_code": test["side_code"],
                "ammo_status": test["ammo_status"]
            }
            response = requests.post(
                f"{JETSON1_URL}/api/ammo/status",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Response: {response.status_code}")
                print_json(data)
            else:
                print_error(f"Response: {response.status_code}")
                print_json(response.json())
                
        except requests.exceptions.ConnectionError:
            print_error(f"Không thể kết nối đến {JETSON1_URL}")
            return False
        except Exception as e:
            print_error(f"Lỗi: {e}")
            return False
    
    return True


def test_cannon_position_endpoint():
    """Test endpoint nhận vị trí pháo hiện tại"""
    print_test("POST /api/cannon/left và /api/cannon/right - Nhận vị trí pháo")
    
    test_cases = [
        {
            "endpoint": "/api/cannon/left",
            "angle": 25.5,
            "direction": 45.0,
            "desc": "Pháo trái - Góc 25.5°, Hướng 45°"
        },
        {
            "endpoint": "/api/cannon/right",
            "angle": 30.0,
            "direction": 50.0,
            "desc": "Pháo phải - Góc 30°, Hướng 50°"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  {Colors.YELLOW}Case {i}: {test['desc']}{Colors.RESET}")
        try:
            payload = {
                "angle": test["angle"],
                "direction": test["direction"]
            }
            response = requests.post(
                f"{JETSON1_URL}{test['endpoint']}",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Response: {response.status_code}")
                print_json(data)
            else:
                print_error(f"Response: {response.status_code}")
                print_json(response.json())
                
        except requests.exceptions.ConnectionError:
            print_error(f"Không thể kết nối đến {JETSON1_URL}")
            return False
        except Exception as e:
            print_error(f"Lỗi: {e}")
            return False
    
    return True


# =============================================================================
# Test Functions - Jetson Left/Right Endpoints
# =============================================================================

def test_launch_endpoint(url, side_name):
    """Test endpoint phóng đạn"""
    print_test(f"POST /api/launch - Gửi lệnh phóng ({side_name})")
    
    test_cases = [
        {
            "cannon_index": 0,
            "positions": [0, 1, 2],
            "desc": f"Phóng 3 viên đầu tiên từ {side_name}"
        },
        {
            "cannon_index": 0,
            "positions": [5, 10, 15],
            "desc": f"Phóng 3 viên (vị trí 5, 10, 15) từ {side_name}"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  {Colors.YELLOW}Case {i}: {test['desc']}{Colors.RESET}")
        try:
            payload = {
                "cannon_index": test["cannon_index"],
                "positions": test["positions"]
            }
            response = requests.post(
                f"{url}/api/launch",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Response: {response.status_code}")
                print_json(data)
            else:
                print_error(f"Response: {response.status_code}")
                print_json(response.json())
                
        except requests.exceptions.ConnectionError:
            print_error(f"Không thể kết nối đến {url}")
            print_warning(f"Đảm bảo webhook_server đang chạy trên {side_name}")
            return False
        except Exception as e:
            print_error(f"Lỗi: {e}")
            return False
    
    return True


# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests():
    """Chạy tất cả các test"""
    print_header("WEBHOOK API TEST SUITE")
    
    results = {}
    
    # Test Jetson1 endpoints
    print_header("JETSON1 ENDPOINTS (Receiver)")
    
    print_info(f"Target URL: {JETSON1_URL}")
    results['target'] = test_target_endpoint()
    time.sleep(1)
    
    results['ammo_status'] = test_ammo_status_endpoint()
    time.sleep(1)
    
    results['cannon_position'] = test_cannon_position_endpoint()
    time.sleep(1)
    
    # Test Jetson Left endpoints
    print_header("JETSON LEFT ENDPOINTS")
    
    print_info(f"Target URL: {JETSON_LEFT_URL}")
    results['launch_left'] = test_launch_endpoint(JETSON_LEFT_URL, "Jetson Left")
    time.sleep(1)
    
    # Test Jetson Right endpoints
    print_header("JETSON RIGHT ENDPOINTS")
    
    print_info(f"Target URL: {JETSON_RIGHT_URL}")
    results['launch_right'] = test_launch_endpoint(JETSON_RIGHT_URL, "Jetson Right")
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\n{Colors.BOLD}Tổng số test groups: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}\n")
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {test_name.ljust(20)}: {status}")
    
    print("\n" + "="*70 + "\n")
    
    return failed == 0


def test_specific_endpoint(endpoint_name):
    """Test một endpoint cụ thể"""
    tests = {
        'target': test_target_endpoint,
        'ammo': test_ammo_status_endpoint,
        'cannon': test_cannon_position_endpoint,
        'launch_left': lambda: test_launch_endpoint(JETSON_LEFT_URL, "Jetson Left"),
        'launch_right': lambda: test_launch_endpoint(JETSON_RIGHT_URL, "Jetson Right"),
    }
    
    if endpoint_name not in tests:
        print_error(f"Không tìm thấy test cho endpoint: {endpoint_name}")
        print_info(f"Các endpoint có thể test: {', '.join(tests.keys())}")
        return False
    
    print_header(f"TESTING: {endpoint_name.upper()}")
    return tests[endpoint_name]()


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        success = test_specific_endpoint(endpoint)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
