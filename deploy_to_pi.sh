#!/bin/bash
# Helper script to deploy to Raspberry Pi from Mac/Linux

set -e

PI_HOST=${1:-"pi@raspberrypi.local"}
REMOTE_PATH="~/bvg_abfahrt"

echo "🚀 Deploying BVG Display to Raspberry Pi"
echo "========================================="
echo ""
echo "Target: $PI_HOST"
echo ""

# Check if we can reach the Pi
echo "🔍 Checking connection to Pi..."
if ! ping -c 1 -W 2 raspberrypi.local > /dev/null 2>&1; then
    echo "❌ Cannot reach raspberrypi.local"
    echo "Make sure your Pi is connected and try: ./deploy_to_pi.sh pi@<pi-ip-address>"
    exit 1
fi

echo "✅ Pi is reachable"
echo ""

# Copy files
echo "📦 Copying files to Pi..."
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
    ./ "$PI_HOST:$REMOTE_PATH/"

echo ""
echo "✅ Files copied successfully!"
echo ""

# Ask if user wants to run setup
read -p "Do you want to run the setup script on the Pi? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔧 Running setup on Pi..."
    ssh "$PI_HOST" "cd $REMOTE_PATH && chmod +x install_pi.sh && ./install_pi.sh"
    echo ""
    echo "✅ Setup complete!"
else
    echo ""
    echo "Skipping setup. You can run it later with:"
    echo "  ssh $PI_HOST"
    echo "  cd $REMOTE_PATH"
    echo "  ./install_pi.sh"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. SSH to Pi: ssh $PI_HOST"
echo "2. Edit config: nano $REMOTE_PATH/config/config.json"
echo "3. Test: $REMOTE_PATH/.venv/bin/python3 $REMOTE_PATH/main.py $REMOTE_PATH/config/config.json"
echo "4. Enable auto-start: sudo systemctl enable bvg-display.service"
echo "5. Start service: sudo systemctl start bvg-display.service"
echo ""
