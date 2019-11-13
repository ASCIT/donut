DROP TABLE IF EXISTS arc_complaint_emails;
DROP TABLE IF EXISTS arc_complaint_messages;
DROP TABLE IF EXISTS arc_complaint_info;

CREATE TABLE arc_complaint_info (
  complaint_id INT(11) NOT NULL AUTO_INCREMENT,
  subject VARCHAR(50) DEFAULT NULL,
  status VARCHAR(36) DEFAULT NULL,
  uuid BINARY(16) NOT NULL,
  PRIMARY KEY (complaint_id),
  UNIQUE KEY (uuid)
);

CREATE TABLE arc_complaint_messages (
  complaint_id INT(11) DEFAULT NULL,
  time TIMESTAMP,
  message TEXT,
  poster VARCHAR(50) DEFAULT NULL,
  message_id INT(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (message_id),
  FOREIGN KEY (complaint_id) REFERENCES arc_complaint_info (complaint_id) ON DELETE CASCADE
);

CREATE TABLE arc_complaint_emails (
  complaint_id INT(11) NOT NULL,
  email VARCHAR(50) DEFAULT NULL,
  email_id INT(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (email_id),
  FOREIGN KEY (complaint_id) REFERENCES arc_complaint_info (complaint_id) ON DELETE CASCADE,
  CONSTRAINT complaint_email UNIQUE (complaint_id, email)
); 

