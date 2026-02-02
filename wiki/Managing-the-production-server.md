# Where is the production code?

It's in `/home/ascit/donut`, which is cloned from this repository.
There are some secret configuration files that must also be present for the app to run; they should be the same as in the development clones of the repository:
- `donut/config.py`: has configuration information for the `dev` and `prod` environments, e.g. database logins
- `calendar.json`: has authorization information for the Google Calendar API

# Apache

The production server (at http://35.162.204.135) uses Apache and [mod_wsgi](https://modwsgi.readthedocs.io/en/develop) to run the Flask app.
The Apache configuration is in `/etc/apache2/sites-available/000-default.conf` and the mod_wsgi configuration is `/home/ascit/donut/donut.wsgi`.
To reload these configurations, run `sudo service apache2 restart`.

# Logs

The Flask (Apache) logs are written to `/var/log/apache2/access.log`.
Apache and mod_wsgi error logs are written to `/var/log/apache2/error.log`.

# Database

The production MariaDB database is `donut`.
See `donut/config.py` for the username and password.

# `virtualenv`

The production server uses the virtualenv in `/home/ascit/virtualenvs/donut-py3`.
To update the `pip` modules, activate the virtualenv by running `. /home/ascit/virtualenvs/donut-py3/bin/activate` in a shell and then run `make update-packages` in the production code directory.

# HTTPS

After years of sending plaintext passwords on legacy Donut, we finally have encryption!
We are using [Let's Encrypt](https://letsencrypt.org) to get those sweet sweet HTTPS certificates for free.
HTTPS was set up initially with this command, which obtained a cert and reconfigured Apache automatically:
```
sudo certbot --apache -d donut.caltech.edu,beta.donut.caltech.edu -m csander@caltech.edu --agree-tos
```
The certificates are installed in `/etc/letsencrypt` and the Apache HTTPS config is at `/etc/apache2/sites-available/000-default-le-ssl.conf`.
The certificate expires every 3 months, and the following command is set up as a `cron` job to renew it:
```
sudo certbot renew --post-hook 'service apache2 restart'
```
We should probably register it with a different email address when I'm no longer on devteam just in case the renewal script fails.

# Initial configuration

Hopefully, this should never have to be done a second time, but just in case...

1. Set up the tables in the prod DB. This requires removing the `donut_test` lines and the `SOURCE sql/test_data.sql` line in `sql/reset.sql` and running `mysql --password=PASSWORD -u ascit donut < sql/reset.sql`.

2. Export and import legacy directory tables (Run `donut/modules/directory_search/utils/export_legacy.py` on legacy server and `donut/modules/directory_search/utils/import_legacy.py` on new server.)

3. Run this SQL on the prod DB:
```sql
INSERT INTO marketplace_categories (cat_title) 
VALUES ('Textbooks'), ('Furniture'), ('Appliances'), ('Transportation'), ('Electronics'), ('Games'), ('Miscellaneous');

INSERT INTO rooms (location, title, description) VALUES 
	('SAC 23', 'ASCIT Screening Room', 'A room for watching DVDs and videos'), 
	('SAC 13', 'Group Study Room', 'Group study room in the SAC'), 
	('SAC 14', 'Group Study Room', 'Group study room in the SAC'), 
	('SAC 4', 'Music Room', 'Music room in the SAC'), 
	('SAC 5', 'Music Room', 'Music room in the SAC'), 
	('SAC 5a', 'Music Room', 'Music room in the SAC'), 
	('SAC 7', 'Music Room', 'Music room in the SAC');

INSERT INTO permissions (permission_id, permission_type, resource_name, description) VALUES
	(1, 'Admin', 'ALL', 'Grants all other permissions -- FOR DEV ONLY'),
	(3, 'View', 'Directory search hidden fields', 'Can view UID, birthday, phone number, and hometown'),
	(4, 'Edit', 'Edit pages', 'Able to edit pages'),
	(5, 'Edit', 'Upload documents', 'Able to upload documents'),
	(8, 'View', 'BOD feedback summary', 'View a summary page of all feedback'),
	(9, 'Edit', 'BOD feedback resolved', 'Mark a complaint resolved or unresolved'),
	(10, 'Edit', 'BOD feedback emails', 'Add or remove subscribed emails from feedback'),
	(11, 'View', 'BOD feedback emails', 'View the list of subscribed emails on feedback'),
	(12, 'Masquerade', 'Masquerade', 'Log in as other users with their permissions'),
	(13, 'View', 'ARC feedback summary', 'View a summary page of all feedback'),
	(14, 'Edit', 'ARC feedback resolved', 'Mark a complaint resolved or unresolved'),
	(15, 'Edit', 'ARC feedback emails', 'Add or remove subscribed emails from feedback'),
	(16, 'View', 'ARC feedback emails', 'View the list of subscribed emails on feedback'),
	(17, 'View', 'Donut feedback summary', 'View a summary page of all feedback'),
	(18, 'Edit', 'Donut feedback resolved', 'Mark a complaint resolved or unresolved'),
	(19, 'Edit', 'Donut feedback emails', 'Add or remove subscribed emails from feedback'),
	(20, 'View', 'Donut feedback emails', 'View the list of subscribed emails on feedback'),
	(21, 'Calendar', 'Avery', 'Edit Avery calendar'),
	(22, 'Calendar', 'ASCIT', 'Edit ASCIT calendar'),
	(23, 'Calendar', 'Bechtel', 'Edit Bechtel calendar'),
	(24, 'Calendar', 'Blacker', 'Edit Blacker calendar'),
	(25, 'Calendar', 'Dabney', 'Edit Dabney calendar'),
	(26, 'Calendar', 'Fleming', 'Edit Fleming calendar'),
	(27, 'Calendar', 'Lloyd', 'Edit Lloyd calendar'),
	(28, 'Calendar', 'Page', 'Edit Page calendar'),
	(29, 'Calendar', 'Ricketts', 'Edit Ricketts calendar'),
	(30, 'Calendar', 'Ruddock', 'Edit Ruddock calendar'),
	(31, 'Calendar', 'Other', 'Edit Other calendar'),
	(32, 'Calendar', 'Athletics', 'Edit Athletics calendar'),
	(33, 'Edit', 'Surveys', 'Create and manage surveys'),
	(34, 'Memberships', 'Avery', 'Manage Avery memberships'),
	(35, 'Memberships', 'Blacker', 'Manage Blacker memberships'),
	(36, 'Memberships', 'Dabney', 'Manage Dabney memberships'),
	(37, 'Memberships', 'Fleming', 'Manage Fleming memberships'),
	(38, 'Memberships', 'Lloyd', 'Manage Lloyd memberships'),
	(39, 'Memberships', 'Page', 'Manage Page memberships'),
	(40, 'Memberships', 'Ricketts', 'Manage Ricketts memberships'),
	(41, 'Memberships', 'Ruddock', 'Manage Ruddock memberships');
```

4. On the legacy server, log onto the database, and do
```
\copy (SELECT start_date, end_date, pos_name, org_name, uid, control FROM position_holders NATURAL JOIN position_titles NATURAL JOIN position_organizations NATURAL JOIN inums NATURAL JOIN undergrads) TO group_info.csv WITH CSV HEADER
```
Then take that output and run `donut/modules/groups/utils/position_importer.py` 

5. Run `python donut/modules/groups/utils/insert_permissions.py` to insert the permissions for each group. 

6. On the legacy server, `sudo -i`
```
cd /var/lib/mediawiki 

php maintenance/dumpBackup.php --full > full.xml
```
to get the mediawiki dump (aka all the ascit pages).

Take that output, and run
`donut/modules/editor/utils/media_wiki_import.py`

7. Define the `ug` group by running the following SQL on the prod DB:
```sql
INSERT INTO groups(group_name, group_desc, type, newsgroups) VALUES
('ug', 'All undergrads', 'ug-auto', 1);
SET @ug_group = (SELECT group_id FROM groups WHERE group_name = 'ug');
INSERT INTO positions(group_id, pos_name, send, control, receive) VALUES
	(@ug_group, 'Member', 0, 0, 1),
	(@ug_group, 'Admin', 1, 1, 0);
INSERT INTO position_relations(pos_id_from, pos_id_to)
SELECT
	pos_id AS pos_id_from,
	(SELECT pos_id FROM positions WHERE group_id = @ug_group AND pos_name = 'Admin') AS pos_id_to
FROM positions NATURAL JOIN groups
WHERE group_name IN ('ASCIT', 'Interhouse Committee (IHC)', 'Devteam', 'Review Committee', 'The Tech');
```

8. Run `donut/modules/directory_search/utils/update_ug_groups.py`
9. `chown -Rf www-data.www-data /home/ascit/donut/donut/modules/uploads/uploaded_files/`, since all uploads go there and the server needs to be able to insert and delete from the folder.

# Backups

You can use `mysqldump` to generate a backup of the database:
```
sudo mysqldump -u root --password=ROOT_PASSWORD donut --single-transaction --add-drop-table --result-file=donut_backup.sql
```
(This generates a ~600 MB SQL file containing all the `CREATE TABLE` and `INSERT` statements necessary to rebuild the database.)
You can load this backup by piping the file into `mysql` (it may be necessary to temporarily disable foreign key constraints):
```
(echo "SET FOREIGN_KEY_CHECKS = 0;"; cat donut_backup.sql; echo "SET FOREIGN_KEY_CHECKS = 1;") | mysql -u root --password=ROOT_PASSWORD donut
```
I've also found this procedure useful for copying the contents of the prod DB to the dev DB (just import to `donut_dev` instead).
I haven't experimented with automating this procedure.