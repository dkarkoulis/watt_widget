#!/usr/bin/env python3
"""
GUI Configuration Tool for Battery Power Monitor
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import json
from pathlib import Path

class ConfigWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Battery Power Monitor Settings")
        self.set_border_width(10)
        self.set_default_size(500, 600)
        
        self.config_file = Path.home() / ".config" / "battery-power-monitor.json"
        self.config = self.load_config()
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        self.add(notebook)
        
        # General settings tab
        general_box = self.create_general_tab()
        notebook.append_page(general_box, Gtk.Label(label="General"))
        
        # Display settings tab
        display_box = self.create_display_tab()
        notebook.append_page(display_box, Gtk.Label(label="Display"))
        
        # Notifications tab
        notify_box = self.create_notify_tab()
        notebook.append_page(notify_box, Gtk.Label(label="Notifications"))
        
        # Menu options tab
        menu_box = self.create_menu_tab()
        notebook.append_page(menu_box, Gtk.Label(label="Menu Options"))
        
        # Buttons at bottom
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_halign(Gtk.Align.END)
        
        save_btn = Gtk.Button(label="Save & Restart")
        save_btn.connect("clicked", self.on_save)
        button_box.pack_start(save_btn, False, False, 0)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", self.on_cancel)
        button_box.pack_start(cancel_btn, False, False, 0)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(notebook, True, True, 0)
        main_box.pack_start(button_box, False, False, 0)
        
        self.add(main_box)
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}
    
    def create_general_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(12)
        
        # Update interval
        interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        interval_box.pack_start(Gtk.Label(label="Update Interval (seconds):"), False, False, 0)
        self.interval_spin = Gtk.SpinButton()
        self.interval_spin.set_range(0.5, 10)
        self.interval_spin.set_increments(0.5, 1)
        self.interval_spin.set_value(self.config.get('update_interval', 1))
        interval_box.pack_start(self.interval_spin, False, False, 0)
        box.pack_start(interval_box, False, False, 0)
        
        # Battery device
        device_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        device_box.pack_start(Gtk.Label(label="Battery Device:"), False, False, 0)
        self.device_entry = Gtk.Entry()
        self.device_entry.set_text(self.config.get('battery_device', 'BAT1'))
        device_box.pack_start(self.device_entry, True, True, 0)
        box.pack_start(device_box, False, False, 0)
        
        # Decimal places
        decimal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        decimal_box.pack_start(Gtk.Label(label="Decimal Places:"), False, False, 0)
        self.decimal_spin = Gtk.SpinButton()
        self.decimal_spin.set_range(0, 4)
        self.decimal_spin.set_increments(1, 1)
        self.decimal_spin.set_value(self.config.get('decimal_places', 2))
        decimal_box.pack_start(self.decimal_spin, False, False, 0)
        box.pack_start(decimal_box, False, False, 0)
        
        return box
    
    def create_display_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(12)
        
        # Display format
        format_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        format_box.pack_start(Gtk.Label(label="Display Format:"), False, False, 0)
        self.format_combo = Gtk.ComboBoxText()
        self.format_combo.append("short", "Short (5.23W)")
        self.format_combo.append("detailed", "Detailed (Power: 5.23W)")
        self.format_combo.set_active_id(self.config.get('display_format', 'short'))
        format_box.pack_start(self.format_combo, False, False, 0)
        box.pack_start(format_box, False, False, 0)
        
        # Icon style
        icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon_box.pack_start(Gtk.Label(label="Icon Style:"), False, False, 0)
        self.icon_combo = Gtk.ComboBoxText()
        self.icon_combo.append("battery", "Battery")
        self.icon_combo.append("power", "Power")
        self.icon_combo.append("bolt", "Bolt")
        self.icon_combo.append("chip", "Chip")
        self.icon_combo.set_active_id(self.config.get('icon_style', 'battery'))
        icon_box.pack_start(self.icon_combo, False, False, 0)
        box.pack_start(icon_box, False, False, 0)
        
        # Color coding
        box.pack_start(Gtk.Label(label="Color Coding:", xalign=0), False, False, 0)
        
        color_config = self.config.get('color_coding', {})
        self.color_enabled = Gtk.CheckButton(label="Enable color indicators")
        self.color_enabled.set_active(color_config.get('enabled', True))
        box.pack_start(self.color_enabled, False, False, 0)
        
        # Thresholds
        threshold_grid = Gtk.Grid()
        threshold_grid.set_column_spacing(6)
        threshold_grid.set_row_spacing(6)
        threshold_grid.set_margin_left(20)
        
        threshold_grid.attach(Gtk.Label(label="Low threshold (W):"), 0, 0, 1, 1)
        self.low_spin = Gtk.SpinButton()
        self.low_spin.set_range(0, 50)
        self.low_spin.set_increments(1, 5)
        self.low_spin.set_value(color_config.get('low', 5.0))
        threshold_grid.attach(self.low_spin, 1, 0, 1, 1)
        
        threshold_grid.attach(Gtk.Label(label="Medium threshold (W):"), 0, 1, 1, 1)
        self.medium_spin = Gtk.SpinButton()
        self.medium_spin.set_range(0, 50)
        self.medium_spin.set_increments(1, 5)
        self.medium_spin.set_value(color_config.get('medium', 15.0))
        threshold_grid.attach(self.medium_spin, 1, 1, 1, 1)
        
        threshold_grid.attach(Gtk.Label(label="High threshold (W):"), 0, 2, 1, 1)
        self.high_spin = Gtk.SpinButton()
        self.high_spin.set_range(0, 100)
        self.high_spin.set_increments(1, 5)
        self.high_spin.set_value(color_config.get('high', 25.0))
        threshold_grid.attach(self.high_spin, 1, 2, 1, 1)
        
        box.pack_start(threshold_grid, False, False, 0)
        
        return box
    
    def create_notify_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(12)
        
        notify_config = self.config.get('notify_high_power', {})
        
        self.notify_enabled = Gtk.CheckButton(label="Enable high power notifications")
        self.notify_enabled.set_active(notify_config.get('enabled', False))
        box.pack_start(self.notify_enabled, False, False, 0)
        
        # Notification settings
        notify_grid = Gtk.Grid()
        notify_grid.set_column_spacing(6)
        notify_grid.set_row_spacing(6)
        notify_grid.set_margin_left(20)
        
        notify_grid.attach(Gtk.Label(label="Threshold (W):"), 0, 0, 1, 1)
        self.notify_threshold = Gtk.SpinButton()
        self.notify_threshold.set_range(10, 100)
        self.notify_threshold.set_increments(5, 10)
        self.notify_threshold.set_value(notify_config.get('threshold', 30.0))
        notify_grid.attach(self.notify_threshold, 1, 0, 1, 1)
        
        notify_grid.attach(Gtk.Label(label="Cooldown (seconds):"), 0, 1, 1, 1)
        self.notify_cooldown = Gtk.SpinButton()
        self.notify_cooldown.set_range(60, 600)
        self.notify_cooldown.set_increments(30, 60)
        self.notify_cooldown.set_value(notify_config.get('cooldown', 300))
        notify_grid.attach(self.notify_cooldown, 1, 1, 1, 1)
        
        box.pack_start(notify_grid, False, False, 0)
        
        return box
    
    def create_menu_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(12)
        
        box.pack_start(Gtk.Label(label="Show in menu:", xalign=0), False, False, 0)
        
        self.show_voltage = Gtk.CheckButton(label="Voltage")
        self.show_voltage.set_active(self.config.get('show_voltage', True))
        box.pack_start(self.show_voltage, False, False, 0)
        
        self.show_current = Gtk.CheckButton(label="Current")
        self.show_current.set_active(self.config.get('show_current', True))
        box.pack_start(self.show_current, False, False, 0)
        
        self.show_status = Gtk.CheckButton(label="Battery Status")
        self.show_status.set_active(self.config.get('show_battery_status', True))
        box.pack_start(self.show_status, False, False, 0)
        
        self.show_capacity = Gtk.CheckButton(label="Capacity")
        self.show_capacity.set_active(self.config.get('show_capacity', True))
        box.pack_start(self.show_capacity, False, False, 0)
        
        return box
    
    def on_save(self, widget):
        # Build config
        config = {
            "update_interval": self.interval_spin.get_value(),
            "battery_device": self.device_entry.get_text(),
            "display_format": self.format_combo.get_active_id(),
            "decimal_places": int(self.decimal_spin.get_value()),
            "color_coding": {
                "enabled": self.color_enabled.get_active(),
                "low": self.low_spin.get_value(),
                "medium": self.medium_spin.get_value(),
                "high": self.high_spin.get_value()
            },
            "icon_style": self.icon_combo.get_active_id(),
            "notify_high_power": {
                "enabled": self.notify_enabled.get_active(),
                "threshold": self.notify_threshold.get_value(),
                "cooldown": int(self.notify_cooldown.get_value())
            },
            "show_voltage": self.show_voltage.get_active(),
            "show_current": self.show_current.get_active(),
            "show_battery_status": self.show_status.get_active(),
            "show_capacity": self.show_capacity.get_active()
        }
        
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Show success dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Settings Saved!"
        )
        dialog.format_secondary_text(
            "Please restart the battery monitor for changes to take effect.\n\n"
            "Run: pkill -f battery-power-monitor && ~/.local/bin/battery-power-monitor &"
        )
        dialog.run()
        dialog.destroy()
        
        self.close()
    
    def on_cancel(self, widget):
        self.close()

def main():
    win = ConfigWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
