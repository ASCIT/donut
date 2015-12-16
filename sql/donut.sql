DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    user_id int(11) NOT NULL AUTO_INCREMENT, -- Primary Key
    uid char(7) NOT NULL,  -- Unique
    last_name varchar(255) NOT NULL, 
    first_name varchar(255) NOT NULL,
    middle_name varchar(255), 
    email varchar(255) NOT NULL,
    phone varchar(64) DEFAULT NULL,
    gender tinyint(2) DEFAULT NULL, -- Numerical code that will be stored in code
    birthday date DEFAULT NULL,
    entry_year year(4) DEFAULT NULL,
    graduation_year year(4) DEFAULT NULL, -- Question: does this 1-to-1 denote year of school (frosh, soph)
    msc smallint(6) DEFAULT NULL,
    building varchar(32) DEFAULT NULL,
    room_num smallint(6) DEFAULT NULL,
    is_abroad bool DEFAULT 0,
    major varchar(16) DEFAULT NULL,
    major2 varchar(16) DEFAULT NULL,
    address varchar(255) DEFAULT NULL, -- Someone confirm how big this varchar should be.
    city varchar(64) DEFAULT NULL,
    state varchar(64) DEFAULT NULL,
    zip varchar(9) DEFAULT NULL,
    country varchar(64) DEFAULT NULL, 
    create_account_key char(32) DEFAULT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY (uid)
);

CREATE TABLE users(
    user_id int(11) NOT NULL,  -- Primary Key, Foreign Key to members(user_id) 
    username varchar(32) NOT NULL,    -- Unique
    last_login datetime DEFAULT NULL,
    password_hash varchar(255) NOT NULL,
    password_reset_key char(32) DEFAULT NULL,
    password_reset_expiration datetime DEFAULT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    UNIQUE KEY (username)
);

/* Test data / initial data */
-- Non-null constraint test.
INSERT INTO members(uid, last_name, first_name, email) 
    VALUES ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com'); 
           
