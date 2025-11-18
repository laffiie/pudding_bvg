#!/bin/bash
# Fix systemd service user issue
# Run this if you get "Failed to determine user credentials" error

set -e

echo "🔧 Fixing BVG Display Service User"
echo "===================================="
echo ""

# Get actual username
ACTUAL_USER=$(whoami)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

# Detect the working directory
if [ -d "$HOME/bvg_abfahrt" ]; then
    WORKING_DIR="$HOME/bvg_abfahrt"
elif [ -d "$ACTUAL_HOME/bvg_abfahrt" ]; then
    WORKING_DIR="$ACTUAL_HOME/bvg_abfahrt"
else
    echo "❌ Cannot find bvg_abfahrt directory"
    echo "Please run this from the bvg_abfahrt directory or specify the path:"
    echo "  cd ~/bvg_abfahrt && ./fix_service.sh"
    exit 1
fi

echo "Current user: $ACTUAL_USER"
echo "Working directory: $WORKING_DIR"
echo ""

# Stop the service if it's running
echo "⏹️  Stopping service..."
sudo systemctl stop bvg-display.service 2>/dev/null || true

# Create the service file with correct user
echo "📝 Creating service file..."
SERVICE_FILE="/etc/systemd/system/bvg-display.service"
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=BVG Abfahrtsmonitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$WORKING_DIR
Environment=DISPLAY=:0
Environment=SDL_VIDEODRIVER=x11
Environment=HOME=$ACTUAL_HOME
ExecStart=/usr/bin/python3 $WORKING_DIR/main.py $WORKING_DIR/config/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file updated"

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Show the service file for verification
echo ""
echo "📄 Service file contents:"
echo "------------------------"
sudo cat $SERVICE_FILE
echo "------------------------"
echo ""

# Test the service
echo "🧪 Testing service..."
sudo systemctl start bvg-display.service
sleep 2

if sudo systemctl is-active --quiet bvg-display.service; then
    echo "✅ Service started successfully!"
    echo ""
    echo "Status:"
    sudo systemctl status bvg-display.service --no-pager -l
    echo ""
    echo "To enable auto-start on boot:"
    echo "  sudo systemctl enable bvg-display.service"
else
    echo "❌ Service failed to start"
    echo ""
    echo "Checking logs:"
    sudo journalctl -u bvg-display.service -n 20 --no-pager
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if python3 is installed: which python3"
    echo "2. Check if config exists: ls -l $WORKING_DIR/config/config.json"
    echo "3. Try running manually: python3 $WORKING_DIR/main.py $WORKING_DIR/config/config.json"
    exit 1
fi

echo ""
echo "🎉 Done! Your service should now work correctly."
