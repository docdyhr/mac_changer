# MAC Address Backup and Restore Procedures

## Overview

This document provides comprehensive procedures for backing up and restoring MAC addresses when using the MAC Address Changer tool. Following these procedures ensures safe MAC address changes with the ability to restore original configurations.

## Table of Contents

- [Quick Start](#quick-start)
- [Backup Procedures](#backup-procedures)
- [Restore Procedures](#restore-procedures)
- [Verification](#verification)
- [Emergency Rollback](#emergency-rollback)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Quick Start

### Before Any MAC Address Change

```bash
# 1. Create a backup
python scripts/backup_restore.py backup

# 2. Verify backup
python scripts/backup_restore.py verify --name <backup_name>

# 3. Make your MAC address change
sudo python mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff

# 4. If needed, restore original
python scripts/backup_restore.py restore --name <backup_name>
```

## Backup Procedures

### Automatic Backup

The MAC Address Changer automatically creates backups before making changes when auto-backup is enabled:

```bash
# Check if auto-backup is enabled
python scripts/backup_restore.py list

# Enable auto-backup (default)
# Edit backups/mac_addresses/config.json:
{
  "auto_backup": true,
  "backup_retention_days": 30,
  "max_backups": 100
}
```

### Manual Backup

#### Create Named Backup

```bash
# Create backup with specific name
python scripts/backup_restore.py backup --name production_backup

# Create backup with timestamp (automatic naming)
python scripts/backup_restore.py backup
```

#### Create Pre-Change Backup

```bash
# Before changing MAC addresses
python scripts/backup_restore.py backup --name pre_change_$(date +%Y%m%d_%H%M%S)
```

### Backup Verification

Always verify backups after creation:

```bash
# Verify specific backup
python scripts/backup_restore.py verify --name production_backup

# List all backups
python scripts/backup_restore.py list
```

### Backup Contents

Each backup contains:
- **Interface Information**: All network interfaces and their MAC addresses
- **System Information**: Hostname, OS, architecture
- **Timestamps**: Creation time and timezone
- **Checksums**: Integrity verification data
- **Metadata**: Tool version and backup format

## Restore Procedures

### Full System Restore

Restore all interfaces to their backed-up state:

```bash
# Restore all interfaces
sudo python scripts/backup_restore.py restore --name production_backup

# Dry run to see what would be restored
python scripts/backup_restore.py restore --name production_backup --dry-run
```

### Selective Interface Restore

Restore specific interfaces only:

```bash
# Restore single interface
sudo python scripts/backup_restore.py restore --name production_backup --interface eth0

# Restore multiple interfaces
sudo python scripts/backup_restore.py restore --name production_backup --interface eth0 --interface wlan0
```

### Interactive Restore

For interactive restoration with confirmation:

```bash
# Interactive restore with prompts
sudo python scripts/backup_restore.py restore --name production_backup
# Will prompt: "Are you sure you want to restore MAC addresses? (y/N):"
```

## Verification

### Backup Integrity Check

```bash
# Verify backup integrity
python scripts/backup_restore.py verify --name production_backup

# Check all backups
for backup in $(python scripts/backup_restore.py list | grep "✅" | awk '{print $2}'); do
    echo "Verifying $backup..."
    python scripts/backup_restore.py verify --name $backup
done
```

### Post-Restore Verification

After restoration, verify MAC addresses:

```bash
# Check current MAC addresses
python mac_changer.py -l

# Compare with backup
python scripts/backup_restore.py verify --name production_backup

# Verify specific interface
python mac_changer.py -i eth0 -c
```

## Emergency Rollback

### Immediate Rollback

If MAC address change causes issues:

```bash
# 1. Find latest backup
python scripts/backup_restore.py list

# 2. Restore immediately
sudo python scripts/backup_restore.py restore --name <latest_backup>

# 3. Verify network connectivity
ping -c 4 8.8.8.8
```

### Network Loss Recovery

If you lose network connectivity:

```bash
# 1. Use local console access
# 2. List available backups
python scripts/backup_restore.py list

# 3. Restore from most recent backup
sudo python scripts/backup_restore.py restore --name <backup_name>

# 4. Restart network services
sudo systemctl restart networking  # Ubuntu/Debian
sudo systemctl restart network     # CentOS/RHEL
```

### System Recovery

For system-wide recovery:

```bash
# 1. Boot from recovery media if needed
# 2. Mount system partition
# 3. Navigate to project directory
# 4. Restore original MAC addresses
sudo python scripts/backup_restore.py restore --name <original_backup>
```

## Best Practices

### Before Making Changes

1. **Always create a backup**:
   ```bash
   python scripts/backup_restore.py backup --name pre_change_$(date +%Y%m%d_%H%M%S)
   ```

2. **Verify backup integrity**:
   ```bash
   python scripts/backup_restore.py verify --name <backup_name>
   ```

3. **Test with dry-run**:
   ```bash
   python mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff --dry-run
   ```

### During Changes

1. **Monitor network connectivity**:
   ```bash
   # Keep a ping running in another terminal
   ping -i 1 8.8.8.8
   ```

2. **Have console access ready**:
   - Physical console access
   - IPMI/iDRAC access
   - Serial console

3. **Change one interface at a time**:
   ```bash
   # Don't change multiple interfaces simultaneously
   sudo python mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff
   # Verify connectivity before proceeding to next interface
   ```

### After Changes

1. **Verify functionality**:
   ```bash
   # Test network connectivity
   ping -c 4 8.8.8.8
   
   # Check interface status
   python mac_changer.py -l
   
   # Verify services are running
   sudo systemctl status networking
   ```

2. **Create post-change backup**:
   ```bash
   python scripts/backup_restore.py backup --name post_change_$(date +%Y%m%d_%H%M%S)
   ```

### Regular Maintenance

1. **Clean up old backups**:
   ```bash
   python scripts/backup_restore.py cleanup
   ```

2. **Export important backups**:
   ```bash
   python scripts/backup_restore.py export --name production_backup --output /backup/location/
   ```

3. **Verify backup integrity regularly**:
   ```bash
   # Weekly verification script
   #!/bin/bash
   for backup in $(python scripts/backup_restore.py list | grep "✅" | awk '{print $2}'); do
       python scripts/backup_restore.py verify --name $backup
   done
   ```

## Troubleshooting

### Common Issues

#### Backup Creation Fails

**Problem**: Cannot create backup
```bash
Error: Failed to get interfaces: Permission denied
```

**Solution**:
```bash
# Check if ifconfig is available
which ifconfig

# Install net-tools if missing
sudo apt-get install net-tools  # Ubuntu/Debian
sudo yum install net-tools      # CentOS/RHEL

# Run with appropriate permissions
sudo python scripts/backup_restore.py backup
```

#### Restore Fails

**Problem**: Restore operation fails
```bash
Error: Failed to restore eth0
```

**Solution**:
```bash
# Check if interface exists
ip link show eth0

# Verify backup integrity
python scripts/backup_restore.py verify --name <backup_name>

# Try restoring individual interface
sudo python scripts/backup_restore.py restore --name <backup_name> --interface eth0

# Check for permission issues
sudo python mac_changer.py -i eth0 -c
```

#### Network Connectivity Lost

**Problem**: Lost network after MAC change

**Solution**:
```bash
# 1. Use console access
# 2. Restore from backup
sudo python scripts/backup_restore.py restore --name <backup_name>

# 3. If backup restore fails, manual restore
sudo ifconfig eth0 down
sudo ifconfig eth0 hw ether <original_mac>
sudo ifconfig eth0 up

# 4. Restart networking
sudo systemctl restart networking
```

#### Backup Corruption

**Problem**: Backup integrity check fails
```bash
❌ Checksum mismatch for eth0
```

**Solution**:
```bash
# 1. Try using different backup
python scripts/backup_restore.py list

# 2. Import backup from external source
python scripts/backup_restore.py import --file /path/to/backup.json

# 3. Manual MAC address lookup
# Check system logs for original MAC
journalctl -u networking | grep -i "mac\|ether"

# 4. Check hardware for printed MAC
# Look for MAC address on network card
```

### Recovery Scenarios

#### Scenario 1: Single Interface Issues

```bash
# Problem: eth0 MAC change caused connectivity issues
# Solution: Restore only eth0

# 1. Identify the issue
python mac_changer.py -i eth0 -c

# 2. Restore eth0 from backup
sudo python scripts/backup_restore.py restore --name <backup_name> --interface eth0

# 3. Verify connectivity
ping -c 4 8.8.8.8
```

#### Scenario 2: Multiple Interface Issues

```bash
# Problem: Multiple interfaces changed, system unstable
# Solution: Full system restore

# 1. Access via console
# 2. Restore all interfaces
sudo python scripts/backup_restore.py restore --name <backup_name>

# 3. Restart network services
sudo systemctl restart networking
```

#### Scenario 3: No Backup Available

```bash
# Problem: No backup exists, need original MAC
# Solution: Hardware/system recovery

# 1. Check system logs
journalctl -u networking | grep -i "mac\|ether"
dmesg | grep -i "mac\|ether"

# 2. Check hardware labels
# Look for printed MAC on network card

# 3. Use DHCP logs (if available)
# Check router/DHCP server logs for MAC history

# 4. Network equipment logs
# Check switch/router logs for MAC learning
```

## Advanced Usage

### Scripted Backups

Create automated backup scripts:

```bash
#!/bin/bash
# backup_script.sh

# Configuration
BACKUP_NAME="scheduled_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/var/log/mac_backup.log"

# Create backup
echo "$(date): Starting backup..." >> $LOG_FILE
python scripts/backup_restore.py backup --name $BACKUP_NAME >> $LOG_FILE 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): Backup $BACKUP_NAME created successfully" >> $LOG_FILE
    
    # Verify backup
    python scripts/backup_restore.py verify --name $BACKUP_NAME >> $LOG_FILE 2>&1
    
    if [ $? -eq 0 ]; then
        echo "$(date): Backup $BACKUP_NAME verified successfully" >> $LOG_FILE
    else
        echo "$(date): Backup $BACKUP_NAME verification failed" >> $LOG_FILE
    fi
else
    echo "$(date): Backup creation failed" >> $LOG_FILE
fi

# Cleanup old backups
python scripts/backup_restore.py cleanup >> $LOG_FILE 2>&1
```

### Cron Job Setup

Set up automated backups:

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /path/to/backup_script.sh
```

### Integration with Configuration Management

#### Ansible Integration

```yaml
---
- name: Backup MAC addresses
  shell: python scripts/backup_restore.py backup --name ansible_backup
  args:
    chdir: /path/to/mac_changer
  register: backup_result

- name: Verify backup
  shell: python scripts/backup_restore.py verify --name ansible_backup
  args:
    chdir: /path/to/mac_changer
  when: backup_result.rc == 0

- name: Change MAC address
  shell: python mac_changer.py -i {{ interface }} -m {{ new_mac }}
  args:
    chdir: /path/to/mac_changer
  become: yes
  register: mac_change_result

- name: Restore on failure
  shell: python scripts/backup_restore.py restore --name ansible_backup
  args:
    chdir: /path/to/mac_changer
  become: yes
  when: mac_change_result.rc != 0
```

### Monitoring and Alerting

Monitor backup and restore operations:

```bash
#!/bin/bash
# monitoring_script.sh

# Check backup age
LATEST_BACKUP=$(python scripts/backup_restore.py list | head -2 | tail -1 | awk '{print $2}')
BACKUP_AGE=$(python -c "
import json
with open('backups/mac_addresses/${LATEST_BACKUP}.json', 'r') as f:
    data = json.load(f)
    import datetime
    backup_time = datetime.datetime.fromisoformat(data['timestamp'])
    age = (datetime.datetime.now() - backup_time).days
    print(age)
")

# Alert if backup is too old
if [ $BACKUP_AGE -gt 7 ]; then
    echo "WARNING: Latest backup is $BACKUP_AGE days old" | mail -s "MAC Backup Alert" admin@example.com
fi

# Check backup integrity
python scripts/backup_restore.py verify --name $LATEST_BACKUP
if [ $? -ne 0 ]; then
    echo "ERROR: Backup integrity check failed for $LATEST_BACKUP" | mail -s "MAC Backup Error" admin@example.com
fi
```

## Security Considerations

### Backup Security

1. **Protect backup files**:
   ```bash
   # Set restrictive permissions
   chmod 600 backups/mac_addresses/*.json
   chown root:root backups/mac_addresses/*.json
   ```

2. **Encrypt sensitive backups**:
   ```bash
   # Encrypt backup
   gpg --symmetric --cipher-algo AES256 backup.json

   # Decrypt when needed
   gpg --decrypt backup.json.gpg > backup.json
   ```

3. **Secure backup storage**:
   - Store backups on encrypted filesystems
   - Use separate storage for critical backups
   - Implement backup rotation policies

### Access Control

1. **Restrict script access**:
   ```bash
   # Only root can execute
   chmod 750 scripts/backup_restore.py
   chown root:root scripts/backup_restore.py
   ```

2. **Audit backup operations**:
   ```bash
   # Log all backup operations
   echo "$(date): $(whoami) created backup $BACKUP_NAME" >> /var/log/audit.log
   ```

## Compliance and Documentation

### Change Documentation

Document all MAC address changes:

```bash
# Create change log
echo "$(date): Changed $INTERFACE from $OLD_MAC to $NEW_MAC by $(whoami)" >> /var/log/mac_changes.log

# Include backup information
echo "$(date): Backup $BACKUP_NAME created before change" >> /var/log/mac_changes.log
```

### Compliance Requirements

For regulated environments:
- Maintain backup retention per compliance requirements
- Document all changes with business justification
- Implement approval workflows for changes
- Regular audit of backup procedures

---

## Support and Contact

For backup and restore issues:
- **Documentation**: This file and README.md
- **Issues**: GitHub Issues page
- **Email**: thomas@dyhr.com for critical issues

**Remember**: Always test backup and restore procedures in a non-production environment first!

**Last Updated**: December 2024
**Version**: 1.0.0