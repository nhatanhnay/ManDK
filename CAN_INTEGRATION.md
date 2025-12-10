# Architecture Update: CAN Integration for Jetson Left/Right

## Tổng quan thay đổi

Đã chuyển xử lý CAN bus từ **Jetson1** sang **Jetson Left** và **Jetson Right**.

## Kiến trúc mới

### Jetson1 (Control Center)

- **Nhận từ webhook:**

  - Trạng thái đạn từ Jetson Left/Right
  - Góc pháo từ Jetson Left/Right
  - Module data từ Jetson Left/Right
  - Distance/Direction từ Jetson3

- **Gửi qua webhook:**

  - Lệnh phóng đạn → Jetson Left/Right
  - Lệnh điều chỉnh góc → Jetson Left/Right

- **KHÔNG CÒN CAN BUS**

### Jetson Left (Pháo Trái)

- **Nhận từ CAN bus:**

  - Trạng thái đạn (CAN ID 0x300, side_code=0x01)

- **Gửi xuống CAN bus:**

  - Lệnh phóng đạn (CAN ID 0x100)

- **Nhận từ webhook (Jetson1):**

  - `/api/launch` - Lệnh phóng đạn
  - `/api/angle` - Lệnh điều chỉnh góc

- **Gửi qua webhook (về Jetson1):**
  - `/api/ammo/status` - Trạng thái đạn (đọc từ CAN)
  - `/api/cannon/left` - Góc hiện tại
  - `/api/module/data` - Dữ liệu module

### Jetson Right (Pháo Phải)

- **Nhận từ CAN bus:**

  - Trạng thái đạn (CAN ID 0x300, side_code=0x02)

- **Gửi xuống CAN bus:**

  - Lệnh phóng đạn (CAN ID 0x100)

- **Nhận từ webhook (Jetson1):**

  - `/api/launch` - Lệnh phóng đạn
  - `/api/angle` - Lệnh điều chỉnh góc

- **Gửi qua webhook (về Jetson1):**
  - `/api/ammo/status` - Trạng thái đạn (đọc từ CAN)
  - `/api/cannon/right` - Góc hiện tại
  - `/api/module/data` - Dữ liệu module

## Files mới

### Jetson Left

```
jetson_left/
├── can_receiver.py      # Nhận trạng thái đạn từ CAN
├── can_sender.py        # Gửi lệnh phóng xuống CAN
├── webhook_server.py    # Nhận lệnh từ Jetson1 (UPDATED)
├── data_sender.py       # Gửi data về Jetson1 (UPDATED)
└── README.md
```

### Jetson Right

```
jetson_right/
├── can_receiver.py      # Nhận trạng thái đạn từ CAN
├── can_sender.py        # Gửi lệnh phóng xuống CAN
├── webhook_server.py    # Nhận lệnh từ Jetson1 (UPDATED)
├── data_sender.py       # Gửi data về Jetson1 (UPDATED)
└── README.md
```

## Flow hoạt động

### 1. Phóng đạn

```
Jetson1 (UI)
  → webhook POST /api/launch → Jetson Left/Right
    → can_sender.send_launch_command()
      → CAN bus (ID 0x100)
        → Mạch điều khiển phần cứng
```

### 2. Trạng thái đạn

```
Mạch phần cứng
  → CAN bus (ID 0x300, side_code 0x01/0x02)
    → can_receiver.can_receiver_thread()
      → Update ammo_flags
        → data_sender.send_ammo_status()
          → webhook POST /api/ammo/status → Jetson1
            → Update ui.ui_config.AMMO_L/AMMO_R
```

### 3. Điều chỉnh góc

```
Jetson1 (UI)
  → webhook POST /api/angle → Jetson Left/Right
    → HardwareController.set_cannon_angle()
      → TODO: Điều khiển servo/motor thực tế
```

## CAN Configuration

### CAN IDs

- `0x100` - Launch command (Jetson → Mạch)
- `0x300` - Ammo status (Mạch → Jetson)

### Side Codes

- `0x01` - Left (Trái)
- `0x02` - Right (Phải)

### CAN Settings

- Channel: `can0`
- Bustype: `socketcan`
- Bitrate: `500000`

## Testing

### Test Jetson Left

```bash
cd /home/na/Projects/ManDK/jetson_left

# Test CAN receiver
python3 can_receiver.py

# Test CAN sender
python3 can_sender.py

# Test webhook server + CAN
python3 webhook_server.py
```

### Test Jetson Right

```bash
cd /home/na/Projects/ManDK/jetson_right

# Test CAN receiver
python3 can_receiver.py

# Test CAN sender
python3 can_sender.py

# Test webhook server + CAN
python3 webhook_server.py
```

## Dependencies

Cả Jetson Left và Right cần:

```bash
pip install flask requests python-can
```

## Migration Notes

### Code đã xóa khỏi Jetson1

- ❌ `communication/data_receiver.py` - Phần xử lý CAN_ID_AMMO_STATUS
- ❌ `communication/data_sender.py` - Function sender_ammo_status()

### Code di chuyển

- ✅ CAN receiver cho ammo status → `jetson_left/can_receiver.py` và `jetson_right/can_receiver.py`
- ✅ CAN sender cho launch command → `jetson_left/can_sender.py` và `jetson_right/can_sender.py`

### Code mới

- ✅ Tích hợp CAN vào webhook_server
- ✅ Tích hợp CAN vào data_sender
- ✅ Auto-start CAN receiver khi webhook server khởi động

## Debugging

### Check CAN interface

```bash
ip link show can0
candump can0
```

### Monitor logs

```bash
# Jetson Left
tail -f /var/log/jetson_left_webhook.log

# Jetson Right
tail -f /var/log/jetson_right_webhook.log
```

### Test CAN communication

```bash
# Send test CAN message
cansend can0 300#010102030405

# Monitor CAN traffic
candump -a can0
```
