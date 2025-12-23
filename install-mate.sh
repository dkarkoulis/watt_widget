#!/bin/bash
# Installation script for Battery Power Monitor (MATE Desktop)

set -e

echo "╔════════════════════════════════════════════╗"
echo "║  Battery Power Monitor for MATE Desktop   ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if running on a system with a battery
if [ ! -d "/sys/class/power_supply" ]; then
    echo "❌ Error: No power supply devices found!"
    echo "This tool requires a laptop with a battery."
    exit 1
fi

# Detect battery device
echo "🔍 Detecting battery device..."
BATTERY_DEVICE=""
for dev in /sys/class/power_supply/*; do
    if [ -f "$dev/voltage_now" ] && [ -f "$dev/current_now" ]; then
        BATTERY_DEVICE=$(basename "$dev")
        echo "✅ Found battery: $BATTERY_DEVICE"
        break
    fi
done

if [ -z "$BATTERY_DEVICE" ]; then
    echo "❌ Error: No compatible battery device found!"
    echo "Available devices:"
    ls /sys/class/power_supply/
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3-gi gir1.2-appindicator3-0.1 libnotify-bin
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-gobject gtk3 libappindicator-gtk3 libnotify
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm python-gobject gtk3 libappindicator-gtk3 libnotify
else
    echo "⚠️  Warning: Could not detect package manager."
    echo "Please install: python3-gi, gir1.2-appindicator3-0.1, libnotify"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p ~/.local/bin
mkdir -p ~/.config/autostart

# Install the monitor script
echo "📋 Installing battery power monitor..."
cp battery-power-monitor.py ~/.local/bin/battery-power-monitor
chmod +x ~/.local/bin/battery-power-monitor

# Create configuration file
CONFIG_FILE="$HOME/.config/battery-power-monitor.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚙️  Creating configuration file..."
    cat > "$CONFIG_FILE" << EOF
{
    "update_interval": 1,
    "battery_device": "$BATTERY_DEVICE",
    "display_format": "short",
    "decimal_places": 2,
    "color_coding": {
        "enabled": true,
        "low": 5.0,
        "medium": 15.0,
        "high": 25.0
    },
    "icon_style": "battery",
    "notify_high_power": {
        "enabled": false,
        "threshold": 30.0,
        "cooldown": 300
    },
    "show_voltage": true,
    "show_current": true,
    "show_battery_status": true,
    "show_capacity": true
}
EOF
    echo "✅ Configuration created at: $CONFIG_FILE"
else
    echo "ℹ️  Configuration already exists, keeping current settings"
fi

# Create autostart entry
echo "🚀 Creating autostart entry..."
cat > ~/.config/autostart/battery-power-monitor.desktop << EOF
[Desktop Entry]
Type=Application
Name=Battery Power Monitor
Comment=Shows real-time battery power consumption
Exec=$HOME/.local/bin/battery-power-monitor
Icon=battery
Terminal=false
Categories=System;Monitor;
StartupNotify=false
X-MATE-Autostart-enabled=true
EOF

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║        Installation Complete! 🎉          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📍 Installed to: ~/.local/bin/battery-power-monitor"
echo "⚙️  Config file: ~/.config/battery-power-monitor.json"
echo "🚀 Autostart: ~/.config/autostart/battery-power-monitor.desktop"
echo ""
echo "To start the monitor now:"
echo "  ~/.local/bin/battery-power-monitor &"
echo ""
echo "Or log out and log back in for autostart."
echo ""
echo "💡 Tips:"
echo "  • Click the tray icon to see detailed battery info"
echo "  • Right-click and select 'Settings' to edit configuration"
echo "  • Customize update interval, colors, and notifications"
echo ""
