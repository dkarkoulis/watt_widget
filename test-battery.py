#!/usr/bin/env python3
"""
Quick test script to verify battery power monitoring works
"""

import os
from pathlib import Path

print("🔍 Battery Power Monitor - System Check")
print("=" * 50)

# Check for battery devices
print("\n1. Checking for battery devices...")
power_supply = Path("/sys/class/power_supply")

if not power_supply.exists():
    print("   ❌ No power supply directory found!")
    exit(1)

batteries = []
for device in power_supply.iterdir():
    voltage_file = device / "voltage_now"
    current_file = device / "current_now"
    
    if voltage_file.exists() and current_file.exists():
        batteries.append(device.name)
        print(f"   ✅ Found battery: {device.name}")

if not batteries:
    print("   ❌ No compatible batteries found!")
    print("   Available devices:")
    for device in power_supply.iterdir():
        print(f"      - {device.name}")
    exit(1)

# Test reading power from first battery
battery = batteries[0]
battery_path = power_supply / battery

print(f"\n2. Testing power reading from {battery}...")

try:
    with open(battery_path / "voltage_now") as f:
        voltage = int(f.read().strip())
    with open(battery_path / "current_now") as f:
        current = int(f.read().strip())
    
    power = (voltage * current) / 1_000_000_000_000
    
    print(f"   ✅ Voltage: {voltage/1_000_000:.2f} V")
    print(f"   ✅ Current: {current/1_000_000:.2f} A")
    print(f"   ✅ Power: {power:.2f} W")
    
except Exception as e:
    print(f"   ❌ Error reading battery: {e}")
    exit(1)

# Check for optional info
print(f"\n3. Checking additional battery info...")

for info_file in ["status", "capacity", "energy_now", "energy_full"]:
    file_path = battery_path / info_file
    if file_path.exists():
        try:
            with open(file_path) as f:
                value = f.read().strip()
            print(f"   ✅ {info_file}: {value}")
        except:
            pass

# Check Python dependencies
print("\n4. Checking Python dependencies...")

try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import Gtk, AppIndicator3
    print("   ✅ GTK and AppIndicator3 available")
except Exception as e:
    print(f"   ❌ Missing dependencies: {e}")
    print("   Install with: sudo apt install python3-gi gir1.2-appindicator3-0.1")

# Check for notify-send
print("\n5. Checking notification support...")
if os.system("which notify-send > /dev/null 2>&1") == 0:
    print("   ✅ notify-send available")
else:
    print("   ⚠️  notify-send not found (optional)")
    print("   Install with: sudo apt install libnotify-bin")

print("\n" + "=" * 50)
print("✅ System check complete!")
print("\nYour battery device is:", battery)
print("You can now run: ./install-mate.sh")
