#!/usr/bin/env python3
"""
Battery Power Monitor for MATE Desktop
Configurable system tray indicator showing real-time power consumption
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import json
import os
from pathlib import Path

# ============= CONFIGURATION =============
CONFIG = {
    # Update interval in seconds
    "update_interval": 1,
    
    # Battery device (BAT0, BAT1, etc.)
    "battery_device": "BAT1",
    
    # Display format: "short" shows "5.23W", "detailed" shows "Power: 5.23W"
    "display_format": "short",
    
    # Decimal places for power reading
    "decimal_places": 2,
    
    # Color coding thresholds (watts)
    "color_coding": {
        "enabled": True,
        "low": 5.0,      # Green below this
        "medium": 15.0,  # Yellow between low and medium
        "high": 25.0     # Orange between medium and high, red above
    },
    
    # Icon style: "battery", "power", "bolt", "chip"
    "icon_style": "battery",
    
    # Show notification on high power draw
    "notify_high_power": {
        "enabled": False,
        "threshold": 30.0,
        "cooldown": 300  # seconds between notifications
    },
    
    # Menu options
    "show_voltage": True,
    "show_current": True,
    "show_battery_status": True,
    "show_capacity": True
}

class BatteryPowerMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.battery_path = f"/sys/class/power_supply/{self.config['battery_device']}"
        self.last_notification = 0
        
        # Set up indicator
        icon = self.get_icon_name()
        self.indicator = AppIndicator3.Indicator.new(
            "battery-power-monitor",
            icon,
            AppIndicator3.IndicatorCategory.HARDWARE
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create menu
        self.create_menu()
        
        # Start updating
        self.update_power()
        GLib.timeout_add_seconds(self.config['update_interval'], self.update_power)
    
    def load_config(self):
        """Load configuration from file or use defaults"""
        config_file = Path.home() / ".config" / "battery-power-monitor.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = CONFIG.copy()
                    config.update(user_config)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        # Save default config
        self.save_config(CONFIG)
        return CONFIG
    
    def save_config(self, config):
        """Save configuration to file"""
        config_dir = Path.home() / ".config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "battery-power-monitor.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_icon_name(self):
        """Get icon based on configuration"""
        icons = {
            "battery": "battery",
            "power": "system-shutdown",
            "bolt": "weather-storm",
            "chip": "computer"
        }
        return icons.get(self.config['icon_style'], "battery")
    
    def read_battery_value(self, filename):
        """Read a value from battery sysfs"""
        try:
            with open(f"{self.battery_path}/{filename}", 'r') as f:
                return int(f.read().strip())
        except:
            return None
    
    def read_battery_string(self, filename):
        """Read a string from battery sysfs"""
        try:
            with open(f"{self.battery_path}/{filename}", 'r') as f:
                return f.read().strip()
        except:
            return None
    
    def get_power_draw(self):
        """Calculate current power draw in watts"""
        voltage = self.read_battery_value("voltage_now")
        current = self.read_battery_value("current_now")
        
        if voltage is None or current is None:
            return None
        
        # Calculate power in watts
        power = (voltage * current) / 1_000_000_000_000
        return power
    
    def get_power_color(self, power):
        """Get color emoji/indicator based on power level"""
        if not self.config['color_coding']['enabled']:
            return ""
        
        thresholds = self.config['color_coding']
        
        if power < thresholds['low']:
            return "🟢"
        elif power < thresholds['medium']:
            return "🟡"
        elif power < thresholds['high']:
            return "🟠"
        else:
            return "🔴"
    
    def format_power_label(self, power):
        """Format power reading for display"""
        decimals = self.config['decimal_places']
        
        if self.config['display_format'] == "short":
            return f"{power:.{decimals}f}W"
        else:
            return f"Power: {power:.{decimals}f}W"
    
    def check_high_power_notification(self, power):
        """Send notification if power is too high"""
        notify_config = self.config['notify_high_power']
        
        if not notify_config['enabled']:
            return
        
        if power < notify_config['threshold']:
            return
        
        import time
        current_time = time.time()
        
        if current_time - self.last_notification < notify_config['cooldown']:
            return
        
        try:
            import subprocess
            subprocess.run([
                'notify-send',
                '⚠️ High Power Draw',
                f'Battery is consuming {power:.1f}W',
                '-u', 'normal',
                '-t', '5000'
            ])
            self.last_notification = current_time
        except:
            pass
    
    def update_power(self):
        """Update power reading and display"""
        power = self.get_power_draw()
        
        if power is None:
            self.indicator.set_label("ERR", "")
            return True
        
        # Format label
        label = self.format_power_label(power)
        color = self.get_power_color(power)
        
        # Update indicator
        self.indicator.set_label(f"{color} {label}".strip(), "")
        
        # Update menu items
        self.update_menu_items()
        
        # Check for notifications
        self.check_high_power_notification(power)
        
        return True
    
    def create_menu(self):
        """Create the context menu"""
        self.menu = Gtk.Menu()
        
        # Power info
        self.power_item = Gtk.MenuItem(label="Power: Calculating...")
        self.power_item.set_sensitive(False)
        self.menu.append(self.power_item)
        
        if self.config['show_voltage'] or self.config['show_current']:
            self.menu.append(Gtk.SeparatorMenuItem())
        
        # Voltage
        if self.config['show_voltage']:
            self.voltage_item = Gtk.MenuItem(label="Voltage: --")
            self.voltage_item.set_sensitive(False)
            self.menu.append(self.voltage_item)
        
        # Current
        if self.config['show_current']:
            self.current_item = Gtk.MenuItem(label="Current: --")
            self.current_item.set_sensitive(False)
            self.menu.append(self.current_item)
        
        if self.config['show_battery_status'] or self.config['show_capacity']:
            self.menu.append(Gtk.SeparatorMenuItem())
        
        # Battery status
        if self.config['show_battery_status']:
            self.status_item = Gtk.MenuItem(label="Status: --")
            self.status_item.set_sensitive(False)
            self.menu.append(self.status_item)
        
        # Capacity
        if self.config['show_capacity']:
            self.capacity_item = Gtk.MenuItem(label="Capacity: --")
            self.capacity_item.set_sensitive(False)
            self.menu.append(self.capacity_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Settings
        settings_item = Gtk.MenuItem(label="⚙️ Settings")
        settings_item.connect("activate", self.open_settings)
        self.menu.append(settings_item)
        
        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
    
    def update_menu_items(self):
        """Update menu items with current values"""
        power = self.get_power_draw()
        
        if power is not None:
            decimals = self.config['decimal_places']
            self.power_item.set_label(f"Power Draw: {power:.{decimals}f} W")
        
        if self.config['show_voltage']:
            voltage = self.read_battery_value("voltage_now")
            if voltage:
                self.voltage_item.set_label(f"Voltage: {voltage/1_000_000:.2f} V")
        
        if self.config['show_current']:
            current = self.read_battery_value("current_now")
            if current:
                self.current_item.set_label(f"Current: {current/1_000_000:.2f} A")
        
        if self.config['show_battery_status']:
            status = self.read_battery_string("status")
            if status:
                self.status_item.set_label(f"Status: {status}")
        
        if self.config['show_capacity']:
            capacity = self.read_battery_value("capacity")
            if capacity is not None:
                self.capacity_item.set_label(f"Capacity: {capacity}%")
    
    def open_settings(self, widget):
        """Open configuration file in default editor"""
        config_file = Path.home() / ".config" / "battery-power-monitor.json"
        
        try:
            import subprocess
            subprocess.Popen(['xdg-open', str(config_file)])
        except:
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Configuration file:"
            )
            dialog.format_secondary_text(str(config_file))
            dialog.run()
            dialog.destroy()
    
    def quit(self, widget):
        """Quit the application"""
        Gtk.main_quit()

def main():
    # Check if battery device exists
    battery_device = CONFIG['battery_device']
    battery_path = f"/sys/class/power_supply/{battery_device}"
    
    if not os.path.exists(battery_path):
        print(f"Error: Battery device {battery_device} not found!")
        print("\nAvailable devices:")
        power_supply = Path("/sys/class/power_supply")
        if power_supply.exists():
            for device in power_supply.iterdir():
                print(f"  - {device.name}")
        return 1
    
    monitor = BatteryPowerMonitor()
    Gtk.main()
    return 0

if __name__ == "__main__":
    exit(main())
