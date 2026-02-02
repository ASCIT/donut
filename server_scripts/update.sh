#!/bin/bash

set -e
set -o pipefail
set -x

cd /home/ascit/donut
git pull
# rebuild gpt_sam module, which has separate vite build process
cd donut/modules/gpt_sam/frontend
npm run build
# restart the server
sudo apachectl restart

