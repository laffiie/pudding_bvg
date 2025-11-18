#!/bin/bash
# Disable screen blanking on Raspberry Pi OS Desktop

echo "🖥️  Disabling Screen Blanking for BVG Display"
echo "=============================================="
echo ""

# Detect OS type
if [ -f /usr/bin/startx ]; then
    OS_TYPE="desktop"
else
    OS_TYPE="lite"
fi

echo "Detected OS: Raspberry Pi OS $OS_TYPE"
echo ""

if [ "$OS_TYPE" = "desktop" ]; then
    # Desktop OS
    echo "📝 Adding desktop configuration..."
    
    mkdir -p ~/.config/lxsession/LXDE-pi/
    
    # Add xset commands to autostart
    if [ -f ~/.config/lxsession/LXDE-pi/autostart ]; then
        # Backup existing file
        cp ~/.config/lxsession/LXDE-pi/autostart ~/.config/lxsession/LXDE-pi/autostart.backup
        echo "Backed up existing autostart file"
    fi
    
    # Add screen blanking disable commands
    cat >> ~/.config/lxsession/LXDE-pi/autostart <<EOF

# Disable screen blanking for BVG display
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
EOF
    
    echo "✅ Desktop autostart configured"
    echo ""
    echo "Changes will take effect on next login/reboot"
    
else
    # Lite OS (console only)
    echo "📝 Configuring console..."
    
    # Backup cmdline.txt
    sudo cp /boot/cmdline.txt /boot/cmdline.txt.backup
    echo "Backed up /boot/cmdline.txt"
    
    # Check if consoleblank=0 is already there
    if grep -q "consoleblank=0" /boot/cmdline.txt; then
        echo "⚠️  consoleblank=0 already present in /boot/cmdline.txt"
    else
        # Add consoleblank=0 to the end
        sudo sed -i '$ s/$/ consoleblank=0/' /boot/cmdline.txt
        echo "✅ Added consoleblank=0 to /boot/cmdline.txt"
    fi
    
    echo ""
    echo "⚠️  You must reboot for changes to take effect!"
fi

echo ""
echo "Additional tip: Hide mouse cursor with unclutter"
echo "  Already installed by install_pi.sh"
echo ""
echo "🎉 Done!"
