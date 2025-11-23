# network/interface_bind.py
import socket
import requests
from requests.adapters import HTTPAdapter
import logging
import subprocess
import re

logger = logging.getLogger(__name__)

# Try to import netifaces, but make it optional
try:
    import netifaces
    NETIFACES_AVAILABLE = True
    logger.debug("netifaces available - using for interface detection")
except ImportError:
    NETIFACES_AVAILABLE = False
    logger.warning("netifaces not available - will use system commands for interface detection")

class InterfaceBinder:
    def __init__(self):
        self.available_interfaces = self.detect_interfaces()
    
    def detect_interfaces_netifaces(self):
        """Detect available network interfaces using netifaces"""
        interfaces = []
        try:
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get('addr', '')
                        if ip and ip != '127.0.0.1':
                            interface_type = 'VPN' if any(x in iface for x in ['tun', 'tap', 'wg', 'ppp']) else 'Other'
                            interfaces.append({
                                'name': iface,
                                'ip': ip,
                                'type': interface_type
                            })
            logger.debug(f"Found {len(interfaces)} interfaces using netifaces")
        except Exception as e:
            logger.error(f"netifaces detection failed: {e}")
        return interfaces
    
    def detect_interfaces_ip_command(self):
        """Detect available network interfaces using system ip command"""
        interfaces = []
        try:
            # Try using 'ip' command (Linux)
            result = subprocess.run(['ip', 'addr', 'show'], 
                                  capture_output=True, text=True, check=True)
            
            current_interface = None
            for line in result.stdout.split('\n'):
                # Look for interface lines: "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> ..."
                interface_match = re.match(r'^\d+:\s+([^:]+):', line)
                if interface_match:
                    current_interface = interface_match.group(1)
                
                # Look for IP address lines: "    inet 192.168.1.100/24 ..."
                ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match and current_interface:
                    ip = ip_match.group(1)
                    if ip != '127.0.0.1':
                        interface_type = 'VPN' if any(x in current_interface for x in ['tun', 'tap', 'wg', 'ppp']) else 'Other'
                        interfaces.append({
                            'name': current_interface,
                            'ip': ip,
                            'type': interface_type
                        })
            
            logger.debug(f"Found {len(interfaces)} interfaces using ip command")
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"ip command failed: {e}")
            # Final fallback - basic socket detection
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip != '127.0.0.1':
                    interfaces.append({
                        'name': 'default',
                        'ip': local_ip,
                        'type': 'Other'
                    })
                    logger.debug("Found interface using socket fallback")
            except socket.gaierror:
                logger.warning("Could not detect network interfaces with any method")
        
        return interfaces
    
    def detect_interfaces(self):
        """Detect available network interfaces using best available method"""
        if NETIFACES_AVAILABLE:
            interfaces = self.detect_interfaces_netifaces()
            if interfaces:  # If netifaces found interfaces, use them
                return interfaces
        
        # Fallback to ip command if netifaces not available or found nothing
        return self.detect_interfaces_ip_command()
    
    def bind_to_interface(self, session, interface_name):
        """Bind requests session to specific interface (Linux only)"""
        if not hasattr(socket, 'SO_BINDTODEVICE'):
            return session  # Not supported on this platform
            
        class BoundAdapter(HTTPAdapter):
            def __init__(self, interface, *args, **kwargs):
                self.interface = interface
                super().__init__(*args, **kwargs)
            
            def init_poolmanager(self, *args, **kwargs):
                if hasattr(socket, 'SO_BINDTODEVICE'):
                    kwargs['socket_options'] = [
                        (socket.SOL_SOCKET, socket.SO_BINDTODEVICE, 
                         self.interface.encode() + b'\x00')
                    ]
                super().init_poolmanager(*args, **kwargs)
        
        adapter = BoundAdapter(interface_name)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def is_linux(self):
        """Check if running on Linux"""
        return hasattr(socket, 'SO_BINDTODEVICE')