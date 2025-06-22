"""
Configuration Manager for Network Device Backup Tool

Handles loading and validation of device configurations and application settings.
"""

import yaml
import os
import logging
from typing import Dict, List, Any
from pathlib import Path


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize ConfigManager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.devices_config = None
        self.settings_config = None
        self.logger = logging.getLogger(__name__)

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

    def load_devices_config(self) -> List[Dict[str, Any]]:
        """
        Load device configuration from devices.yaml.

        Returns:
            List of device configuration dictionaries

        Raises:
            FileNotFoundError: If devices.yaml doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        devices_file = self.config_dir / "devices.yaml"

        if not devices_file.exists():
            self._create_sample_devices_config()
            self.logger.warning(f"Created sample devices config at {devices_file}")

        try:
            with open(devices_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.devices_config = config.get('devices', [])
                self._validate_devices_config()
                return self.devices_config

        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing devices.yaml: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading devices config: {e}")
            raise

    def load_settings_config(self) -> Dict[str, Any]:
        """
        Load application settings from settings.yaml.

        Returns:
            Dictionary containing application settings

        Raises:
            FileNotFoundError: If settings.yaml doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        settings_file = self.config_dir / "settings.yaml"

        if not settings_file.exists():
            self._create_sample_settings_config()
            self.logger.warning(f"Created sample settings config at {settings_file}")

        try:
            with open(settings_file, 'r', encoding='utf-8') as file:
                self.settings_config = yaml.safe_load(file)
                self._validate_settings_config()
                return self.settings_config

        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing settings.yaml: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading settings config: {e}")
            raise

    def _validate_devices_config(self):
        """Validate device configuration format."""
        if not isinstance(self.devices_config, list):
            raise ValueError("devices_config must be a list")

        required_fields = ['name', 'ip', 'username', 'password', 'device_type']

        for i, device in enumerate(self.devices_config):
            if not isinstance(device, dict):
                raise ValueError(f"Device {i} must be a dictionary")

            missing_fields = [field for field in required_fields if field not in device]
            if missing_fields:
                raise ValueError(f"Device {i} missing required fields: {missing_fields}")

            # Set default port if not specified
            if 'port' not in device:
                device['port'] = 22

    def _validate_settings_config(self):
        """Validate settings configuration format."""
        if not isinstance(self.settings_config, dict):
            raise ValueError("settings_config must be a dictionary")

        # Set defaults for missing sections
        defaults = {
            'backup': {
                'backup_directory': './backups',
                'retention_days': 7,
                'schedule_day': 'sunday',
                'schedule_time': '02:00'
            },
            'email': {
                'enabled': False,
                'smtp_server': '',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_email': ''
            },
            'logging': {
                'level': 'INFO',
                'log_file': './logs/network_backup.log'
            }
        }

        for section, section_defaults in defaults.items():
            if section not in self.settings_config:
                self.settings_config[section] = section_defaults
            else:
                for key, default_value in section_defaults.items():
                    if key not in self.settings_config[section]:
                        self.settings_config[section][key] = default_value

    def _create_sample_devices_config(self):
        """Create a sample devices configuration file."""
        sample_config = {
            'devices': [
                {
                    'name': 'router-01',
                    'ip': '192.168.1.1',
                    'username': 'admin',
                    'password': 'password123',
                    'device_type': 'cisco_ios',
                    'port': 22
                },
                {
                    'name': 'switch-01',
                    'ip': '192.168.1.2',
                    'username': 'admin',
                    'password': 'password123',
                    'device_type': 'cisco_ios',
                    'port': 22
                }
            ]
        }

        devices_file = self.config_dir / "devices.yaml"
        with open(devices_file, 'w', encoding='utf-8') as file:
            yaml.dump(sample_config, file, default_flow_style=False, indent=2)

    def _create_sample_settings_config(self):
        """Create a sample settings configuration file."""
        sample_config = {
            'backup': {
                'backup_directory': './backups',
                'retention_days': 7,
                'schedule_day': 'sunday',
                'schedule_time': '02:00'
            },
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'your-email@gmail.com',
                'sender_password': 'your-app-password',
                'recipient_email': 'admin@company.com'
            },
            'logging': {
                'level': 'INFO',
                'log_file': './logs/network_backup.log'
            }
        }

        settings_file = self.config_dir / "settings.yaml"
        with open(settings_file, 'w', encoding='utf-8') as file:
            yaml.dump(sample_config, file, default_flow_style=False, indent=2)

    def get_backup_directory(self) -> str:
        """Get the configured backup directory."""
        if not self.settings_config:
            self.load_settings_config()
        return self.settings_config['backup']['backup_directory']

    def get_retention_days(self) -> int:
        """Get the configured retention period in days."""
        if not self.settings_config:
            self.load_settings_config()
        return self.settings_config['backup']['retention_days']

    def get_schedule_info(self) -> tuple:
        """
        Get scheduling information.

        Returns:
            Tuple of (day, time) for scheduling
        """
        if not self.settings_config:
            self.load_settings_config()
        return (
            self.settings_config['backup']['schedule_day'],
            self.settings_config['backup']['schedule_time']
        )

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        if not self.settings_config:
            self.load_settings_config()
        return self.settings_config['email']

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        if not self.settings_config:
            self.load_settings_config()
        return self.settings_config['logging']
