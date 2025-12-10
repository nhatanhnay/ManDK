# Hướng dẫn cấu hình IP tĩnh cho các Jetson

## 🌐 Vấn đề: IP thay đổi mỗi lần khởi động

Khi Jetson sử dụng DHCP, IP có thể thay đổi mỗi lần khởi động. Để hệ thống webhook hoạt động ổn định, cần cấu hình IP tĩnh cho tất cả các Jetson.

## 📋 Bảng phân bổ IP

| Jetson | IP tĩnh        | Hostname        | Role                 |
| ------ | -------------- | --------------- | -------------------- |
| 1      | 172.18.254.230 | jetson1-control | Control Center       |
| Left   | 172.18.254.231 | jetson-left     | Cannon Control Left  |
| Right  | 172.18.254.232 | jetson-right    | Cannon Control Right |
| 3      | 172.18.254.233 | jetson3-opto    | Optoelectronics      |

## 🚀 Cách 1: Script tự động (Khuyến nghị)

### Bước 1: Copy script lên từng Jetson

```bash
# Trên máy phát triển
scp setup_static_ip.sh user@jetson:/home/user/

# SSH vào từng Jetson
ssh user@jetson
```

### Bước 2: Chạy script

```bash
cd /home/user
chmod +x setup_static_ip.sh
sudo ./setup_static_ip.sh
```

### Bước 3: Chọn số tương ứng

- Jetson 1: Chọn `1`
- Jetson Left: Chọn `2`
- Jetson Right: Chọn `3`
- Jetson 3: Chọn `4`

### Bước 4: Khởi động lại

```bash
sudo reboot
```

## 🔧 Cách 2: Cấu hình thủ công

### Ubuntu 18.04+ (NetworkManager)

```bash
# Xác định interface (thường là eth0 hoặc wlan0)
ip addr

# Cấu hình IP tĩnh cho Jetson 1
sudo nmcli con mod eth0 ipv4.addresses "172.18.254.230/24"
sudo nmcli con mod eth0 ipv4.gateway "172.18.254.1"
sudo nmcli con mod eth0 ipv4.dns "8.8.8.8 8.8.4.4"
sudo nmcli con mod eth0 ipv4.method manual
sudo nmcli con down eth0 && sudo nmcli con up eth0

# Kiểm tra
ip addr show eth0
```

### Ubuntu 18.04+ (Netplan)

Tạo file `/etc/netplan/01-netcfg.yaml`:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 172.18.254.230/24
      gateway4: 172.18.254.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Áp dụng cấu hình:

```bash
sudo netplan apply
```

### Ubuntu cũ (/etc/network/interfaces)

Chỉnh sửa `/etc/network/interfaces`:

```bash
sudo nano /etc/network/interfaces
```

Thêm:

```
auto eth0
iface eth0 inet static
    address 172.18.254.230
    netmask 255.255.255.0
    gateway 172.18.254.1
    dns-nameservers 8.8.8.8 8.8.4.4
```

Khởi động lại networking:

```bash
sudo systemctl restart networking
```

## 🏷️ Cách 3: Đặt hostname (Tuỳ chọn)

Để dễ nhận biết các Jetson:

```bash
# Jetson 1
sudo hostnamectl set-hostname jetson1-control

# Jetson Left
sudo hostnamectl set-hostname jetson-left

# Jetson Right
sudo hostnamectl set-hostname jetson-right

# Jetson 3
sudo hostnamectl set-hostname jetson3-opto
```

Thêm vào `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

Thêm dòng:

```
172.18.254.230  jetson1-control
172.18.254.231  jetson-left
172.18.254.232  jetson-right
172.18.254.233  jetson3-opto
```

## 🔍 Kiểm tra cấu hình

### Kiểm tra IP

```bash
ip addr show
# Hoặc
ifconfig
```

### Kiểm tra gateway

```bash
ip route
```

### Kiểm tra DNS

```bash
cat /etc/resolv.conf
```

### Kiểm tra kết nối

```bash
# Ping gateway
ping 172.18.254.1

# Ping Google DNS
ping 8.8.8.8

# Ping Jetson khác
ping 172.18.254.231
```

### Kiểm tra hostname

```bash
hostname
hostnamectl
```

## 🌍 Cách 4: Sử dụng hostname thay vì IP (Nâng cao)

Sau khi cấu hình hostname, bạn có thể cập nhật code để dùng hostname:

### Cập nhật webhook_config.py

```python
# Thay vì dùng IP
JETSON_LEFT_HOST = "jetson-left"
JETSON_RIGHT_HOST = "jetson-right"
JETSON3_HOST = "jetson3-opto"
```

**Lợi ích:**

- Không cần thay đổi code khi IP thay đổi
- Dễ đọc, dễ nhớ
- Hỗ trợ mDNS/Avahi (jetson-left.local)

**Yêu cầu:**

- Tất cả Jetson phải nằm trong cùng mạng LAN
- DNS hoặc /etc/hosts phải được cấu hình đúng

## 📡 Cách 5: DHCP Reservation (Router-based)

Nếu bạn có quyền truy cập router:

1. Đăng nhập vào router (thường là 192.168.1.1 hoặc 172.18.254.1)
2. Tìm phần **DHCP Reservation** hoặc **Static DHCP**
3. Thêm MAC address của mỗi Jetson với IP tương ứng:
   - Lấy MAC: `ip addr | grep ether`
   - Đặt reservation: MAC → IP

**Lợi ích:**

- Không cần cấu hình trên từng Jetson
- Quản lý tập trung tại router
- Tự động áp dụng sau mỗi lần khởi động

## 🐛 Troubleshooting

### IP không thay đổi sau khi cấu hình

```bash
# Xóa lease DHCP cũ
sudo rm /var/lib/dhcp/dhclient.leases
sudo systemctl restart networking
```

### Mất kết nối mạng sau khi cấu hình

```bash
# Kiểm tra lại cấu hình
ip addr
ip route

# Khôi phục DHCP
sudo nmcli con mod eth0 ipv4.method auto
sudo nmcli con down eth0 && sudo nmcli con up eth0
```

### Gateway không đúng

```bash
# Xóa gateway mặc định
sudo ip route del default

# Thêm gateway mới
sudo ip route add default via 172.18.254.1
```

## 📝 Checklist sau khi cấu hình

- [ ] IP tĩnh đã được đặt đúng
- [ ] Gateway hoạt động (`ping 172.18.254.1`)
- [ ] DNS hoạt động (`ping google.com`)
- [ ] Các Jetson ping được nhau
- [ ] Hostname đã được đặt
- [ ] Cấu hình tồn tại sau khi reboot
- [ ] Code đã được cập nhật với IP mới (nếu cần)

## 🎯 Khuyến nghị

**Môi trường development:**

- Dùng DHCP Reservation trên router (nếu có)
- Hoặc cấu hình IP tĩnh trên từng Jetson

**Môi trường production:**

- **Bắt buộc** dùng IP tĩnh
- Cấu hình backup (ghi lại cấu hình)
- Sử dụng hostname để linh hoạt hơn
