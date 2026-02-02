#!/bin/bash

set -e

docker compose exec mariadb mysql -u root -ppassword donut
