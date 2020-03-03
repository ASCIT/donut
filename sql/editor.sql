
DROP TABLE IF EXISTS webpage_files;

CREATE TABLE webpage_files
(
	webpage_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL UNIQUE, 
	last_edit_uid INTEGER, 
	locked BOOL DEFAULT FALSE, 
	last_edit_time DATETIME DEFAULT NOW(),       
	content  TEXT DEFAULT "", 
    primary key(webpage_id)
);
