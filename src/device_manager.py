"""
Device Manager for Network Device Backup Tool

Handles SSH connections and communication with network devices.
"""

import logging
from typing import Dict, List, Optional, Tuple
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from netmiko.exceptions import NetmikoBaseException
import paramiko


class DeviceManager:
    """Manages network device connections and operations."""

    def __init__(self):
        """Initialize DeviceManager."""
        self.logger = logging.getLogger(__name__)
        self.active_connections = {}

    def test_connection(self, device_config: Dict) -> Tuple[bool, str]:
        """
        Test connection to a network device.

        Args:
            device_config: Device configuration dictionary

        Returns:
            Tuple of (success_status, message)
        """
        # Create a copy of the device config for Netmiko
        netmiko_config = device_config.copy()

        # Use name if available, otherwise use IP as device identifier
        device_name = netmiko_config.get('name', netmiko_config.get('ip', 'unknown'))

        # Remove 'name' from the config as Netmiko doesn't use it
        if 'name' in netmiko_config:
            del netmiko_config['name']

        # Ensure 'host' is set (Netmiko requires it)
        if 'host' not in netmiko_config:
            netmiko_config['host'] = netmiko_config['ip']

        try:
            connection = ConnectHandler(**netmiko_config)

            # Test basic command
            output = connection.send_command("show version", max_loops=10)
            connection.disconnect()

            if output:
                return True, f"Successfully connected to {device_name}"
            else:
                return False, f"Connected but no output from {device_name}"

        except NetmikoTimeoutException:
            return False, f"Timeout connecting to {device_name}"
        except NetmikoAuthenticationException:
            return False, f"Authentication failed for {device_name}"
        except NetmikoBaseException as e:
            return False, f"SSH error connecting to {device_name}: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error connecting to {device_name}: {str(e)}"

    def get_device_config(self, device_config: Dict) -> Tuple[bool, str, str]:
        """
        Retrieve configuration from a network device.

        Args:
            device_config: Device configuration dictionary

        Returns:
            Tuple of (success_status, configuration_text, error_message)
        """
        # Create a copy of the device config for Netmiko
        netmiko_config = device_config.copy()

        # Use name if available, otherwise use IP as device identifier
        device_name = netmiko_config.get('name', netmiko_config.get('ip', 'unknown'))

        # Remove 'name' from the config as Netmiko doesn't use it
        if 'name' in netmiko_config:
            del netmiko_config['name']

        # Ensure 'host' is set (Netmiko requires it)
        if 'host' not in netmiko_config:
            netmiko_config['host'] = netmiko_config['ip']

        try:
            self.logger.info(f"Connecting to {device_name} ({netmiko_config['ip']})")

            connection = ConnectHandler(**netmiko_config)

            # Get configuration based on device type
            config_command = self._get_config_command(netmiko_config['device_type'])

            self.logger.info(f"Retrieving configuration from {device_name}")
            configuration = connection.send_command(config_command, max_loops=100)

            connection.disconnect()

            if configuration:
                self.logger.info(f"Successfully retrieved configuration from {device_name}")
                return True, configuration, ""
            else:
                error_msg = f"No configuration received from {device_name}"
                self.logger.error(error_msg)
                return False, "", error_msg

        except NetmikoTimeoutException:
            error_msg = f"Timeout connecting to {device_name}"
            self.logger.error(error_msg)
            return False, "", error_msg
        except NetmikoAuthenticationException:
            error_msg = f"Authentication failed for {device_name}"
            self.logger.error(error_msg)
            return False, "", error_msg
        except NetmikoBaseException as e:
            error_msg = f"SSH error connecting to {device_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error retrieving config from {device_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, "", error_msg

    def _get_config_command(self, device_type: str) -> str:
        """
        Get the appropriate configuration command for the device type.

        Args:
            device_type: Type of network device

        Returns:
            Configuration command string
        """
        # Command mapping for different device types
        config_commands = {
            'cisco_ios': 'show running-config',
            'cisco_xe': 'show running-config',
            'cisco_nxos': 'show running-config',
            'cisco_asa': 'show running-config',
            'juniper': 'show configuration',
            'juniper_junos': 'show configuration',
            'arista_eos': 'show running-config',
            'hp_comware': 'display current-configuration',
            'hp_procurve': 'show config',
            'fortinet': 'show full-configuration',
            'paloalto_panos': 'show config running',
            'dell_force10': 'show running-config',
            'dell_powerconnect': 'show running-config',
            'extreme': 'show configuration',
            'extreme_exos': 'show configuration',
            'mikrotik_routeros': '/export',
            'vyos': 'show configuration',
            'linux': 'cat /etc/network/interfaces'  # Example for Linux systems
        }

        # Default to Cisco IOS command if device type not found
        return config_commands.get(device_type.lower(), 'show running-config')

    def test_all_devices(self, devices: List[Dict]) -> List[Tuple[str, bool, str]]:
        """
        Test connections to all devices.

        Args:
            devices: List of device configuration dictionaries

        Returns:
            List of tuples (hostname, success_status, message)
        """
        results = []

        for device in devices:
            device_name = device.get('name', device.get('ip', 'unknown'))
            success, message = self.test_connection(device)
            results.append((device_name, success, message))

        return results

    def backup_all_devices(self, devices: List[Dict]) -> List[Tuple[str, bool, str, str]]:
        """
        Backup configurations from all devices.

        Args:
            devices: List of device configuration dictionaries

        Returns:
            List of tuples (hostname, success_status, configuration, error_message)
        """
        results = []

        for device in devices:
            device_name = device.get('name', device.get('ip', 'unknown'))
            success, config, error = self.get_device_config(device)
            results.append((device_name, success, config, error))

        return results

    def get_device_info(self, device_config: Dict) -> Tuple[bool, Dict, str]:
        """
        Get basic device information.

        Args:
            device_config: Device configuration dictionary

        Returns:
            Tuple of (success_status, device_info_dict, error_message)
        """
        # Create a copy of the device config for Netmiko
        netmiko_config = device_config.copy()

        # Use name if available, otherwise use IP as device identifier
        device_name = netmiko_config.get('name', netmiko_config.get('ip', 'unknown'))

        # Remove 'name' from the config as Netmiko doesn't use it
        if 'name' in netmiko_config:
            del netmiko_config['name']

        # Ensure 'host' is set (Netmiko requires it)
        if 'host' not in netmiko_config:
            netmiko_config['host'] = netmiko_config['ip']

        try:
            connection = ConnectHandler(**netmiko_config)

            # Get device information
            version_output = connection.send_command("show version", max_loops=10)

            device_info = {
                'name': device_name,
                'ip': netmiko_config['ip'],
                'device_type': netmiko_config['device_type'],
                'version_info': version_output
            }

            connection.disconnect()

            return True, device_info, ""

        except Exception as e:
            error_msg = f"Error getting device info from {device_name}: {str(e)}"
            self.logger.error(error_msg)
            return False, {}, error_msg

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Network Device Backup Tool")
    parser.add_argument("--backup", action="store_true", help="Backup device configurations")
    parser.add_argument("--test", action="store_true", help="Test device connections")
    parser.add_argument("--devices", type=str, help="Comma-separated list of device IPs or hostnames")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Device manager instance
    manager = DeviceManager()

    # Device list (for demonstration, this should be loaded from a config file or input source)
    device_list = [
        {'ip': '192.168.1.1', 'device_type': 'cisco_ios', 'username': 'admin', 'password': 'password'},
        {'ip': '192.168.1.2', 'device_type': 'cisco_ios', 'username': 'admin', 'password': 'password'},
        # Add more devices as needed
    ]

    if args.devices:
        # Split device IPs/hostnames by comma and strip whitespace
        device_list = [device.strip() for device in args.devices.split(',')]

        # For each device, add default device_type, username, and password
        for i in range(len(device_list)):
            device_list[i] = {
                'ip': device_list[i],
                'device_type': 'cisco_ios',  # Default device type
                'username': 'admin',         # Default username
                'password': 'password'       # Default password
            }

    if args.backup:
        logging.info("Starting configuration backup for all devices...")
        backup_results = manager.backup_all_devices(device_list)

        for hostname, success, config, error in backup_results:
            if success:
                logging.info(f"Backup successful for {hostname}")
            else:
                logging.error(f"Backup failed for {hostname}: {error}")

    if args.test:
        logging.info("Testing connections to all devices...")
        test_results = manager.test_all_devices(device_list)

        for hostname, success, message in test_results:
            if success:
                logging.info(f"Connection successful to {hostname}")
            else:
                logging.error(f"Connection failed to {hostname}: {message}")
