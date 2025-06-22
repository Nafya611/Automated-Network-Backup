import logging
import argparse
from src.config_manager import ConfigManager
from src.backup_manager import BackupManager
from src.scheduler import BackupScheduler, SimpleScheduler
from src.email_notifier import EmailNotifier
import os

def setup_logging(logging_config):
    log_file = logging_config.get('log_file', './logs/network_backup.log')
    log_level = getattr(logging, logging_config.get('level', 'INFO').upper(), logging.INFO)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger().addHandler(logging.StreamHandler())

def main():
    parser = argparse.ArgumentParser(description="Network Device Backup Tool")
    parser.add_argument('--backup', action='store_true', help='Run a one-time backup now')
    parser.add_argument('--schedule', action='store_true', help='Start the backup scheduler')
    parser.add_argument('--test', action='store_true', help='Test device connections')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    args = parser.parse_args()

    config_manager = ConfigManager()
    settings = config_manager.load_settings_config()
    setup_logging(settings['logging'])
    logger = logging.getLogger('main')

    backup_manager = BackupManager(config_manager)
    email_notifier = EmailNotifier(settings['email'])

    def backup_and_notify():
        success, fail, errors = backup_manager.run_backup()
        email_notifier.send_backup_report(success, fail, errors)

    if args.backup:
        logger.info("Running one-time backup...")
        backup_and_notify()
    elif args.schedule:
        logger.info("Starting backup scheduler...")
        try:
            # Prefer APScheduler, fallback to schedule
            try:
                scheduler = BackupScheduler(config_manager, backup_and_notify)
                scheduler.start_scheduler()
            except ImportError:
                logger.warning("APScheduler not available, using simple scheduler.")
                scheduler = SimpleScheduler(config_manager, backup_and_notify)
                scheduler.start_scheduler()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
    elif args.test:
        logger.info("Testing device connections...")
        results = backup_manager.test_devices()
        for hostname, success, message in results:
            status = "OK" if success else "FAIL"
            print(f"{hostname}: {status} - {message}")
    elif args.config:
        print("\nDevice Configuration:")
        for device in config_manager.load_devices_config():
            print(device)
        print("\nSettings:")
        print(settings)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
