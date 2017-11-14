/* Test data / initial data */
INSERT INTO members(uid, last_name, first_name, email)
    VALUES ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com');

INSERT INTO groups(group_id, group_name, type)
    VALUES (1, 'Donut Devteam', '');

INSERT INTO positions(group_id, pos_id, pos_name) VALUES
    (1, 1, 'Head'),
    (1, 2, 'Secretary');