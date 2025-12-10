#!/bin/bash

# Start Jetson Right Webhook Server
# Script khởi động server điều khiển pháo phải

echo "==========================================="
echo "Jetson Right - Hệ thống điều khiển pháo phải"
echo "==========================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Lỗi: Không tìm thấy Python3"
    exit 1
fi

# Kiểm tra dependencies
echo "Đang kiểm tra dependencies..."
python3 -c "import flask" 2>/dev/null || {
    echo "❌ Flask chưa được cài đặt"
    echo "Chạy: pip install flask"
    exit 1
}

python3 -c "import requests" 2>/dev/null || {
    echo "❌ Requests chưa được cài đặt"
    echo "Chạy: pip install requests"
    exit 1
}

echo "✅ Dependencies OK"

# Kiểm tra IP
MY_IP=$(hostname -I | awk '{print $1}')
echo "IP của Jetson Right: $MY_IP"

# Menu
echo ""
echo "Chọn chế độ khởi động:"
echo "1. Chạy webhook server (nhận lệnh từ Jetson1)"
echo "2. Test gửi data về Jetson1"
echo "3. Chạy cả hai (server + data sender loop)"
echo "4. Thoát"
echo -n "Lựa chọn [1-4]: "
read choice

case $choice in
    1)
        echo ""
        echo "🚀 Khởi động webhook server..."
        echo "Server sẽ lắng nghe tại: http://0.0.0.0:5000"
        python3 webhook_server.py
        ;;
    2)
        echo ""
        echo "📤 Test gửi data về Jetson1..."
        python3 data_sender.py
        ;;
    3)
        echo ""
        echo "🚀 Khởi động cả server và data sender..."
        # Chạy server ở background
        python3 webhook_server.py &
        SERVER_PID=$!
        echo "Server PID: $SERVER_PID"
        
        # Đợi 2 giây để server khởi động
        sleep 2
        
        # Chạy data sender
        echo "Đang gửi data..."
        python3 data_sender.py
        
        # Cleanup
        kill $SERVER_PID 2>/dev/null
        ;;
    4)
        echo "Thoát."
        exit 0
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac
