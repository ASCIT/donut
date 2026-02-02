#!/bin/bash

set -e
set -o pipefail
set -x

# Backup the donut database
# Creates a timestamped backup file in the current directory

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/donut_backup_${TIMESTAMP}.sql"

mysqldump -u root --password='1<3d0nut5' --single-transaction --routines --triggers donut > "${BACKUP_FILE}"

echo "Backup created: ${BACKUP_FILE}"
