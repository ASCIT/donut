DROP TABLE IF EXISTS calendar_logs;
DROP TABLE IF EXISTS calendar_events;
CREATE TABLE calendar_logs(
    log_id                 INT          NOT NULL AUTO_INCREMENT,
    uid                    CHAR(7)  NOT NULL, 
    calendar_id            VARCHAR(25)  NOT NULL, 
    calendar_gmail         VARCHAR(50)  NOT NULL,
    user_gmail         VARCHAR(50)  NOT NULL,
    acl_id                 VARCHAR(50)  NOT NULL,
    request_time           DATETIME     NOT NULL, 
    request_permission     CHAR(4)     NOT NULL, 
    PRIMARY KEY (log_id)
);

CREATE TABLE calendar_events(
    event_id            INT          NOT NULL AUTO_INCREMENT,
    uid                 CHAR(7) , -- Who created this even
    calendar_tag        VARCHAR(15)  NOT NULL,
    google_event_id     VARCHAR(80)  NOT NULL, 
    summary             TEXT, 
    description         TEXT, 
    location            TEXT,  
    begin_time	        DATETIME, 
    end_time	        DATETIME, 
    UNIQUE(google_event_id), 
    PRIMARY KEY (event_id));
