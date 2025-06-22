"""
Scheduler for Network Device Backup Tool

Handles automated scheduling of backup operations.
"""

import logging
import time
from datetime import datetime
from typing import Callable
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .config_manager import ConfigManager


class BackupScheduler:
    """Manages automated backup scheduling."""

    def __init__(self, config_manager: ConfigManager, backup_function: Callable):
        """
        Initialize BackupScheduler.

        Args:
            config_manager: ConfigManager instance
            backup_function: Function to call for backups
        """
        self.config_manager = config_manager
        self.backup_function = backup_function
        self.scheduler = BlockingScheduler()
        self.logger = logging.getLogger(__name__)

    def start_scheduler(self):
        """Start the backup scheduler."""
        try:
            # Get schedule configuration
            schedule_day, schedule_time = self.config_manager.get_schedule_info()

            # Parse schedule time (format: HH:MM)
            hour, minute = map(int, schedule_time.split(':'))

            # Map day names to weekday numbers (Monday=0, Sunday=6)
            day_mapping = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }

            weekday = day_mapping.get(schedule_day.lower())
            if weekday is None:
                raise ValueError(f"Invalid schedule day: {schedule_day}")            # Create cron trigger for weekly scheduling
            trigger = CronTrigger(
                day_of_week=weekday,
                hour=hour,
                minute=minute
            )

            # Add the backup job
            self.scheduler.add_job(
                func=self.backup_function,
                trigger=trigger,
                id='weekly_backup',
                name='Weekly Network Device Backup',
                replace_existing=True
            )

            self.logger.info(f"Scheduler configured for {schedule_day}s at {schedule_time}")
            self.logger.info("Starting backup scheduler...")

            # Try to log next run time (handle API changes)
            try:
                job = self.scheduler.get_job('weekly_backup')
                if hasattr(job, 'next_run_time'):
                    next_run = job.next_run_time
                    self.logger.info(f"Next backup scheduled for: {next_run}")
                else:
                    self.logger.info(f"Next backup scheduled for {schedule_day}s at {schedule_time}")
            except Exception as e:
                self.logger.warning(f"Could not determine next run time: {e}")

            # Start the scheduler (this will block)
            self.scheduler.start()

        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
            self.stop_scheduler()
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {str(e)}")
            raise

    def stop_scheduler(self):
        """Stop the backup scheduler."""
        if self.scheduler.running:
            self.logger.info("Stopping backup scheduler...")
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")

    def get_next_run_time(self) -> str:
        """
        Get the next scheduled run time.

        Returns:
            String representation of next run time
        """
        try:
            job = self.scheduler.get_job('weekly_backup')
            if job:
                return str(job.next_run_time)
            else:
                return "No job scheduled"
        except Exception:
            return "Unknown"

    def run_immediate_backup(self):
        """Run an immediate backup outside of the schedule."""
        self.logger.info("Running immediate backup...")
        try:
            self.backup_function()
        except Exception as e:
            self.logger.error(f"Error during immediate backup: {str(e)}")
            raise


class SimpleScheduler:
    """Simple scheduler using the schedule library for basic scheduling needs."""

    def __init__(self, config_manager: ConfigManager, backup_function: Callable):
        """
        Initialize SimpleScheduler.

        Args:
            config_manager: ConfigManager instance
            backup_function: Function to call for backups
        """
        self.config_manager = config_manager
        self.backup_function = backup_function
        self.logger = logging.getLogger(__name__)
        self.running = False

    def start_scheduler(self):
        """Start the simple scheduler."""
        try:
            import schedule

            # Get schedule configuration
            schedule_day, schedule_time = self.config_manager.get_schedule_info()

            # Schedule the backup job
            if schedule_day.lower() == 'sunday':
                schedule.every().sunday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'monday':
                schedule.every().monday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'tuesday':
                schedule.every().tuesday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'wednesday':
                schedule.every().wednesday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'thursday':
                schedule.every().thursday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'friday':
                schedule.every().friday.at(schedule_time).do(self.backup_function)
            elif schedule_day.lower() == 'saturday':
                schedule.every().saturday.at(schedule_time).do(self.backup_function)
            else:
                raise ValueError(f"Invalid schedule day: {schedule_day}")

            self.logger.info(f"Simple scheduler configured for {schedule_day}s at {schedule_time}")
            self.logger.info("Starting simple backup scheduler...")

            self.running = True

            # Run the scheduler loop
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("Simple scheduler stopped by user")
            self.stop_scheduler()
        except Exception as e:
            self.logger.error(f"Error starting simple scheduler: {str(e)}")
            raise

    def stop_scheduler(self):
        """Stop the simple scheduler."""
        self.running = False
        self.logger.info("Simple scheduler stopped")

    def run_immediate_backup(self):
        """Run an immediate backup outside of the schedule."""
        self.logger.info("Running immediate backup...")
        try:
            self.backup_function()
        except Exception as e:
            self.logger.error(f"Error during immediate backup: {str(e)}")
            raise
