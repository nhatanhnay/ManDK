# Jetson Right (Pháo Phải) - Documentation

## Mục đích

Jetson Right điều khiển phần cứng của pháo PHẢI và giao tiếp với Jetson1 qua webhook.

## Thành phần

### 1. webhook_server.py

- **Chức năng**: Flask server nhận lệnh điều khiển từ Jetson1
- **Port**: 5000
- **Endpoints**:
  - `POST /api/launch` - Phóng đạn
  - `POST /api/angle` - Điều khiển góc pháo
  - `GET /health` - Kiểm tra trạng thái

### 2. data_sender.py

- **Chức năng**: Gửi dữ liệu sensor về Jetson1
- **Gửi đến**: `http://192.168.1.101:5001`
- **Data types**:
  - Góc pháo hiện tại (angle, direction)
  - Trạng thái đạn (18 flags)
  - Module data (voltage, current, power, temperature)

## Cài đặt

### Bước 1: Dependencies

```bash
pip install flask requests
```

### Bước 2: Cấu hình IP

Chỉnh sửa IP của Jetson1 trong `data_sender.py`:

```python
JETSON1_HOST = "192.168.1.101"  # IP thực tế của Jetson1
```

### Bước 3: Kiểm tra kết nối

```bash
# Test server
python3 webhook_server.py

# Test sender (trong terminal khác)
python3 data_sender.py
```

## Chạy tự động với Systemd

### Tạo service file: /etc/systemd/system/jetson-right.service

```ini
[Unit]
Description=Jetson Right Webhook Server
After=network.target

[Service]
Type=simple
User=na
WorkingDirectory=/home/na/Projects/ManDK/jetson_right
ExecStart=/usr/bin/python3 /home/na/Projects/ManDK/jetson_right/webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable service

```bash
sudo systemctl daemon-reload
sudo systemctl enable jetson-right.service
sudo systemctl start jetson-right.service
```

### Kiểm tra status

```bash
sudo systemctl status jetson-right.service
```

## Tích hợp phần cứng

### Thay thế mock functions trong HardwareController

#### 1. Encoder cho góc pháo

Cập nhật `get_current_angle()`:

```python
def get_current_angle(self):
    # Thay thế bằng đọc encoder thực tế
    import spidev
    spi = spidev.SpiDev()
    spi.open(0, 0)
    angle_raw = spi.readbytes(2)
    return calculate_angle(angle_raw)
```

#### 2. Sensor đạn

Cập nhật `get_ammo_status()`:

```python
def get_ammo_status(self):
    # Đọc 18 sensor qua GPIO hoặc I2C
    import RPi.GPIO as GPIO
    flags = []
    for pin in AMMO_SENSOR_PINS:
        flags.append(GPIO.input(pin))
    return flags
```

#### 3. Điều khiển motor góc

Cập nhật `set_cannon_angle()`:

```python
def set_cannon_angle(self, angle, direction):
    # Điều khiển motor qua PWM hoặc CAN
    motor_controller.set_angle(angle)
    motor_controller.set_direction(direction)
```

#### 4. Điều khiển phóng đạn

Cập nhật `launch_ammunition()`:

```python
def launch_ammunition(self, idx):
    # Kích hoạt relay hoặc solenoid
    GPIO.output(FIRE_PIN[idx], GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(FIRE_PIN[idx], GPIO.LOW)
```

## API Specification

### POST /api/launch

Phóng đạn tại vị trí cụ thể.

**Request:**

```json
{
  "idx": 0
}
```

**Response:**

```json
{
  "success": true,
  "message": "Đã phóng đạn vị trí 0"
}
```

### POST /api/angle

Điều chỉnh góc pháo.

**Request:**

```json
{
  "angle": 45.5,
  "direction": 90.0
}
```

**Response:**

```json
{
  "success": true,
  "message": "Đã điều chỉnh góc pháo"
}
```

### GET /health

Kiểm tra trạng thái server.

**Response:**

```json
{
  "status": "healthy",
  "server": "Jetson Right",
  "uptime": 3600
}
```

## Troubleshooting

### Lỗi kết nối

- Kiểm tra firewall: `sudo ufw allow 5000/tcp`
- Kiểm tra IP: `ip addr show`
- Test endpoint: `curl http://localhost:5000/health`

### Lỗi gửi data về Jetson1

- Kiểm tra IP của Jetson1 trong `data_sender.py`
- Kiểm tra Jetson1 webhook_receiver đang chạy: `curl http://192.168.1.101:5001/health`
- Xem log: `sudo journalctl -u jetson-right.service -f`

### Performance tuning

- Tăng worker threads nếu cần xử lý nhiều request:

```python
app.run(host='0.0.0.0', port=5000, threaded=True)
```

## Monitoring

### Log files

```bash
# Xem log realtime
sudo journalctl -u jetson-right.service -f

# Xem log 100 dòng gần nhất
sudo journalctl -u jetson-right.service -n 100
```

### Network monitoring

```bash
# Kiểm tra port đang listen
sudo netstat -tulpn | grep 5000

# Kiểm tra traffic
sudo tcpdump -i any port 5000
```
