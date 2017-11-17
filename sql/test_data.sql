/* Test data / initial data */
INSERT INTO members(uid, last_name, first_name, email) VALUES
        ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com'),
     	('1984853', 'Eng', 'Robert', 'reng@caltech.edu');

INSERT INTO groups(group_id, group_name, type)
    VALUES (1, 'Donut Devteam', '');

INSERT INTO group_members(user_id, group_id) VALUES
       (1, 1),
       (2, 1);

INSERT INTO positions(group_id, pos_id, pos_name) VALUES
    (1, 1, 'Head'),
    (1, 2, 'Secretary');

INSERT INTO rooms(id, location, title, description) VALUES
    (1, 'SAC 23', 'ASCIT Screening Room', 'A room for watching DVDs and videos');

INSERT INTO room_reservations(room_id, user_id, reason, start_time, end_time) VALUES
    (1, 1, NULL, '2017-11-14 18:00:00', '2017-11-14 19:00:00'),
    (1, 2, 'Dank memes', '2017-11-15 12:00:00', '2017-11-15 13:00:00');