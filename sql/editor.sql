
DROP TABLE IF EXISTS webpage_files_locks;

CREATE TABLE webpage_files_locks
(
	webpage_id INT NOT NULL AUTO_INCREMENT,
	title VARCHAR(35) NOT NULL UNIQUE, 
	last_edit_uid INTEGER, 
	locked BOOL DEFAULT FALSE, 
	last_edit_time TIMESTAMP DEFAULT NOW(),       
	primary key(webpage_id)
);
