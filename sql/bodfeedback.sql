DROP TABLE IF EXISTS `bod_complaint_info`;

CREATE TABLE `bod_complaint_info` (
  `complaint_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(50) DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `uuid` varchar(36) NOT NULL,
  PRIMARY KEY (`complaint_id`),
  UNIQUE KEY (`uuid`)
);

DROP TABLE IF EXISTS `bod_complaint_messages`;

CREATE TABLE `bod_complaint_messages` (
  `complaint_id` int(11) DEFAULT NULL,
  `time` timestamp,
  `message` text,
  `poster` varchar(50) DEFAULT NULL,
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`message_id`),
  FOREIGN KEY (`complaint_id`) REFERENCES `bod_complaint_info` (`complaint_id`) ON DELETE CASCADE
);

DROP TABLE IF EXISTS `bod_complaint_emails`;

CREATE TABLE `bod_complaint_emails` (
  `complaint_id` int(11) NOT NULL,
  `email` varchar(50) DEFAULT NULL,
  `email_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`email_id`),
  FOREIGN KEY (`complaint_id`) REFERENCES `bod_complaint_info` (`complaint_id`) ON DELETE CASCADE
); 

