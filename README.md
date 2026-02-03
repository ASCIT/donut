# donut

The repository for Donut. Written using Python/Flask and powered by MariaDB.

## Local setup

First, on the donut server, create a backup:
```bash
/home/ascit/donut/server_scripts/backup_db.sh
```

In your local repo:
```bash
cd `local_db/`
# copy backup file to local machine (change filename to backup created above)
rsync -P donut:/backups/donut_backup_2026XXXX_XXXXXX.sql .
# start local database
docker compose up -d
# load the backup
./import_backup.sh donut_backup_2026XXXX_XXXXXX.sql
# keep the backup sql file in case the server does down, it is good to have copies of the backups
```

To setup the backend:
```bash
micromamba create -n donut2 -y conda-forge::python=3.8 conda-forge::nodejs=24
mamba activate donut2
pip install -r requirements.txt
# separate vite build for gpt_sam
cd donut/modules/gpt_sam/frontend
npm install
npm run build
```

To run the server, activate the environment and run:
```bash
python run_server.py
```
