/* Test data / initial data */
INSERT INTO members(uid, last_name, first_name, email) VALUES
    ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com'),
    ('1984853', 'Eng', 'Robert', 'reng@caltech.edu');

INSERT INTO users(user_id, username) VALUES
    (1, "dqu"),
    (2, "reng");

INSERT INTO groups(group_id, group_name, type) VALUES
    (1, 'Donut Devteam', '');

INSERT INTO group_members(user_id, group_id) VALUES
    (1, 1),
    (2, 1);

INSERT INTO positions(group_id, pos_id, pos_name) VALUES
    (1, 1, 'Head'),
    (1, 2, 'Secretary');

INSERT INTO position_holders(group_id, pos_id, user_id) VALUES
    (1, 1, 1),
    (1, 1, 2);

INSERT INTO rooms(room_id, location, title, description) VALUES
    (1, 'SAC 23', 'ASCIT Screening Room', 'A room for watching DVDs and videos');
