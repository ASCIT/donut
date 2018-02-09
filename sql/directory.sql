DROP TABLE IF EXISTS images;

CREATE TABLE images (
    user_id     INT         NOT NULL,
    extension   VARCHAR(5)  NOT NULL,
    image       BLOB        NOT NUll,
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    UNIQUE (user_id)
);