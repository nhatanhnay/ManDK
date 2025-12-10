#!/bin/bash
# Script khởi động hệ thống webhook trên Jetson1
# Chạy script này để khởi động ứng dụng điều khiển

echo "=================================================="
echo "  Khởi động hệ thống điều khiển Jetson1"
echo "=================================================="
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được cài đặt!"
    exit 1
fi

# Kiểm tra dependencies
echo "Kiểm tra dependencies..."
python3 -c "import flask, requests, PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Thiếu dependencies. Đang cài đặt..."
    pip3 install -r requirements.txt
fi

# Kiểm tra cấu hình
echo "Kiểm tra cấu hình..."
JETSON2_IP=$(python3 -c "from communication.webhook_config import JETSON2_HOST; print(JETSON2_HOST)" 2>/dev/null)
if [ -z "$JETSON2_IP" ]; then
    echo "⚠️  Không thể đọc IP Jetson2 từ config"
else
    echo "📡 Jetson2 IP: $JETSON2_IP"
    
    # Ping test
    ping -c 1 -W 2 "$JETSON2_IP" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Kết nối đến Jetson2 OK"
    else
        echo "⚠️  Không thể ping đến Jetson2. Kiểm tra kết nối mạng!"
    fi
fi

echo ""
echo "🚀 Khởi động ứng dụng..."
echo "   - Webhook receiver sẽ chạy trên port 5001"
echo "   - Nhấn Ctrl+C để thoát"
echo ""

# Chạy ứng dụng
python3 main.py
