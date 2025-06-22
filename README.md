# Network Device Backup Tool

A comprehensive Python-based tool for backing up configurations from network devices (routers, switches, etc.) with automated scheduling and management features.

## Features

- **Multi-Device Support**: Connect to multiple network devices via SSH
- **Automated Scheduling**: Weekly backups every Sunday with configurable time
- **Intelligent Storage Management**: Automatic cleanup of backups older than 1 week
- **Comprehensive Logging**: Detailed logging of all backup operations
- **Email Notifications**: Optional email alerts for backup success/failure
- **Flexible Configuration**: Easy device management via YAML configuration files

## Requirements

- Python 3.7+
- Network devices accessible via SSH
- SMTP server for email notifications (optional)

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Devices**
   - Edit `config/devices.yaml` with your actual network device information
   - See `config/devices.yaml.example` for supported device types

4. **Test the Setup**
   ```bash
   python test_tool.py
   ```

5. **Test Device Connections**
   ```powershell
   python main.py --test
   ```

6. **Run Your First Backup**
   ```powershell
   python main.py --backup
   ```

7. **Start Automated Backups**
   ```powershell
   python main.py --schedule
   ```

**Or use the interactive startup script:**
```powershell
start.bat
```

## Configuration

### Device Configuration

Create a `devices.yaml` file in the `config/` directory:

```yaml
devices:
  - hostname: "router-01"
    ip: "192.168.1.1"
    username: "admin"
    password: "password123"
    device_type: "cisco_ios"
    port: 22

  - hostname: "switch-01"
    ip: "192.168.1.2"
    username: "admin"
    password: "password123"
    device_type: "cisco_ios"
    port: 22
```

### Application Settings

Configure settings in `config/settings.yaml`:

```yaml
backup:
  backup_directory: "./backups"
  retention_days: 7
  schedule_day: "sunday"
  schedule_time: "02:00"

email:
  enabled: false
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-password"
  recipient_email: "admin@company.com"

logging:
  level: "INFO"
  log_file: "./logs/network_backup.log"
```

## Usage

### Manual Backup

Run a one-time backup of all configured devices:

```bash
python main.py --backup
```

### Start Scheduler

Start the automated weekly backup scheduler:

```bash
python main.py --schedule
```

### Configuration Management

```bash
# Test device connections
python main.py --test

# View current configuration
python main.py --config
```

## Project Structure

```
network backup/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config/
│   ├── devices.yaml        # Device configuration
│   └── settings.yaml       # Application settings
├── src/
│   ├── __init__.py
│   ├── backup_manager.py   # Core backup functionality
│   ├── device_manager.py   # Device connection management
│   ├── scheduler.py        # Backup scheduling
│   ├── config_manager.py   # Configuration management
│   └── email_notifier.py   # Email notification system
├── backups/                # Backup storage directory
├── logs/                   # Application logs
└── README.md              # This file
```

## Supported Device Types

The tool supports various network device types through netmiko:

- Cisco IOS/IOS-XE
- Cisco NX-OS
- Juniper JunOS
- Arista EOS
- HP ProCurve
- And many more...

## Logging

All backup operations are logged with timestamps, device information, and operation status. Logs are stored in `logs/network_backup.log`.

## Email Notifications

Configure SMTP settings in `config/settings.yaml` to receive email notifications about backup operations. The system will notify you of:

- Successful backup completions
- Failed backup attempts
- Storage cleanup operations

## Security Considerations

- Store device credentials securely
- Use SSH keys where possible instead of passwords
- Restrict access to configuration files
- Consider using environment variables for sensitive data
