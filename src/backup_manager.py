"""
Backup Manager for Network Device Backup Tool

Handles the backup process, file management, and cleanup operations.
"""

import os
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from .device_manager import DeviceManager
from .config_manager import ConfigManager


class BackupManager:
    """Manages network device backup operations."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize BackupManager.

        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.device_manager = DeviceManager()
        self.logger = logging.getLogger(__name__)

        # Create backup directory if it doesn't exist
        self.backup_dir = Path(self.config_manager.get_backup_directory())
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def run_backup(self) -> Tuple[int, int, List[str]]:
        """
        Run backup for all configured devices.

        Returns:
            Tuple of (successful_backups, failed_backups, error_messages)
        """
        self.logger.info("Starting backup process")

        # Load device configurations
        try:
            devices = self.config_manager.load_devices_config()
        except Exception as e:
            error_msg = f"Error loading device configuration: {e}"
            self.logger.error(error_msg)
            return 0, 0, [error_msg]

        if not devices:
            error_msg = "No devices configured for backup"
            self.logger.warning(error_msg)
            return 0, 0, [error_msg]

        successful_backups = 0
        failed_backups = 0
        error_messages = []

        # Get current timestamp for backup files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")        # Backup each device
        for device in devices:
            device_name = device.get('name', device.get('ip', 'unknown'))

            try:
                self.logger.info(f"Backing up {device_name}")

                # Get device configuration
                success, config, error_msg = self.device_manager.get_device_config(device)

                if success and config:
                    # Save configuration to file
                    backup_filename = f"{device_name}_{timestamp}.txt"
                    backup_filepath = self.backup_dir / backup_filename

                    with open(backup_filepath, 'w', encoding='utf-8') as backup_file:
                        backup_file.write(f"# Configuration backup for {device_name}\n")
                        backup_file.write(f"# Backup date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        backup_file.write(f"# Device IP: {device['ip']}\n")
                        backup_file.write(f"# Device Type: {device['device_type']}\n")
                        backup_file.write("#" + "="*70 + "\n\n")
                        backup_file.write(config)

                    self.logger.info(f"Successfully backed up {device_name} to {backup_filename}")
                    successful_backups += 1

                else:
                    error_msg = error_msg or f"Failed to retrieve configuration from {device_name}"
                    self.logger.error(error_msg)
                    error_messages.append(error_msg)
                    failed_backups += 1

            except Exception as e:
                error_msg = f"Unexpected error backing up {device_name}: {str(e)}"
                self.logger.error(error_msg)
                error_messages.append(error_msg)
                failed_backups += 1

        # Clean up old backups
        try:
            self.cleanup_old_backups()
        except Exception as e:
            error_msg = f"Error during backup cleanup: {str(e)}"
            self.logger.error(error_msg)
            error_messages.append(error_msg)

        self.logger.info(f"Backup process completed: {successful_backups} successful, {failed_backups} failed")

        return successful_backups, failed_backups, error_messages

    def cleanup_old_backups(self):
        """Remove backup files older than the configured retention period."""
        retention_days = self.config_manager.get_retention_days()
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.logger.info(f"Cleaning up backups older than {retention_days} days")

        deleted_count = 0

        try:
            for backup_file in self.backup_dir.glob("*.txt"):
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    self.logger.info(f"Deleting old backup: {backup_file.name}")
                    backup_file.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                self.logger.info(f"Deleted {deleted_count} old backup files")
            else:
                self.logger.info("No old backup files to delete")

        except Exception as e:
            self.logger.error(f"Error during backup cleanup: {str(e)}")
            raise

    def get_backup_statistics(self) -> Dict:
        """
        Get statistics about existing backups.

        Returns:
            Dictionary containing backup statistics
        """
        stats = {
            'total_backups': 0,
            'devices': {},
            'oldest_backup': None,
            'newest_backup': None,
            'total_size_mb': 0
        }

        try:
            backup_files = list(self.backup_dir.glob("*.txt"))
            stats['total_backups'] = len(backup_files)

            if backup_files:
                total_size = 0
                oldest_time = None
                newest_time = None

                for backup_file in backup_files:
                    # Get file size
                    file_size = backup_file.stat().st_size
                    total_size += file_size

                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                    if oldest_time is None or file_mtime < oldest_time:
                        oldest_time = file_mtime
                        stats['oldest_backup'] = backup_file.name

                    if newest_time is None or file_mtime > newest_time:
                        newest_time = file_mtime
                        stats['newest_backup'] = backup_file.name

                    # Count backups per device
                    device_name = backup_file.name.split('_')[0]
                    if device_name not in stats['devices']:
                        stats['devices'][device_name] = 0
                    stats['devices'][device_name] += 1

                stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)

        except Exception as e:
            self.logger.error(f"Error getting backup statistics: {str(e)}")

        return stats

    def test_devices(self) -> List[Tuple[str, bool, str]]:
        """
        Test connections to all configured devices.

        Returns:
            List of tuples (hostname, success_status, message)
        """
        try:
            devices = self.config_manager.load_devices_config()
            return self.device_manager.test_all_devices(devices)
        except Exception as e:
            self.logger.error(f"Error testing devices: {str(e)}")
            return [("error", False, f"Error loading device configuration: {str(e)}")]

    def list_backup_files(self) -> List[Dict]:
        """
        List all backup files with details.

        Returns:
            List of dictionaries containing backup file information
        """
        backup_files = []

        try:
            for backup_file in sorted(self.backup_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True):
                file_stat = backup_file.stat()

                backup_info = {
                    'filename': backup_file.name,
                    'device': backup_file.name.split('_')[0],
                    'timestamp': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size_kb': round(file_stat.st_size / 1024, 2),
                    'age_days': (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).days
                }

                backup_files.append(backup_info)

        except Exception as e:
            self.logger.error(f"Error listing backup files: {str(e)}")

        return backup_files
