-- TODO: Add CASCADEs
-- TODO: Better comments

DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS groups;
DROP VIEW IF EXISTS org_house_membership;
DROP VIEW IF EXISTS org_houses;
DROP TABLE IF EXISTS position_holders;
DROP TABLE IF EXISTS position_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS organizations;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS privacies;
DROP TABLE IF EXISTS member_options; DROP TABLE IF EXISTS options; DROP VIEW IF EXISTS members_full_name; DROP TABLE IF EXISTS members; 
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
    building           VARCHAR(32)  DEFAULT NULL,
    room_num           SMALLINT     DEFAULT NULL,
    address            VARCHAR(255) DEFAULT NULL,
    city               VARCHAR(64)  DEFAULT NULL,
    state              VARCHAR(64)  DEFAULT NULL,
    zip                VARCHAR(9)   DEFAULT NULL,
    country            VARCHAR(64)  DEFAULT NULL,
    create_account_key CHAR(32)     DEFAULT NULL,
    PRIMARY KEY (user_id),
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
    option_name   VARCHAR(16) NOT NULL,
    PRIMARY KEY (option_id)
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

-- Organizations Table
-- Organizations on campus. Used for positions, etc.
-- Examples: Blacker Hovse, IHC, CRC
CREATE TABLE organizations (
    org_id   INT         NOT NULL AUTO_INCREMENT,
    org_name VARCHAR(32) NOT NULL,
    type     VARCHAR(32) DEFAULT NULL,
    PRIMARY KEY (org_id),
    UNIQUE (org_name)
);

-- Organization Positions Table
CREATE TABLE positions (
    org_id   INT         NOT NULL,
    pos_id   INT         NOT NULL AUTO_INCREMENT,
    pos_name VARCHAR(32) NOT NULL,
    PRIMARY KEY (pos_id),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

-- Permissions Table
-- Table of types of permissions a position holder could have
CREATE TABLE permissions (
    perm_id   INT          NOT NULL AUTO_INCREMENT,
    perm_name VARCHAR(32)  NOT NULL,
    perm_desc VARCHAR(255),
    PRIMARY KEY (perm_id),
    UNIQUE (perm_name)
);

-- Permission to Position Table
CREATE TABLE position_permissions (
    org_id  INT NOT NULL,
    pos_id  INT NOT NULL,
    perm_id INT NOT NULL,
    PRIMARY KEY (org_id, pos_id, perm_id),
    FOREIGN KEY (org_id, pos_id) REFERENCES positions(org_id, pos_id)
);

-- Position to Member Table
CREATE TABLE position_holders (
    hold_id    INT  NOT NULL AUTO_INCREMENT,
    org_id     INT  NOT NULL,
    pos_id     INT  NOT NULL,
    user_id    INT  NOT NULL,
    start_date DATE DEFAULT NULL,
    end_date   DATE DEFAULT NULL,
    PRIMARY KEY (hold_id),
    FOREIGN KEY (org_id, pos_id) REFERENCES positions(org_id, pos_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id)
);

-- House View
-- Because houses are used so much, make a view separate from the organizations
-- table.
CREATE VIEW org_houses AS (
    SELECT org_id, org_name FROM organizations WHERE type = 'house'
);

-- House Members View
-- Because house membership is used so much, make a view separate from the
-- positions table.
CREATE VIEW org_house_membership AS (
    SELECT user_id, org_id, pos_id
    FROM org_houses NATURAL JOIN positions NATURAL JOIN position_holders
    WHERE UPPER(pos_name) = UPPER('Full Member') 
        OR UPPER(pos_name) = UPPER('Social Member')
);

-- Groups Table
-- Groups of members. Used for mailing lists, etc.
-- Groups are very similar to organizations, but more for internal groupings
-- of users.
CREATE TABLE groups (
    group_id    INT          NOT NULL AUTO_INCREMENT,
    group_name  VARCHAR(32)  NOT NULL,
    group_desc  VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (group_id),
    UNIQUE (group_name)
);

-- Group Members Table
CREATE TABLE group_members (
    user_id  INT NOT NULL,
    group_id INT NOT NULL,
    PRIMARY KEY (user_id, group_id)
);


