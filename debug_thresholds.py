#!/usr/bin/env python3
"""
Debug script to check threshold lookup vs actual parameter values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_threshold_checking():
    """Debug threshold checking for multiple modules."""

    print("=== Debugging Threshold vs Parameter Values ===\n")

    from data_management.module_data_manager import module_manager
    from data_management.module_threshold_manager import (
        get_threshold_for_parameter,
        is_parameter_normal,
        DEFAULT_THRESHOLDS,
        MODULE_TYPE_THRESHOLDS
    )

    print(f"DEFAULT_THRESHOLDS: {DEFAULT_THRESHOLDS}")
    print(f"MODULE_TYPE_THRESHOLDS: {MODULE_TYPE_THRESHOLDS}")
    print()

    # Check first few modules
    checked_count = 0
    for node_id, node_modules in module_manager.modules.items():
        if checked_count >= 3:  # Only check first 3 modules
            break

        for module_id, module in node_modules.items():
            if checked_count >= 3:
                break

            print(f"=== Module: {module.name} in {node_id} ===")
            print(f"Status: {module.status}")
            print(f"Errors: {module.error_messages}")

            # Check each parameter
            parameters = [
                ("Điện áp", module.parameters.voltage, "V"),
                ("Dòng điện", module.parameters.current, "A"),
                ("Công suất", module.parameters.power, "W"),
                ("Điện trở", module.parameters.resistance, "Ω")
            ]

            for param_name, value, unit in parameters:
                threshold = get_threshold_for_parameter(module.name, param_name)
                is_normal = is_parameter_normal(module.name, param_name, value)

                min_val = threshold['min_normal']
                max_val = threshold['max_normal']

                status = "✅ NORMAL" if is_normal else "❌ ERROR"

                print(f"  {param_name}: {value}{unit}")
                print(f"    Threshold: {min_val}-{max_val}{unit}")
                print(f"    Within range? {min_val} <= {value} <= {max_val} = {status}")
                print(f"    is_parameter_normal() = {is_normal}")

                # Manual check
                manual_check = min_val <= value <= max_val
                if manual_check != is_normal:
                    print(f"    🚨 MISMATCH: Manual check={manual_check}, is_parameter_normal={is_normal}")
                print()

            print("-" * 50)
            checked_count += 1

    return True

if __name__ == "__main__":
    debug_threshold_checking()