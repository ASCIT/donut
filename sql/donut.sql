DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS privacies;
DROP TABLE IF EXISTS member_options;
DROP TABLE IF EXISTS options;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    user_id            INT          NOT NULL AUTO_INCREMENT, 
    uid                CHAR(7)      NOT NULL,  
    last_name          VARCHAR(255) NOT NULL,
    first_name         VARCHAR(255) NOT NULL,
    middle_name        VARCHAR(255) DEFAULT NULL,
    email              VARCHAR(255) NOT NULL,
    phone              VARCHAR(64)  DEFAULT NULL,
    gender             TINYINT      DEFAULT NULL, -- Numerical code that will be stored in code
    gender_custom      VARCHAR(32)  DEFAULT NULL, -- TODO: Implement showing custom gender options
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
    UNIQUE KEY (uid)
);

CREATE TABLE options (
    option_id     INT         NOT NULL AUTO_INCREMENT,
    option_name   VARCHAR(16) NOT NULL,
    option_type   VARCHAR(8)  NOT NULL,
    PRIMARY KEY (option_id)
);

-- Many to many relationship between members and options
CREATE TABLE member_options (
    user_id     INT,
    option_id   INT, 
    PRIMARY KEY (user_id, option_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    FOREIGN KEY (option_id) REFERENCES options(option_id)
); 

-- Directory privacies for who can see data.
-- Default is Caltech?
CREATE TABLE privacies (
    priv_id     INT,
    priv_name   VARCHAR(8) NOT NULL,
    priv_desc   VARCHAR(64) NOT NULL,
    PRIMARY KEY (priv_id),
    UNIQUE (priv_name)
);

CREATE TABLE users (
    user_id                   INT,
    username                  VARCHAR(32)  NOT NULL,   
    last_login                DATETIME     DEFAULT NULL,
    password_hash             VARCHAR(255) NOT NULL,
    password_reset_key        CHAR(32)     DEFAULT NULL,
    password_reset_expiration DATETIME     DEFAULT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    UNIQUE KEY (username)
);

