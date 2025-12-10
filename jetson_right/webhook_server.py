# -*- coding: utf-8 -*-
"""
Jetson Right Webhook Server
============================
Server webhook chạy trên Jetson Right (Pháo phải) để nhận lệnh từ Jetson1.
Server này xử lý các lệnh phóng đạn và điều khiển góc pháo PHẢI.
"""

from flask import Flask, request, jsonify
import logging
import sys
import can_sender  # Import CAN sender để gửi lệnh xuống CAN bus
import can_receiver  # Import CAN receiver để nhận trạng thái đạn

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/jetson_right_webhook.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__)

# =============================================================================
# Mock Hardware Interface (thay thế bằng code thực tế điều khiển phần cứng)
# =============================================================================

class HardwareController:
    """
    Interface để điều khiển phần cứng pháo PHẢI.
    THAY THẾ các hàm mock này bằng code thực tế điều khiển phần cứng.
    """
    
    @staticmethod
    def launch_ammunition(idx, flag1, flag2, flag3, positions):
        """
        Thực hiện lệnh phóng đạn cho pháo PHẢI - Gửi xuống CAN bus.
        
        Args:
            idx: Index của lệnh
            flag1, flag2, flag3: Bit flags cho 18 vị trí
            positions: List các vị trí cần phóng
        
        Returns:
            bool: True nếu thành công
        """
        try:
            logger.info(f"[HARDWARE RIGHT] Lệnh phóng đạn - idx={idx}, positions={positions}")
            logger.info(f"[HARDWARE RIGHT] Flags: {flag1:08b} {flag2:08b} {flag3:08b}")
            
            # Gửi lệnh xuống CAN bus
            success = can_sender.send_launch_command(idx, positions)
            
            if success:
                logger.info(f"[HARDWARE RIGHT] ✅ Đã gửi lệnh phóng xuống CAN bus")
            else:
                logger.error(f"[HARDWARE RIGHT] ❌ Lỗi gửi lệnh phóng xuống CAN bus")
            
            return success
            
        except Exception as e:
            logger.error(f"[HARDWARE RIGHT] Lỗi khi phóng đạn: {e}")
            return False
    
    @staticmethod
    def set_cannon_angle(angle, direction):
        """
        Điều khiển góc pháo PHẢI.
        
        Args:
            angle: Góc tầm (đơn vị 0.1 độ)
            direction: Hướng (đơn vị 0.1 độ)
        
        Returns:
            bool: True nếu thành công
        """
        try:
            # TODO: Thay thế bằng code thực tế điều khiển servo/motor pháo phải
            angle_deg = angle / 10.0
            direction_deg = direction / 10.0
            logger.info(f"[HARDWARE RIGHT] Điều khiển pháo PHẢI - Góc: {angle_deg:.1f}°, Hướng: {direction_deg:.1f}°")
            
            return True
            
        except Exception as e:
            logger.error(f"[HARDWARE RIGHT] Lỗi khi điều khiển pháo: {e}")
            return False


# =============================================================================
# Webhook Endpoints
# =============================================================================

@app.route('/api/launch', methods=['POST'])
def handle_launch_command():
    """
    Nhận lệnh phóng đạn từ Jetson1.
    
    Payload JSON:
    {
        "idx": int,
        "flag1": int,
        "flag2": int,
        "flag3": int,
        "positions": [int, ...]
    }
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        idx = data.get('idx')
        flag1 = data.get('flag1')
        flag2 = data.get('flag2')
        flag3 = data.get('flag3')
        positions = data.get('positions', [])
        
        if idx is None or flag1 is None or flag2 is None or flag3 is None:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        logger.info(f"[API] Nhận lệnh phóng - idx={idx}, positions={positions}")
        
        # Thực hiện lệnh phóng
        success = HardwareController.launch_ammunition(idx, flag1, flag2, flag3, positions)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Launch command executed",
                "idx": idx,
                "positions": positions,
                "side": "right"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to execute launch command"
            }), 500
            
    except Exception as e:
        logger.error(f"[API] Lỗi xử lý lệnh phóng: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/angle', methods=['POST'])
def handle_angle():
    """
    Nhận lệnh điều khiển góc pháo PHẢI từ Jetson1.
    
    Payload JSON:
    {
        "angle": int (đơn vị 0.1 độ),
        "direction": int (đơn vị 0.1 độ),
        "angle_degrees": float (optional),
        "direction_degrees": float (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        angle = data.get('angle')
        direction = data.get('direction')
        
        if angle is None or direction is None:
            return jsonify({"status": "error", "message": "Missing angle or direction"}), 400
        
        logger.info(f"[API] Nhận lệnh góc pháo PHẢI - Góc: {angle/10:.1f}°, Hướng: {direction/10:.1f}°")
        
        # Điều khiển pháo phải
        success = HardwareController.set_cannon_angle(angle, direction)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Cannon angle set",
                "angle": angle,
                "direction": direction,
                "side": "right"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to set cannon angle"
            }), 500
            
    except Exception as e:
        logger.error(f"[API] Lỗi xử lý góc pháo: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Jetson Right Webhook Server",
        "side": "right"
    }), 200


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Jetson Right Webhook Server Starting...")
    logger.info("=" * 60)
    
    # Khởi động CAN receiver để nhận trạng thái đạn
    logger.info("Khởi động CAN receiver...")
    can_receiver.start_can_receiver()
    logger.info("✅ CAN receiver đã khởi động")
    
    # Chạy server trên port 5000, listen trên tất cả các network interface
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set False trong production
        threaded=True  # Cho phép xử lý nhiều request cùng lúc
    )
