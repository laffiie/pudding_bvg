#!/bin/bash
# Setup script for Raspberry Pi
# Run this on your Raspberry Pi to install everything

set -e

echo "🍓 BVG Abfahrtsmonitor - Raspberry Pi Setup"
echo "==========================================="
echo ""

# Check if running on Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    fonts-noto-color-emoji \
    unclutter

# Install Python packages
echo "🐍 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created in .venv"
fi

echo "📦 Installing Python dependencies into virtual environment..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# Check if config exists
if [ ! -f "./config/config.json" ]; then
    echo "⚠️  No config.json found, copying example..."
    cp ./config/config.example.json ./config/config.json
    echo "✏️  Please edit ./config/config.json with your station IDs"
fi

# Add user to video group (for framebuffer access)
echo "👤 Adding user to video group..."
sudo usermod -a -G video $USER

# Create systemd user service (inherits Wayland session automatically)
echo "⚙️  Creating systemd user service..."
ACTUAL_USER=$(whoami)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
ACTUAL_PWD=$PWD
ACTUAL_UID=$(id -u $ACTUAL_USER)

SERVICE_DIR="$ACTUAL_HOME/.config/systemd/user"
mkdir -p "$SERVICE_DIR"
SERVICE_FILE="$SERVICE_DIR/bvg-display.service"
tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=BVG Abfahrtsmonitor
After=network-online.target graphical-session.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ACTUAL_PWD
ExecStart=$ACTUAL_PWD/.venv/bin/python3 $ACTUAL_PWD/main.py $ACTUAL_PWD/config/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Enable linger so user services start at boot without login
sudo loginctl enable-linger $ACTUAL_USER

# Reload user systemd
systemctl --user daemon-reload

echo "✅ User service created: $SERVICE_FILE"
echo "   Working directory: $ACTUAL_PWD"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config: nano ./config/config.json"
echo "2. Test manually: ./.venv/bin/python3 main.py ./config/config.json"
echo "3. Enable auto-start: systemctl --user enable bvg-display.service"
echo "4. Start service: systemctl --user start bvg-display.service"
echo "5. Check status: systemctl --user status bvg-display.service"
echo ""
echo "Optional: Disable screen blanking"
echo "  For Desktop OS: See README_PI.md"
echo "  For Lite OS: Add 'consoleblank=0' to /boot/cmdline.txt"
echo ""
echo "🎉 Ready to go! Reboot recommended."
