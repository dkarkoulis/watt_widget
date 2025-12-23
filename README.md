# Battery Power Monitor for MATE Desktop 🔋⚡

A beautiful, configurable system tray indicator that shows real-time battery power consumption in watts for MATE Desktop Environment.

## Features ✨

- **Real-time monitoring**: Updates every second (configurable)
- **System tray integration**: Clean, minimal display in your panel
- **Color-coded alerts**: Visual indicators for power levels (🟢🟡🟠🔴)
- **Detailed menu**: Click to see voltage, current, battery status, and capacity
- **Fully configurable**: JSON config file for easy customization
- **Optional notifications**: Get alerts when power draw is too high
- **Auto-start support**: Automatically runs on login
- **Lightweight**: Minimal CPU and memory usage

## Quick Installation 🚀

```bash
chmod +x install-mate.sh
./install-mate.sh
```

The installer will:
1. Detect your battery device automatically
2. Install required dependencies
3. Set up the monitor in `~/.local/bin`
4. Create a configuration file
5. Add autostart entry

Start it immediately:
```bash
~/.local/bin/battery-power-monitor &
```

Or log out and log back in for autostart.

## Configuration ⚙️

The configuration file is located at:
```
~/.config/battery-power-monitor.json
```

You can edit it with any text editor or click "Settings" in the tray menu.

### Configuration Options

```json
{
    "update_interval": 1,           // Update frequency in seconds
    "battery_device": "BAT1",        // Your battery device (BAT0, BAT1, etc.)
    "display_format": "short",       // "short" (5.23W) or "detailed" (Power: 5.23W)
    "decimal_places": 2,             // Number of decimal places
    
    "color_coding": {
        "enabled": true,             // Enable color indicators
        "low": 5.0,                  // 🟢 Green below this (W)
        "medium": 15.0,              // 🟡 Yellow between low-medium
        "high": 25.0                 // 🟠 Orange between medium-high, 🔴 Red above
    },
    
    "icon_style": "battery",         // "battery", "power", "bolt", or "chip"
    
    "notify_high_power": {
        "enabled": false,            // Enable high power notifications
        "threshold": 30.0,           // Notify when power exceeds this (W)
        "cooldown": 300              // Seconds between notifications
    },
    
    "show_voltage": true,            // Show voltage in menu
    "show_current": true,            // Show current in menu
    "show_battery_status": true,     // Show charging/discharging status
    "show_capacity": true            // Show battery percentage
}
```

### Example Configurations

**Minimal Display:**
```json
{
    "display_format": "short",
    "decimal_places": 1,
    "color_coding": {"enabled": false},
    "show_voltage": false,
    "show_current": false
}
```

**Power User:**
```json
{
    "update_interval": 0.5,
    "decimal_places": 3,
    "notify_high_power": {
        "enabled": true,
        "threshold": 20.0,
        "cooldown": 180
    }
}
```

**Battery Saver Mode:**
```json
{
    "update_interval": 5,
    "color_coding": {
        "enabled": true,
        "low": 3.0,
        "medium": 8.0,
        "high": 15.0
    }
}
```

## Usage 💡

### System Tray Display

The indicator shows in your MATE panel with the current power draw:
- `🟢 4.52W` - Low power usage
- `🟡 12.34W` - Medium power usage  
- `🟠 23.45W` - High power usage
- `🔴 35.67W` - Very high power usage

### Menu Options

Click the indicator to see:
- Current power draw
- Voltage and current
- Battery status (Charging/Discharging)
- Battery capacity percentage
- Settings (opens config file)
- Quit

## Troubleshooting 🔧

### Wrong Battery Device

If the monitor shows "ERR", check your battery device:
```bash
ls /sys/class/power_supply/
```

Update the config file with the correct device name (e.g., `BAT0`, `BAT1`).

### Indicator Not Showing

1. Make sure AppIndicator is supported in MATE:
   ```bash
   sudo apt install gir1.2-appindicator3-0.1
   ```

2. Restart the MATE panel:
   ```bash
   mate-panel --replace &
   ```

### Permission Issues

The battery info files should be readable by all users. If not:
```bash
ls -la /sys/class/power_supply/BAT1/
```

### Multiple Batteries

If you have multiple batteries, the monitor tracks one at a time. To monitor both:
1. Run two instances with different config files
2. Or modify the script to sum power from both batteries

## Customization Ideas 🎨

### Change Update Speed
Fast updates (0.5s) for monitoring intensive tasks:
```json
{"update_interval": 0.5}
```

Slow updates (5s) to save resources:
```json
{"update_interval": 5}
```

### Different Icon Styles
```json
{"icon_style": "bolt"}      // Lightning bolt
{"icon_style": "power"}     // Power button
{"icon_style": "chip"}      // Computer chip
```

### High Power Alerts
Get notified when your laptop is consuming too much power:
```json
{
    "notify_high_power": {
        "enabled": true,
        "threshold": 25.0,
        "cooldown": 300
    }
}
```

### Minimal Display
Just show the number:
```json
{
    "display_format": "short",
    "color_coding": {"enabled": false},
    "show_voltage": false,
    "show_current": false,
    "show_battery_status": false,
    "show_capacity": false
}
```

## Manual Installation 📝

If you prefer manual installation:

1. **Install dependencies:**
   ```bash
   sudo apt install python3-gi gir1.2-appindicator3-0.1 libnotify-bin
   ```

2. **Copy the script:**
   ```bash
   cp battery-power-monitor.py ~/.local/bin/battery-power-monitor
   chmod +x ~/.local/bin/battery-power-monitor
   ```

3. **Create config:**
   ```bash
   mkdir -p ~/.config
   # Edit and save the config from above
   ```

4. **Create autostart:**
   ```bash
   mkdir -p ~/.config/autostart
   cat > ~/.config/autostart/battery-power-monitor.desktop << 'EOF'
   [Desktop Entry]
   Type=Application
   Name=Battery Power Monitor
   Exec=$HOME/.local/bin/battery-power-monitor
   Icon=battery
   Terminal=false
   Categories=System;
   X-MATE-Autostart-enabled=true
   EOF
   ```

## Uninstallation 🗑️

```bash
rm ~/.local/bin/battery-power-monitor
rm ~/.config/battery-power-monitor.json
rm ~/.config/autostart/battery-power-monitor.desktop
pkill -f battery-power-monitor
```

## How It Works 🔍

The monitor reads from Linux's battery interface:
```
/sys/class/power_supply/BAT1/voltage_now    # Voltage in microvolts
/sys/class/power_supply/BAT1/current_now    # Current in microamps
```

Power (W) = Voltage (V) × Current (A)

## Requirements 📋

- **OS**: Linux with MATE Desktop
- **Python**: 3.6+
- **Packages**: 
  - `python3-gi`
  - `gir1.2-appindicator3-0.1`
  - `libnotify-bin` (for notifications)
- **Hardware**: Laptop with battery that exposes voltage_now and current_now

## Tips 💭

1. **Find power-hungry apps**: Monitor power while opening different applications
2. **Compare browsers**: See which browser uses less power
3. **Optimize brightness**: Watch power drop as you lower screen brightness
4. **Track background tasks**: Identify processes consuming power
5. **Gaming monitoring**: See real-time power draw during gaming

## Contributing 🤝

Feel free to modify and improve! Common enhancements:
- Graph/history display
- Battery time estimation
- Multiple battery support
- Desktop widget version
- Export power logs

## License 📄

This is free and open-source software. Use it however you like!

## Support ❤️

If you encounter issues:
1. Check the troubleshooting section
2. Verify your battery device path
3. Make sure all dependencies are installed
4. Check system logs: `journalctl -xe | grep battery`

Enjoy monitoring your battery power! ⚡🔋
