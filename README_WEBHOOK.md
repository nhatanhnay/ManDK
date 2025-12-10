# Hệ thống Webhook - ManDK

## 🎯 Tổng quan

Hệ thống đã được chuyển đổi từ **CAN bus** sang **HTTP Webhook** để giao tiếp giữa:

- **Jetson1** (điều khiển - UI chính)
- **Jetson2** (phần cứng pháo - nhận lệnh và gửi dữ liệu cảm biến)
- **Jetson3** (quang điện tử - gửi khoảng cách và hướng)

## 📁 Cấu trúc file mới

```
ManDK/
├── communication/
│   ├── webhook_config.py          # ✨ Cấu hình webhook (thay can_config.py)
│   ├── webhook_sender.py          # ✨ Gửi lệnh qua HTTP (thay data_sender.py)
│   └── webhook_receiver.py        # ✨ Nhận dữ liệu qua HTTP (thay data_receiver.py)
│
├── jetson2/                        # ✨ Code cho Jetson2 (Phần cứng pháo)
│   ├── webhook_server.py          # Server nhận lệnh từ Jetson1
│   ├── data_sender_jetson2.py     # Gửi dữ liệu cảm biến về Jetson1
│   ├── start_jetson2.sh           # Script khởi động nhanh
│   └── README.md                  # Hướng dẫn chi tiết
│
├── jetson3/                        # ✨ Code cho Jetson3 (Quang điện tử)
│   ├── data_sender_jetson3.py     # Gửi khoảng cách & hướng về Jetson1
│   ├── start_jetson3.sh           # Script khởi động nhanh
│   └── README.md                  # Hướng dẫn chi tiết
│
├── start_jetson1.sh               # ✨ Script khởi động Jetson1
├── requirements.txt               # ✨ Dependencies Python
├── WEBHOOK_MIGRATION_GUIDE.md     # ✨ Hướng dẫn chi tiết
└── README_WEBHOOK.md              # File này
```

## 🚀 Khởi động nhanh

### Jetson1 (Điều khiển)

```bash
# Cài đặt dependencies (chỉ cần 1 lần)
pip3 install -r requirements.txt

# Khởi động
./start_jetson1.sh
# Hoặc:
python3 main.py
```

### Jetson2 (Phần cứng pháo)

```bash
# Cài đặt dependencies (chỉ cần 1 lần)
pip3 install flask requests

# Khởi động
cd jetson2
./start_jetson2.sh
# Hoặc:
python3 webhook_server.py
```

### Jetson3 (Quang điện tử)

```bash
# Cài đặt dependencies (chỉ cần 1 lần)
pip3 install requests

# Khởi động
cd jetson3
./start_jetson3.sh
# Hoặc:
python3 data_sender_jetson3.py
```

## ⚙️ Cấu hình

### 1. Địa chỉ IP

**Trên Jetson1** - Sửa `communication/webhook_config.py`:

```python
JETSON2_HOST = "192.168.1.100"  # ← IP của Jetson2
```

**Trên Jetson2** - Sửa `jetson2/data_sender_jetson2.py`:

```python
JETSON1_HOST = "192.168.1.101"  # ← IP của Jetson1
```

**Trên Jetson3** - Sửa `jetson3/data_sender_jetson3.py`:

```python
JETSON1_HOST = "192.168.1.101"  # ← IP của Jetson1
```

### 2. Firewall

```bash
# Trên Jetson1
sudo ufw allow 5001/tcp

# Trên Jetson2
sudo ufw allow 5000/tcp
```

## 🧪 Test kết nối

### Test từ Jetson1 → Jetson2

```bash
curl -X POST http://<JETSON2_IP>:5000/health
# Kết quả: {"status":"healthy","service":"Jetson2 Webhook Server"}
```

### Test từ Jetson2 → Jetson1

```bash
curl -X POST http://<JETSON1_IP>:5001/api/cannon/left \
  -H "Content-Type: application/json" \
  -d '{"angle": 35.5, "direction": 90.0}'
```

### Test từ Jetson3 → Jetson1

```bash
curl -X POST http://<JETSON1_IP>:5001/api/distance \
  -H "Content-Type: application/json" \
  -d '{"distance": 1234.5}'
```

### Test gửi dữ liệu mẫu

**Jetson2:**

```bash
cd jetson2
python3 data_sender_jetson2.py
```

**Jetson3:**

```bash
cd jetson3
python3 data_sender_jetson3.py
```

## 📡 Endpoints

### Jetson1 nhận (port 5001)

- `POST /api/distance` - Nhận khoảng cách từ **Jetson3** (quang điện tử)
- `POST /api/direction` - Nhận hướng từ **Jetson3** (quang điện tử)
- `POST /api/cannon/left` - Nhận góc pháo trái từ **Jetson2**
- `POST /api/cannon/right` - Nhận góc pháo phải từ **Jetson2**
- `POST /api/ammo/status` - Nhận trạng thái đạn từ **Jetson2**
- `POST /api/module/data` - Nhận dữ liệu module từ **Jetson2**

### Jetson2 nhận (port 5000)

- `POST /api/launch` - Nhận lệnh phóng đạn
- `POST /api/angle/left` - Nhận lệnh góc pháo trái
- `POST /api/angle/right` - Nhận lệnh góc pháo phải
- `GET /health` - Health check

## 🔧 Tích hợp phần cứng

Trong `jetson2/webhook_server.py`, class `HardwareController` cần được tích hợp với code điều khiển phần cứng thực tế:

```python
class HardwareController:
    @staticmethod
    def launch_ammunition(idx, flag1, flag2, flag3, positions):
        # TODO: Thêm code điều khiển relay/GPIO để phóng đạn
        pass

    @staticmethod
    def set_cannon_angle_left(angle, direction):
        # TODO: Thêm code điều khiển servo/motor pháo trái
        pass

    @staticmethod
    def set_cannon_angle_right(angle, direction):
        # TODO: Thêm code điều khiển servo/motor pháo phải
        pass
```

## 📚 Tài liệu

- **WEBHOOK_MIGRATION_GUIDE.md** - Hướng dẫn chi tiết về migration từ CAN
- **jetson2/README.md** - Hướng dẫn cài đặt và cấu hình Jetson2

## ❓ Troubleshooting

### Lỗi "Connection refused"

```bash
# Kiểm tra server có chạy không
sudo lsof -i :5000  # Jetson2
sudo lsof -i :5001  # Jetson1

# Kiểm tra firewall
sudo ufw status
```

### Lỗi "No module named 'flask'"

```bash
pip3 install flask requests
```

### Lỗi kết nối mạng

```bash
# Ping test
ping <IP_CỦA_JETSON_KIA>

# Kiểm tra IP
ip addr show
```

## 📊 So sánh CAN vs Webhook

| Tiêu chí    | CAN Bus             | Webhook                   |
| ----------- | ------------------- | ------------------------- |
| Latency     | ~1ms                | ~10-50ms                  |
| Khoảng cách | ~40m                | Không giới hạn (qua mạng) |
| Debug       | Khó                 | Dễ (curl, Postman)        |
| Hardware    | Cần CAN transceiver | Chỉ cần Ethernet/WiFi     |
| Reliability | Rất cao             | Phụ thuộc mạng            |

## ⚠️ Lưu ý

- Webhook có độ trễ cao hơn CAN (~10-50ms vs ~1ms)
- Cần mạng ổn định giữa 2 Jetson
- Nên thêm authentication trong môi trường production
- Đã có retry mechanism khi gửi thất bại

## 🔐 Security (Optional)

Để thêm authentication, có thể sử dụng API key:

```python
# Trong webhook_config.py
API_KEY = "your-secret-key-here"

# Trong webhook_sender.py
headers = {"X-API-Key": API_KEY}
response = requests.post(url, json=payload, headers=headers)

# Trong webhook_server.py
@app.before_request
def check_api_key():
    if request.headers.get('X-API-Key') != API_KEY:
        abort(401)
```

## 📝 Changelog

### v2.0.0 - Webhook Migration

- ✨ Chuyển từ CAN bus sang HTTP webhook
- ✨ Thêm retry mechanism cho requests
- ✨ Thêm logging chi tiết
- ✨ Tách riêng code Jetson1 và Jetson2
- 📚 Thêm documentation đầy đủ

---

**Cần hỗ trợ?** Xem `WEBHOOK_MIGRATION_GUIDE.md` để biết thêm chi tiết.
