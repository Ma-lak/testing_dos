import os
import time
import subprocess

def get_bluetooth_interface():
    os.system('clear')
    logo()
    print("")
    
    try:
        # Get controllers using bluetoothctl
        result = subprocess.run(
            ['bluetoothctl', 'list'],
            text=True,
            capture_output=True
        )
        
        output = result.stdout.strip()
        
        if not output:
            print("[!] No Bluetooth controllers found.")
            print("[!] Make sure a Bluetooth adapter is connected.")
            print("[!] Try: sudo systemctl start bluetooth")
            exit(1)
        
        # Parse bluetoothctl list output
        # Output format: "Controller XX:XX:XX:XX:XX:XX name [default]"
        controllers = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                mac = parts[1]
                name = ' '.join(parts[2:]).replace('[default]', '').strip()
                controllers.append((mac, name))
        
        print("Available Bluetooth Controllers:")
        print("")
        print(f"{'ID':<5} {'MAC Address':<20} {'Name'}")
        print("-" * 45)
        for idx, (mac, name) in enumerate(controllers, 1):
            print(f"{idx:<5} {mac:<20} {name}")
        print("")
        
        # Let user pick by ID or enter MAC directly
        choice = input("Enter controller ID or MAC address (default: 1): ").strip()
        
        if not choice or choice == '1':
            selected_mac = controllers[0][0]
        elif choice.isdigit():
            selected_mac = controllers[int(choice) - 1][0]
        else:
            selected_mac = choice  # assume they typed a MAC directly
        
        # Convert MAC to hciX format for tools like hcitool/l2flood
        # Find the hciX name via sys
        hci_interface = mac_to_hci(selected_mac)
        print(f"\n[*] Using interface: {hci_interface} ({selected_mac})")
        return hci_interface

    except FileNotFoundError:
        print("[!] 'bluetoothctl' not found. Install with: sudo apt install bluez")
        exit(1)
    except IndexError:
        print("[!] Invalid selection.")
        exit(1)


def mac_to_hci(mac):
    """Map a controller MAC address to its hciX interface name via sysfs."""
    try:
        base = '/sys/class/bluetooth'
        for iface in os.listdir(base):
            addr_file = os.path.join(base, iface, 'address')
            if os.path.exists(addr_file):
                with open(addr_file) as f:
                    if f.read().strip().upper() == mac.upper():
                        return iface  # e.g. "hci0"
    except Exception:
        pass
    # Fallback: just return hci0
    return 'hci0'