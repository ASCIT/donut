-- TODO: Add CASCADEs
-- TODO: Better comments

DROP TABLE IF EXISTS news;
DROP VIEW IF EXISTS current_position_holders;
DROP VIEW IF EXISTS current_direct_position_holders;
DROP TABLE IF EXISTS position_relations;
DROP VIEW IF EXISTS house_positions;
DROP VIEW IF EXISTS house_groups;
DROP TABLE IF EXISTS position_holders;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS member_options;
DROP TABLE IF EXISTS options;
DROP VIEW IF EXISTS members_full_name;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS buildings;
DROP TABLE IF EXISTS newsgroup_posts;
DROP TABLE IF EXISTS group_applications;

-- Residential Buildings
CREATE TABLE buildings (
    building_id     INT             NOT NULL AUTO_INCREMENT,
    building_name   VARCHAR(100)    NOT NULL,
    PRIMARY KEY (building_id),
    UNIQUE (building_name)
);

-- Members Table
CREATE TABLE members (
    user_id            INT          NOT NULL AUTO_INCREMENT,
    uid                CHAR(7)      NOT NULL,
    last_name          VARCHAR(255) NOT NULL,
    first_name         VARCHAR(255) NOT NULL,
    preferred_name     VARCHAR(255) DEFAULT NULL,
    middle_name        VARCHAR(255) DEFAULT NULL,
    email              VARCHAR(255) NOT NULL,
    phone              VARCHAR(64)  DEFAULT NULL,
    gender             TINYINT      DEFAULT NULL, -- Numerical code that will be
                                                  -- stored in code
    gender_custom      VARCHAR(32)  DEFAULT NULL,
    birthday           DATE         DEFAULT NULL,
    entry_year         YEAR(4)      DEFAULT NULL,
    graduation_year    YEAR(4)      DEFAULT NULL,
    msc                SMALLINT     DEFAULT NULL,
    building_id        INT          DEFAULT NULL,
    room               VARCHAR(5)   DEFAULT NULL,
    address            VARCHAR(255) DEFAULT NULL,
    city               VARCHAR(64)  DEFAULT NULL,
    state              VARCHAR(64)  DEFAULT NULL,
    zip                VARCHAR(10)  DEFAULT NULL,
    country            VARCHAR(64)  DEFAULT NULL,
    timezone           INT          DEFAULT NULL, -- Offset from GMT in minutes
                                                  -- TODO: remove after COVID
    create_account_key CHAR(32)     DEFAULT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (building_id) REFERENCES buildings(building_id),
    UNIQUE (uid)
);

-- Member Full Name View
CREATE VIEW members_full_name AS (
    SELECT user_id,
        CONCAT(IFNULL(preferred_name, first_name), ' ', last_name) AS full_name
    FROM members
);

-- Major Option Table
CREATE TABLE options (
    option_id     INT         NOT NULL AUTO_INCREMENT,
    option_name   VARCHAR(50) NOT NULL,
    PRIMARY KEY (option_id),
    UNIQUE (option_name)
);

-- Option to Member Table
-- Many to many relationship between members and options
CREATE TABLE member_options (
    user_id     INT,
    option_id   INT,
    option_type   VARCHAR(8)  NOT NULL,
    PRIMARY KEY (user_id, option_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    FOREIGN KEY (option_id) REFERENCES options(option_id)
);

-- Users Table
CREATE TABLE users (
    user_id                   INT,
    username                  VARCHAR(32)  NOT NULL,
    last_login                DATETIME     DEFAULT NULL,
    password_hash             VARCHAR(255) NOT NULL,
    password_reset_key        CHAR(32)     DEFAULT NULL,
    password_reset_expiration DATETIME     DEFAULT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    UNIQUE (username)
);

-- Groups Table
-- Groups of members. Used for mailing lists, etc.
-- Groups are used for any internal/external groupings of users.
-- Used for groups on campus
-- Examples: Blacker Hovse, IHC, CRC, ug-list, ug-2020
CREATE TABLE groups (
    group_id                INT          NOT NULL AUTO_INCREMENT,
    group_name              VARCHAR(64)  NOT NULL,
    group_desc              VARCHAR(255) DEFAULT NULL,
    type                    VARCHAR(255) NOT NULL,
    newsgroups              BOOLEAN      DEFAULT FALSE, -- Controls if this is
                                                        -- an email group
    anyone_can_send         BOOLEAN      DEFAULT FALSE, -- This flag controls
                                                        -- whether or not
                                                        -- anyone can send
                                                        -- emails to the group
    visible                 BOOLEAN      DEFAULT FALSE, -- Controls if anyone
                                                        -- anyone can see this
                                                        -- group
    PRIMARY KEY (group_id),
    UNIQUE (group_name)
);

CREATE TABLE newsgroup_posts (
    newsgroup_post_id       INT          NOT NULL AUTO_INCREMENT,
    group_id                INT          NOT NULL, -- Which group was it to
    subject                 TEXT         NOT NULL,
    message                 TEXT         NOT NULL,
    post_as		    VARCHAR(32)  DEFAULT NULL,
    user_id                 INT          NOT NULL, -- Who sent this message
    time_sent               TIMESTAMP    DEFAULT CURRENT_TIMESTAMP, -- When were messages sent
    PRIMARY KEY (newsgroup_post_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id)
);

-- Positions Table
CREATE TABLE positions (
    group_id INT         NOT NULL,
    pos_id   INT         NOT NULL AUTO_INCREMENT,
    pos_name VARCHAR(64) NOT NULL,
    send        BOOLEAN DEFAULT FALSE, -- Toggles whether or not this position
                                       -- can send emails to group
    control     BOOLEAN DEFAULT FALSE, -- Toggles whether or not this position
                                       -- has admin control over group
    receive     BOOLEAN DEFAULT TRUE,  -- Toggles if this position receives
                                       -- emails from this group

    PRIMARY KEY (pos_id),
    FOREIGN KEY (group_id)
        REFERENCES groups(group_id)
        ON DELETE CASCADE,
    UNIQUE (group_id, pos_name)
);

-- Position to Member Table
CREATE TABLE position_holders (
    hold_id    INT  NOT NULL AUTO_INCREMENT,
    pos_id     INT  NOT NULL,
    user_id    INT  NOT NULL,
    start_date DATE DEFAULT NULL,
    end_date   DATE DEFAULT NULL,
    subscribed BOOLEAN DEFAULT TRUE, -- Toggles whether user is subscribed to newsgroup
    PRIMARY KEY (hold_id),
    FOREIGN KEY (pos_id)
        REFERENCES positions(pos_id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES members(user_id)
);

-- Houses View
-- Because houses are used so much, make a view separate from the groups
-- table.
CREATE VIEW house_groups AS (
    SELECT group_id, group_name FROM groups WHERE type = 'house'
);
-- House Positions View
-- House membership positions are special,
-- so make a view separate from the positions table.
CREATE VIEW house_positions AS (
    SELECT group_id, group_name, pos_id, pos_name
    FROM house_groups NATURAL JOIN positions
    WHERE pos_name IN ('Full Member', 'Social Member')
);

-- Position to position table
CREATE TABLE position_relations (
    pos_id_from   INT  NOT NULL,
    pos_id_to     INT  NOT NULL,
    PRIMARY KEY (pos_id_from, pos_id_to),
    FOREIGN KEY (pos_id_from) REFERENCES positions(pos_id) ON DELETE CASCADE,
    FOREIGN KEY (pos_id_to) REFERENCES positions(pos_id) ON DELETE CASCADE
);

-- Filters the position_holders table to only list holds that are active
CREATE VIEW current_direct_position_holders AS (
    SELECT * FROM position_holders
    WHERE (start_date IS NULL OR start_date <= CURRENT_DATE)
        AND (end_date IS NULL OR CURRENT_DATE <= end_date)
);
-- All direct and indirect position holds that are currently active.
-- This should be used in general for querying held positions.
CREATE VIEW current_position_holders AS (
    SELECT * FROM current_direct_position_holders
    UNION ALL
    SELECT
        current_direct_position_holders.hold_id,
        position_relations.pos_id_to AS pos_id,
        current_direct_position_holders.user_id,
        current_direct_position_holders.start_date,
        current_direct_position_holders.end_date,
        current_direct_position_holders.subscribed
    FROM current_direct_position_holders
        JOIN position_relations ON pos_id = pos_id_from
);

-- News items to show on the homepage
CREATE TABLE news (
    news_id     INT  NOT NULL AUTO_INCREMENT,
    news_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    news_text   TEXT NOT NULL,
    PRIMARY KEY (news_id)
);
CREATE TABLE group_applications (
    user_id         INT NOT NULL,
    group_id        INT NOT NULL,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);
