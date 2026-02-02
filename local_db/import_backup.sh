#!/bin/bash

set -e
set -o pipefail
set -x

# Import a database backup into a fresh MariaDB Docker container
# Usage: ./import_backup.sh <backup_file.sql>

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File '$BACKUP_FILE' not found"
    exit 1
fi

# Wait for MariaDB to be ready
echo "Waiting for MariaDB to be ready..."
until docker compose exec -T mariadb mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; do
    sleep 1
done

# Create the donut database and import the backup
docker compose exec -T mariadb mysql -u root -ppassword -e "CREATE DATABASE IF NOT EXISTS donut;"
docker compose exec -T mariadb mysql -u root -ppassword donut < "$BACKUP_FILE"

echo "Import complete"
