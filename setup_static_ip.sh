#!/bin/bash
# Script cấu hình IP tĩnh cho các Jetson
# Chạy script này với quyền sudo

echo "=========================================="
echo "Cấu hình IP tĩnh cho hệ thống Jetson"
echo "=========================================="
echo ""

# Kiểm tra quyền sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Vui lòng chạy với quyền sudo:"
    echo "   sudo ./setup_static_ip.sh"
    exit 1
fi

# Menu chọn Jetson
echo "Bạn đang cấu hình cho Jetson nào?"
echo "1. Jetson 1 (Control Center) - 192.0.0.100"
echo "2. Jetson Left (Pháo trái) - 192.0.0.101"
echo "3. Jetson Right (Pháo phải) - 192.0.0.102"
echo "4. Jetson 3 (Quang điện tử) - 192.0.0.103"
echo "5. Tùy chỉnh IP khác"
echo ""
read -p "Nhập lựa chọn [1-5]: " choice

case $choice in
    1)
        STATIC_IP="192.0.0.100"
        HOSTNAME="jetson1-control"
        ;;
    2)
        STATIC_IP="192.0.0.101"
        HOSTNAME="jetson-left"
        ;;
    3)
        STATIC_IP="192.0.0.102"
        HOSTNAME="jetson-right"
        ;;
    4)
        STATIC_IP="192.0.0.103"
        HOSTNAME="jetson3-opto"
        ;;
    5)
        read -p "Nhập IP tĩnh (VD: 192.0.0.110): " STATIC_IP
        read -p "Nhập hostname (VD: jetson-custom): " HOSTNAME
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac

# Tự động phát hiện interface mạng
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -z "$INTERFACE" ]; then
    echo "❌ Không tìm thấy network interface"
    exit 1
fi

echo ""
echo "Thông tin cấu hình:"
echo "  Interface: $INTERFACE"
echo "  IP tĩnh: $STATIC_IP"
echo "  Subnet: 192.0.0.0/24"
echo "  Gateway: 192.0.0.1"
echo "  DNS: 8.8.8.8, 8.8.4.4"
echo "  Hostname: $HOSTNAME"
echo ""
read -p "Xác nhận cấu hình? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Hủy bỏ."
    exit 0
fi

# Phương pháp 1: NetworkManager (Ubuntu 18.04+)
echo ""
echo "Đang cấu hình với NetworkManager..."

nmcli con mod "$INTERFACE" ipv4.addresses "$STATIC_IP/24"
nmcli con mod "$INTERFACE" ipv4.gateway "192.0.0.1"
nmcli con mod "$INTERFACE" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli con mod "$INTERFACE" ipv4.method manual
nmcli con down "$INTERFACE" && nmcli con up "$INTERFACE"

if [ $? -eq 0 ]; then
    echo "✅ Đã cấu hình IP tĩnh với NetworkManager"
else
    echo "⚠️ NetworkManager thất bại, thử cách khác..."
    
    # Phương pháp 2: netplan (Ubuntu 18.04+)
    NETPLAN_FILE="/etc/netplan/01-netcfg.yaml"
    
    if [ -d "/etc/netplan" ]; then
        echo "Đang cấu hình với Netplan..."
        
        cat > $NETPLAN_FILE << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: no
      addresses:
        - $STATIC_IP/24
      gateway4: 192.0.0.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
EOF
        
        chmod 600 $NETPLAN_FILE
        netplan apply
        
        if [ $? -eq 0 ]; then
            echo "✅ Đã cấu hình IP tĩnh với Netplan"
        else
            echo "❌ Netplan thất bại"
        fi
    else
        # Phương pháp 3: /etc/network/interfaces (cũ)
        echo "Đang cấu hình với /etc/network/interfaces..."
        
        cat >> /etc/network/interfaces << EOF

# Static IP configuration
auto $INTERFACE
iface $INTERFACE inet static
    address $STATIC_IP
    netmask 255.255.255.0
    gateway 192.0.0.1
    dns-nameservers 8.8.8.8 8.8.4.4
EOF
        
        systemctl restart networking
        echo "✅ Đã cấu hình IP tĩnh với /etc/network/interfaces"
    fi
fi

# Cấu hình hostname
echo ""
echo "Đang cấu hình hostname..."
hostnamectl set-hostname "$HOSTNAME"
echo "127.0.1.1    $HOSTNAME" >> /etc/hosts

echo ""
echo "=========================================="
echo "✅ Hoàn tất cấu hình!"
echo "=========================================="
echo ""
echo "IP hiện tại:"
ip addr show $INTERFACE | grep "inet "
echo ""
echo "Hostname:"
hostname
echo ""
echo "⚠️ Khuyến nghị: Khởi động lại để đảm bảo cấu hình hoạt động ổn định"
echo "   sudo reboot"
