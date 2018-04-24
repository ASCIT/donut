-- TODO: Add CASCADEs
-- TODO: Better comments

DROP TABLE IF EXISTS position_relations;
DROP VIEW IF EXISTS group_house_membership;
DROP VIEW IF EXISTS group_houses;
DROP TABLE IF EXISTS position_holders;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS privacies;
DROP TABLE IF EXISTS member_options;
DROP TABLE IF EXISTS options;
DROP VIEW IF EXISTS members_full_name;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS buildings;

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
    gender_custom      VARCHAR(32)  DEFAULT NULL, -- TODO: Implement showing
                                                  -- custom gender options
    birthday           DATE         DEFAULT NULL,
    entry_year         YEAR(4)      DEFAULT NULL,
    graduation_year    YEAR(4)      DEFAULT NULL,
    msc                SMALLINT     DEFAULT NULL,
    building_id        INT          DEFAULT NULL,
    room               VARCHAR(5)   DEFAULT NULL,
    address            VARCHAR(255) DEFAULT NULL,
    city               VARCHAR(64)  DEFAULT NULL,
    state              VARCHAR(64)  DEFAULT NULL,
    zip                VARCHAR(9)   DEFAULT NULL,
    country            VARCHAR(64)  DEFAULT NULL,
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

-- Privacy Level of Member Info Table
-- Directory privacies for who can see data.
-- Default is Caltech?
CREATE TABLE privacies (
    priv_id     INT         NOT NULL AUTO_INCREMENT,
    priv_name   VARCHAR(8)  NOT NULL,
    priv_desc   VARCHAR(64) NOT NULL,
    PRIMARY KEY (priv_id),
    UNIQUE (priv_name)
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
    group_name              VARCHAR(32)  NOT NULL,
    group_desc              VARCHAR(255) DEFAULT NULL,
    type                    VARCHAR(255) NOT NULL,
    newsgroups              BOOLEAN      DEFAULT FALSE, -- Controls if this is
                                                        -- an email group
    anyone_can_send         BOOLEAN      DEFAULT FALSE, -- This flag controls
                                                        -- whether or not
                                                        -- anyone can send
                                                        -- emails to the group
    members_can_send        BOOLEAN      DEFAULT FALSE, -- Controls if any
                                                        -- member can send to
                                                        -- the group
    visible                 BOOLEAN      DEFAULT FALSE, -- Controls if anyone
                                                        -- anyone can see this
                                                        -- group
    admin_control_members   BOOLEAN      DEFAULT TRUE,  -- Toggles whether or
                                                        -- not admins control
                                                        -- Group membership
    PRIMARY KEY (group_id),
    UNIQUE (group_name)
);

-- Positions Table
CREATE TABLE positions (
    group_id INT         NOT NULL,
    pos_id   INT         NOT NULL AUTO_INCREMENT,
    pos_name VARCHAR(32) NOT NULL,
    send        BOOLEAN DEFAULT FALSE, -- Toggles whether or not this position
                                       -- can send emails to group
    control     BOOLEAN DEFAULT FALSE, -- Toggles whether or not this position
                                       -- has admin control over group
    receive     BOOLEAN DEFAULT TRUE,  -- Toggles if this position receives
                                       -- emails from this group

    PRIMARY KEY (pos_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

-- Position to Member Table
CREATE TABLE position_holders (
    hold_id    INT  NOT NULL AUTO_INCREMENT,
    group_id   INT  NOT NULL,
    pos_id     INT  NOT NULL,
    user_id    INT  NOT NULL,
    start_date DATE DEFAULT NULL,
    end_date   DATE DEFAULT NULL,
    PRIMARY KEY (hold_id),
    FOREIGN KEY (group_id, pos_id) REFERENCES positions(group_id, pos_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id)
);

-- House View
-- Because houses are used so much, make a view separate from the groups
-- table.
CREATE VIEW group_houses AS (
    SELECT group_id, group_name FROM groups WHERE type = 'house'
);

-- House Members View
-- Because house membership is used so much, make a view separate from the
-- positions table.
CREATE VIEW group_house_membership AS (
    SELECT user_id, group_id, pos_id
    FROM group_houses NATURAL JOIN positions NATURAL JOIN position_holders
    WHERE UPPER(pos_name) = UPPER('Full Member')
        OR UPPER(pos_name) = UPPER('Social Member')
);

CREATE TABLE position_relations (
    relation_id   INT  NOT NULL AUTO_INCREMENT,
    pos_id_from   INT  NOT NULL,
    pos_id_to     INT  NOT NULL,
    PRIMARY KEY (relation_id),
    FOREIGN KEY (pos_id_from) REFERENCES positions(pos_id),
    FOREIGN KEY (pos_id_to) REFERENCES positions(pos_id)
)
