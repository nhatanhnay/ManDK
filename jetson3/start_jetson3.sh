#!/bin/bash
# Script khởi động data sender trên Jetson3 (Quang điện tử)
# Chạy script này để khởi động gửi dữ liệu khoảng cách và hướng về Jetson1

echo "=================================================="
echo "  Khởi động Data Sender Jetson3 (Quang điện tử)"
echo "=================================================="
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được cài đặt!"
    exit 1
fi

# Di chuyển vào thư mục jetson3
cd "$(dirname "$0")" || exit 1

# Kiểm tra dependencies
echo "Kiểm tra dependencies..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Thiếu dependencies. Đang cài đặt..."
    pip3 install requests
fi

# Kiểm tra cấu hình
echo "Kiểm tra cấu hình..."
JETSON1_IP=$(python3 -c "exec(open('data_sender_jetson3.py').read()); print(JETSON1_HOST)" 2>/dev/null)
if [ -z "$JETSON1_IP" ]; then
    echo "⚠️  Không thể đọc IP Jetson1 từ config"
else
    echo "📡 Jetson1 IP: $JETSON1_IP"
    
    # Ping test
    ping -c 1 -W 2 "$JETSON1_IP" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Kết nối đến Jetson1 OK"
    else
        echo "⚠️  Không thể ping đến Jetson1. Kiểm tra kết nối mạng!"
    fi
fi

echo ""
echo "Chọn chế độ chạy:"
echo "  1. Test một lần (gửi dữ liệu mẫu)"
echo "  2. Continuous loop (mock data, 5 Hz)"
echo "  3. Exit"
echo ""
read -p "Nhập lựa chọn (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Chạy test một lần..."
        echo "--------------------------------------------------"
        python3 data_sender_jetson3.py
        ;;
    2)
        echo ""
        echo "🔄 Chạy continuous loop với mock data (5 Hz)..."
        echo "   - Nhấn Ctrl+C để dừng"
        echo "--------------------------------------------------"
        python3 data_sender_jetson3.py loop
        ;;
    3)
        echo "Đã thoát"
        exit 0
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac
