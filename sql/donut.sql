DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    user_id INT(11) NOT NULL AUTO_INCREMENT, -- Primary Key
    uid CHAR(7) NOT NULL,  -- Unique
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(64) DEFAULT NULL,
    gender TINYINT(2) DEFAULT NULL, -- Numerical code that will be stored in code
    birthday DATE DEFAULT NULL,
    entry_year YEAR(4) DEFAULT NULL,
    graduation_year YEAR(4) DEFAULT NULL, -- Question: does this 1-to-1 denote year of school (frosh, soph)
    msc SMALLINT(6) DEFAULT NULL,
    building VARCHAR(32) DEFAULT NULL,
    room_num SMALLINT(6) DEFAULT NULL,
    is_abroad BOOL DEFAULT 0,
    major VARCHAR(16) DEFAULT NULL,
    major2 VARCHAR(16) DEFAULT NULL,
    address VARCHAR(255) DEFAULT NULL, -- Someone confirm how big this varchar should be.
    city VARCHAR(64) DEFAULT NULL,
    state VARCHAR(64) DEFAULT NULL,
    zip VARCHAR(9) DEFAULT NULL,
    country VARCHAR(64) DEFAULT NULL,
    create_account_key CHAR(32) DEFAULT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY (uid)
);

CREATE TABLE users(
    user_id INT(11) NOT NULL,  -- Primary Key, Foreign Key to members(user_id)
    username VARCHAR(32) NOT NULL,    -- Unique
    last_login DATETIME DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_reset_key CHAR(32) DEFAULT NULL,
    password_reset_expiration DATETIME DEFAULT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    UNIQUE KEY (username)
);

/* Test data / initial data */
-- Non-null constraint test.
INSERT INTO members(uid, last_name, first_name, email)
    VALUES ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com');
