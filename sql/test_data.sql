/* Test data / initial data */
INSERT INTO buildings(building_id, building_name) VALUES
    (1, 'Ruddock House');
INSERT INTO options(option_id, option_name) VALUES
    (1, 'CS'),
    (2, 'MechE');

INSERT INTO members(uid, last_name, first_name, email, phone) VALUES
    ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com', NULL),
    ('1984853', 'Eng', 'Robert', 'reng@caltech.edu', '+11234567890');
INSERT INTO members(
    user_id,
    uid,
    last_name,
    first_name,
    preferred_name,
    middle_name,
    email,
    phone,
    gender,
    gender_custom,
    birthday,
    entry_year,
    graduation_year,
    msc,
    city,
    state,
    building_id,
    room
) VALUES (
    3,
    '2078141',
    'Sander',
    'Caleb',
    'Cleb',
    'Caldwell',
    'csander@caltech.edu',
    '6178003347',
    0,
    'Male',
    '1999-05-08',
    2017,
    2021,
    707,
    'Lincoln',
    'MA',
    1,
    '203'
);
INSERT INTO members(uid, last_name, first_name, email, phone) VALUES
    ('2045251', 'Yu', 'Sean', 'ssyu@caltech.edu', NULL);


INSERT INTO member_options(user_id, option_id, option_type) VALUES
    (3, 1, 'Major'),
    (3, 2, 'Minor');

INSERT INTO images(user_id, extension, image) VALUES
    (3, 'png', 'NOT_A_REAL_IMAGE');

INSERT INTO users(user_id, username) VALUES
    (1, "dqu"),
    (2, "reng"),
    (3, "csander");

INSERT INTO groups(group_id, group_name, type) VALUES
    (1, 'Donut Devteam', ''),
    (2, 'Ruddock House', 'house'),
    (3, 'IHC', 'committee');

INSERT INTO positions(group_id, pos_id, pos_name) VALUES
    (1, 1, 'Head'),
    (1, 2, 'Secretary'),
    (2, 3, 'Full Member'),
    (2, 4, 'President'),
    (3, 5, 'Member');

INSERT INTO position_holders(pos_id, user_id) VALUES
    (1, 1),
    (1, 2),
    (3, 3),
    (4, 4),
    (4, 2),
    (5, 4);


INSERT INTO position_relations(pos_id_from, pos_id_to) VALUES
    (4, 5);

INSERT INTO rooms(room_id, location, title, description) VALUES
    (1, 'SAC 23', 'ASCIT Screening Room', 'A room for watching DVDs and videos');

INSERT INTO permissions(permission_id, permission_name) VALUES
    (1, 'Ruddock full member'),
    (2, 'IHC member');

INSERT INTO position_permissions(pos_id, permission_id) VALUES
    (3, 1),
    (5, 2);
