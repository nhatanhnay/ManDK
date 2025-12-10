# Jetson3 - Quang Điện Tử Webhook Sender

Code để gửi dữ liệu khoảng cách và hướng từ Jetson3 (quang điện tử) về Jetson1.

## 📋 Chức năng

Jetson3 chịu trách nhiệm:

- Đo khoảng cách đến mục tiêu từ quang điện tử
- Đo góc hướng (azimuth) đến mục tiêu
- Gửi dữ liệu về Jetson1 qua HTTP webhook

## 📁 File cần thiết

Sao chép 2 file sau vào Jetson3:

1. **data_sender_jetson3.py** - Code gửi dữ liệu (file này)
2. **webhook_config.py** - Cấu hình (copy từ `communication/webhook_config.py`)

## 🚀 Cài đặt

```bash
# Cài đặt dependencies
pip3 install requests

# Kiểm tra kết nối mạng đến Jetson1
ping <JETSON1_IP>

# Mở firewall nếu cần
sudo ufw status
```

## ⚙️ Cấu hình

Sửa IP của Jetson1 trong file này:

```python
JETSON1_HOST = "192.168.1.101"  # ← Thay bằng IP thực tế của Jetson1
JETSON1_PORT = 5001
```

## 📡 API

### send_distance(distance)

Gửi khoảng cách đến mục tiêu (meters)

```python
from data_sender_jetson3 import send_distance

# Gửi khoảng cách 1500.5m
send_distance(1500.5)
```

### send_direction(direction)

Gửi góc hướng đến mục tiêu (degrees, 0-360)

```python
from data_sender_jetson3 import send_direction

# Gửi hướng 45.8°
send_direction(45.8)
```

## 🧪 Test

```bash
# Chạy test để gửi dữ liệu mẫu
python3 data_sender_jetson3.py
```

## 🔄 Tích hợp với phần cứng quang điện tử

Ví dụ code tích hợp:

```python
from data_sender_jetson3 import send_distance, send_direction
import time

# Giả sử bạn có hàm đọc từ quang điện tử
def read_optoelectronic():
    # TODO: Thay bằng code đọc thực tế từ quang điện tử
    distance = read_distance_sensor()  # meters
    direction = read_azimuth_sensor()   # degrees
    return distance, direction

# Main loop
while True:
    try:
        distance, direction = read_optoelectronic()

        # Gửi về Jetson1
        send_distance(distance)
        time.sleep(0.1)  # Delay nhỏ giữa 2 request
        send_direction(direction)

        print(f"Sent: Distance={distance:.1f}m, Direction={direction:.1f}°")

        # Gửi mỗi 100ms (10 Hz)
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)  # Đợi 1s nếu có lỗi
```

## 🔧 Khởi động tự động với systemd

Tạo file `/etc/systemd/system/jetson3-sender.service`:

```ini
[Unit]
Description=Jetson3 Optoelectronic Data Sender
After=network.target

[Service]
Type=simple
User=jetson
WorkingDirectory=/path/to/your/code
ExecStart=/usr/bin/python3 /path/to/your/code/optoelectronic_loop.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable và start:

```bash
sudo systemctl enable jetson3-sender.service
sudo systemctl start jetson3-sender.service
sudo systemctl status jetson3-sender.service
```

## 📊 Monitoring

Xem logs:

```bash
sudo journalctl -u jetson3-sender.service -f
```

## ⚠️ Lưu ý

- Đảm bảo mạng giữa Jetson3 và Jetson1 ổn định
- Nên gửi dữ liệu với tần suất hợp lý (5-10 Hz)
- Có retry mechanism khi gửi thất bại
- Kiểm tra kết nối trước khi gửi liên tục

## 🔒 Security (Optional)

Nếu cần bảo mật, thêm API key:

```python
headers = {"X-API-Key": "your-secret-key"}
response = requests.post(url, json=payload, headers=headers)
```

---

**Xem thêm:** `WEBHOOK_MIGRATION_GUIDE.md` trong thư mục gốc
