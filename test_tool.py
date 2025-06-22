#!/usr/bin/env python3
"""
Test script for Network Device Backup Tool

Run basic tests to verify the tool is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigManager
from src.backup_manager import BackupManager
from src.email_notifier import EmailNotifier
import logging

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    try:
        config_manager = ConfigManager()

        # Test settings loading
        settings = config_manager.load_settings_config()
        print(f"✓ Settings loaded: {len(settings)} sections")

        # Test devices loading
        devices = config_manager.load_devices_config()
        print(f"✓ Devices loaded: {len(devices)} devices")

        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_backup_manager():
    """Test backup manager initialization."""
    print("\nTesting backup manager...")
    try:
        config_manager = ConfigManager()
        backup_manager = BackupManager(config_manager)

        # Test backup statistics
        stats = backup_manager.get_backup_statistics()
        print(f"✓ Backup manager initialized")
        print(f"  Current backup count: {stats['total_backups']}")

        return True
    except Exception as e:
        print(f"✗ Backup manager test failed: {e}")
        return False

def test_email_notifier():
    """Test email notifier."""
    print("\nTesting email notifier...")
    try:
        config_manager = ConfigManager()
        settings = config_manager.load_settings_config()
        email_notifier = EmailNotifier(settings['email'])

        print(f"✓ Email notifier initialized")
        print(f"  Email enabled: {email_notifier.enabled}")

        return True
    except Exception as e:
        print(f"✗ Email notifier test failed: {e}")
        return False

def test_device_connections():
    """Test device connections (if configured)."""
    print("\nTesting device connections...")
    try:
        config_manager = ConfigManager()
        backup_manager = BackupManager(config_manager)

        # Test device connections
        results = backup_manager.test_devices()

        print(f"✓ Connection test completed")
        for hostname, success, message in results:
            status = "✓" if success else "✗"
            print(f"  {status} {hostname}: {message}")

        return True
    except Exception as e:
        print(f"✗ Device connection test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Network Device Backup Tool - Test Suite")
    print("=" * 60)

    tests = [
        test_config_loading,
        test_backup_manager,
        test_email_notifier,
        test_device_connections
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed! The backup tool is ready to use.")
        print("\nNext steps:")
        print("1. Edit config/devices.yaml with your actual device information")
        print("2. Configure email settings in config/settings.yaml (optional)")
        print("3. Run: python main.py --test (to test device connections)")
        print("4. Run: python main.py --backup (for manual backup)")
        print("5. Run: python main.py --schedule (to start automated backups)")
    else:
        print("✗ Some tests failed. Please check the configuration.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
