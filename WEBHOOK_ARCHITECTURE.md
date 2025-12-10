# System Architecture - Webhook Communication

## 🏗️ Kiến trúc Hệ thống (4 Jetsons)

```
┌─────────────────────────────────────────────────────────────────┐
│                         JETSON 1                                │
│                    (Control Center)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PyQt5 GUI (main.py)                                     │  │
│  │  - Main Control Tab                                      │  │
│  │  - Ballistic Calculator                                  │  │
│  │  - Event Log                                             │  │
│  │  - System Info                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↕                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Webhook System                                          │  │
│  │  • webhook_receiver.py (Flask :5001)                     │  │
│  │    - Nhận từ Jetson Left/Right/3                         │  │
│  │  • webhook_sender.py                                     │  │
│  │    - Gửi đến Jetson Left/Right                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           ↑ HTTP ↓              ↑ HTTP ↓              ↑ HTTP ↓

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  JETSON LEFT     │    │  JETSON RIGHT    │    │  JETSON 3        │
│  (Pháo Trái)     │    │  (Pháo Phải)     │    │  (Quang điện tử) │
│  192.168.1.102   │    │  192.168.1.103   │    │  192.168.1.104   │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ Webhook Server   │    │ Webhook Server   │    │ Data Sender Only │
│ (Flask :5000)    │    │ (Flask :5000)    │    │                  │
│                  │    │                  │    │ • distance       │
│ Endpoints:       │    │ Endpoints:       │    │ • direction      │
│ • /api/launch    │    │ • /api/launch    │    │                  │
│ • /api/angle     │    │ • /api/angle     │    │ Mock hoặc:       │
│ • /health        │    │ • /health        │    │ • Serial port    │
├──────────────────┤    ├──────────────────┤    │ • I2C/SPI        │
│ Data Sender      │    │ Data Sender      │    │ • GPIO           │
│ • ammo_status    │    │ • ammo_status    │    └──────────────────┘
│ • cannon_angle   │    │ • cannon_angle   │
│ • module_data    │    │ • module_data    │
├──────────────────┤    ├──────────────────┤
│ CAN Bus Handler  │    │ CAN Bus Handler  │
│ • can_receiver   │    │ • can_receiver   │
│ • can_sender     │    │ • can_sender     │
│      ↕ CAN       │    │      ↕ CAN       │
│ ┌──────────────┐ │    │ ┌──────────────┐ │
│ │ Mạch phần    │ │    │ │ Mạch phần    │ │
│ │ cứng pháo    │ │    │ │ cứng pháo    │ │
│ │ trái         │ │    │ │ phải         │ │
│ └──────────────┘ │    │ └──────────────┘ │
└──────────────────┘    └──────────────────┘
```

## 📡 Communication Protocols

### 1️⃣ **Jetson1 ↔ Jetson Left/Right** (WEBHOOK)

#### Jetson1 → Jetson Left/Right

```
POST http://192.168.1.102:5000/api/launch
POST http://192.168.1.103:5000/api/launch

Body: {
  "idx": 1,
  "flag1": 255,
  "flag2": 0,
  "flag3": 0,
  "positions": [1, 2, 3, 4, 5, 6, 7, 8]
}
```

```
POST http://192.168.1.102:5000/api/angle
POST http://192.168.1.103:5000/api/angle

Body: {
  "angle": 450,          // 45.0° (đơn vị 0.1°)
  "direction": 900,      // 90.0°
  "angle_degrees": 45.0,
  "direction_degrees": 90.0
}
```

#### Jetson Left/Right → Jetson1

```
POST http://192.168.1.101:5001/api/cannon/left
POST http://192.168.1.101:5001/api/cannon/right

Body: {
  "angle": 45.5,
  "direction": 90.0
}
```

```
POST http://192.168.1.101:5001/api/ammo/status

Body: {
  "side_code": 1,  // 1=Left, 2=Right
  "flags": [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0]
}
```

```
POST http://192.168.1.101:5001/api/module/data

Body: {
  "node_id": "bang_dien_trai",
  "module_index": 0,
  "voltage": 48.5,
  "current": 10.2,
  "power": 494.7,
  "temperature": 35.0
}
```

### 2️⃣ **Jetson1 ↔ Jetson3** (WEBHOOK)

#### Jetson3 → Jetson1

```
POST http://192.168.1.101:5001/api/distance

Body: {
  "distance": 1500.5  // meters
}
```

```
POST http://192.168.1.101:5001/api/direction

Body: {
  "direction": 45.8  // degrees (0-360)
}
```

### 3️⃣ **Jetson Left/Right ↔ Mạch phần cứng** (CAN BUS)

#### Jetson → Mạch (Launch Command)

```
CAN ID: 0x100
Data: [0xAA, idx, flag1, flag2, flag3, 0x55]

Example: AA 01 FF 00 00 55
         │  │  │  │  │  └── END marker
         │  │  │  │  └──── Flag3 (bits 17-18)
         │  │  │  └─────── Flag2 (bits 9-16)
         │  │  └────────── Flag1 (bits 1-8)
         │  └───────────── Message index
         └──────────────── START marker
```

#### Mạch → Jetson (Ammo Status)

```
CAN ID: 0x300
Data: [0xAA, side_code, flag1, flag2, flag3, 0x55]

Example: AA 01 FF 00 00 55
         │  │  │  │  │  └── END marker
         │  │  │  │  └──── Flag3 (bits 17-18)
         │  │  │  └─────── Flag2 (bits 9-16)
         │  │  └────────── Flag1 (bits 1-8)
         │  └───────────── Side code (01=Left, 02=Right)
         └──────────────── START marker
```

## 🔄 Data Flow Examples

### Example 1: Phóng đạn

```
[User clicks "Fire" in Jetson1 GUI]
          ↓
[webhook_sender.sender_ammo_status(idx, [1,2,3], is_left=True)]
          ↓
[HTTP POST → http://192.168.1.102:5000/api/launch]
          ↓
[Jetson Left: webhook_server receives request]
          ↓
[can_sender.send_launch_command(idx, [1,2,3])]
          ↓
[CAN Bus: 0x100 → AA 01 07 00 00 55]
          ↓
[Mạch phần cứng thực hiện phóng đạn 1, 2, 3]
```

### Example 2: Cập nhật trạng thái đạn

```
[Mạch phần cứng detect đạn đã bắn]
          ↓
[CAN Bus: 0x300 → AA 01 F8 00 00 55]  (5 đạn còn lại)
          ↓
[Jetson Left: can_receiver detects message]
          ↓
[Parse flags → [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0]]
          ↓
[data_sender.send_ammo_status(flags)]
          ↓
[HTTP POST → http://192.168.1.101:5001/api/ammo/status]
          ↓
[Jetson1: webhook_receiver updates config.AMMO_L]
          ↓
[GUI updates ammunition widget display]
```

### Example 3: Phát hiện mục tiêu

```
[Jetson3 reads optoelectronic sensor]
          ↓
[data_sender_jetson3.send_distance(1500.5)]
[data_sender_jetson3.send_direction(45.8)]
          ↓
[HTTP POST → http://192.168.1.101:5001/api/distance]
[HTTP POST → http://192.168.1.101:5001/api/direction]
          ↓
[Jetson1: webhook_receiver updates config.W_DISTANCE, config.W_DIRECTION]
          ↓
[Targeting system calculates firing solution]
          ↓
[GUI displays target info and suggested angles]
```

## 🔧 Configuration Files

### Jetson1

- `communication/webhook_config.py` - Central config cho tất cả endpoints
- `communication/webhook_receiver.py` - Flask server (:5001)
- `communication/webhook_sender.py` - HTTP client gửi lệnh

### Jetson Left

- `jetson_left/webhook_server.py` - Flask server (:5000)
- `jetson_left/data_sender.py` - HTTP client gửi data
- `jetson_left/can_receiver.py` - CAN receiver thread
- `jetson_left/can_sender.py` - CAN sender

### Jetson Right

- `jetson_right/webhook_server.py` - Flask server (:5000)
- `jetson_right/data_sender.py` - HTTP client gửi data
- `jetson_right/can_receiver.py` - CAN receiver thread
- `jetson_right/can_sender.py` - CAN sender

### Jetson3

- `jetson3/data_sender_jetson3.py` - HTTP client gửi distance/direction

## 🌐 Network Configuration

| Jetson | IP Address    | Webhook Port | Role                 |
| ------ | ------------- | ------------ | -------------------- |
| 1      | 192.168.1.101 | 5001         | Control Center       |
| Left   | 192.168.1.102 | 5000         | Cannon Control Left  |
| Right  | 192.168.1.103 | 5000         | Cannon Control Right |
| 3      | 192.168.1.104 | N/A          | Optoelectronics      |

## 🚀 Startup Sequence

### Jetson1

```bash
cd /home/na/Projects/ManDK
python3 main.py
# Automatically starts webhook_receiver in background
```

### Jetson Left

```bash
cd /home/na/Projects/ManDK/jetson_left
./start_jetson_left.sh
# Or manually:
python3 webhook_server.py
# Automatically starts can_receiver in background
```

### Jetson Right

```bash
cd /home/na/Projects/ManDK/jetson_right
./start_jetson_right.sh
# Or manually:
python3 webhook_server.py
# Automatically starts can_receiver in background
```

### Jetson3

```bash
cd /home/na/Projects/ManDK/jetson3
# One-time test:
python3 data_sender_jetson3.py

# Continuous loop (5 Hz):
python3 data_sender_jetson3.py loop
```

## 🧪 Testing

### Test Jetson1 Webhook Receiver

```bash
# Test distance endpoint
curl -X POST http://192.168.1.101:5001/api/distance \
  -H "Content-Type: application/json" \
  -d '{"distance": 1500.5}'

# Test direction endpoint
curl -X POST http://192.168.1.101:5001/api/direction \
  -H "Content-Type: application/json" \
  -d '{"direction": 45.8}'

# Test ammo status endpoint
curl -X POST http://192.168.1.101:5001/api/ammo/status \
  -H "Content-Type: application/json" \
  -d '{"side_code": 1, "flags": [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0]}'
```

### Test Jetson Left/Right Webhook Server

```bash
# Test launch endpoint (Left)
curl -X POST http://192.168.1.102:5000/api/launch \
  -H "Content-Type: application/json" \
  -d '{"idx": 1, "flag1": 255, "flag2": 0, "flag3": 0, "positions": [1,2,3]}'

# Test angle endpoint (Right)
curl -X POST http://192.168.1.103:5000/api/angle \
  -H "Content-Type: application/json" \
  -d '{"angle": 450, "direction": 900}'

# Test health check
curl http://192.168.1.102:5000/health
```

## 📊 Performance

### Network Latency

- Expected RTT (Round-Trip Time): < 10ms in LAN
- Webhook timeout: 5 seconds
- Retry mechanism: 3 attempts with 1s delay

### Data Rate

- Jetson3 → Jetson1: Up to 10 Hz (distance + direction)
- Jetson Left/Right → Jetson1: Event-driven (ammo status on change)
- Jetson1 → Jetson Left/Right: On-demand (fire commands)

### CAN Bus

- Bitrate: 500 kbps
- Message size: 6 bytes
- Frequency: Event-driven

## 🔒 Error Handling

### Webhook Communication

- Connection timeout → Retry 3 times
- HTTP error → Log and return False
- Network unreachable → Log error, continue operation

### CAN Bus

- Device not found → Log error, webhook server continues
- CAN timeout → Continue listening
- Invalid message → Skip and log warning

## 📝 Dependencies

All Jetsons need:

```bash
pip install flask requests python-can
```

## 🎯 Future Improvements

1. **WebSocket** - Real-time bidirectional communication
2. **HTTPS** - Secure communication with SSL/TLS
3. **Authentication** - API key or JWT tokens
4. **Load Balancing** - Multiple webhook receivers
5. **Message Queue** - RabbitMQ or Redis for reliability
6. **Monitoring** - Prometheus + Grafana for metrics
