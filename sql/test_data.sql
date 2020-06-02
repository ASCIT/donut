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
INSERT INTO members(uid, last_name, first_name, email) VALUES
    ('2045251', 'Yu', 'Sean', 'ssyu@caltech.edu'),
    ('2077933', 'Lin', 'Rachel', 'rlin@caltech.edu');

INSERT INTO member_options(user_id, option_id, option_type) VALUES
    (3, 1, 'Major'),
    (3, 2, 'Minor');

INSERT INTO images(user_id, extension, image) VALUES
    (3, 'png', 'NOT_A_REAL_IMAGE');

INSERT INTO marketplace_categories(cat_title) VALUES
    ('Furniture'),
    ('Textbooks');

INSERT INTO marketplace_items(cat_id, user_id, item_title, item_details, item_condition, item_price) VALUES
    (1, 1, 'A table', "It's a pretty cool table, I guess", 'Good', 5.99);

INSERT INTO users(user_id, username, password_hash) VALUES
    (1, "dqu", ""),
    (2, "reng", ""),
    (3, "csander", ""),
    (4, "ruddock_pres", ""),
    (5, "rlin", "");

INSERT INTO groups(group_id, group_name, type, newsgroups, anyone_can_send) VALUES
    (1, 'Donut Devteam', '', 1, 1),
    (2, 'Ruddock House', 'house', 0, 0),
    (3, 'IHC', 'committee', 1, 0);

INSERT INTO positions(group_id, pos_id, pos_name, send, control, receive) VALUES
    (1, 1, 'Head', 1, 1, 1),
    (1, 2, 'Secretary', 1, 1, 1),
    (2, 3, 'Full Member', 1, 0, 1),
    (2, 4, 'President', 1, 1, 1),
    (3, 5, 'Member', 1, 0, 1);

INSERT INTO position_holders(pos_id, user_id) VALUES
    (1, 1),
    (1, 2),
    (3, 3),
    (4, 4),
    (4, 2),
    (5, 4),
    (5, 5);

INSERT INTO position_relations(pos_id_from, pos_id_to) VALUES
    (4, 5);

INSERT INTO rooms(room_id, location, title, description) VALUES
    (1, 'SAC 23', 'ASCIT Screening Room', 'A room for watching DVDs and videos');

/* bodfeedback */
INSERT INTO complaint_info(org, complaint_id, subject, resolved, uuid) VALUES
    (1, 1, 'Sub1', 0, UNHEX('F034CB412C0411E997ED021EF4D6E881')),
    (1, 2, 'Sub2', 1, '2');

INSERT INTO complaint_messages(complaint_id, time, message, poster, message_id) VALUES
    (1, '2018-01-01 00:00:00', 'Sample Message', 'Davis', 1),
    (1, '2018-01-02 00:00:00', 'Sample Message 2', 'Davis', 2),
    (2, '2018-01-03 00:00:00', 'This course is fun', 'Davis', 3);

INSERT INTO complaint_emails(complaint_id, email) VALUES
    (1, 'test@example.com'),
    (1, 'test2@example.com');

/* arcfeedback */
INSERT INTO complaint_info(org, complaint_id, subject, resolved, uuid) VALUES
    (2, 3, 'Sub2', 0, '3');

INSERT INTO complaint_messages(complaint_id, time, message, poster, message_id) VALUES
    (3, '2018-01-01 00:00:00', 'Sample Message', 'Davis', 4);

INSERT INTO permissions(permission_id, permission_type, resource_name,
       	    	        description) VALUES
    (1, 'Admin', 'ALL', 'Grants all other permissions -- FOR DEV ONLY'),
    (2, 'Edit', 'Rotation Info', 'IHC members may edit general rotation information'),
    (3, 'View', 'Directory Search Hidden Fields', 'Donut Admins may always view hidden fields in directory search'),
    (8, 'View', 'Bodfeedback summary', 'View a summary page of all bodfeedback'),
    (9, 'Edit', 'Bodfeedback', 'Mark a complaint read/unread'),
    (10, 'Edit', 'Bodfeedback emails', 'Add or remove subscribed emails from bodfeedback'),
    (11, 'View', 'Bodfeedback emails', 'View the list of subscribed emails on bodfeedback'),
    (33, 'Edit', 'Surveys', 'Create and manage surveys');

INSERT INTO position_permissions(pos_id, permission_id) VALUES
    (1, 1),
    (5, 2),
    (1, 3),
    (3, 33);


INSERT INTO courses(
    course_id, year, term, department, course_number, name,
    units_lecture, units_lab, units_homework
) VALUES
    (1, 2018, 1, 'CS', '124', 'Operating Systems', 3, 6, 3),
    (2, 2018, 1, 'Ph', '1a', 'Classical Mechanics and Electromagnetism', 4, 0, 5),
    (3, 2019, 2, 'CS', '21', 'Decidability and Tractability', 3, 0, 6),
    (4, 2019, 2, 'Ma', '1b', 'Calculus of One and Several Variables and Linear Algebra', 4, 0, 5),
    (5, 2018, 3, 'CS', '38', 'Algorithms', 3, 0, 6),
    (6, 2018, 3, 'Bi', '1', 'Principles of Biology', 4, 0, 5),
    -- These are just to test courses occuring in multiple terms:
    (7, 2018, 1, 'Ch', '3x', 'Experimental Methods in Solar Energy Conversion', 1, 3, 2),
    (8, 2019, 2, 'Ch', '3x', 'Experimental Methods in Solar Energy Conversion', 1, 3, 2),
    (9, 2018, 3, 'Ch', '3x', 'Experimental Methods in Solar Energy Conversion', 1, 3, 2);
INSERT INTO instructors(instructor_id, instructor) VALUES
    (1, 'Pinkston, D'),
    (2, 'Cheung, C'),
    (3, 'Umans, C'),
    (4, 'Kechris, A'),
    (5, 'Rains, E'),
    (6, 'Vidick, T'),
    (7, 'Meyerowitz, E / Zinn, K'),
    (8, 'Mendez, J'),
    (9, 'Jendez, M');
INSERT INTO grades_types(grades_type_id, grades_type) VALUES
    (1, ''),
    (2, 'PASS-FAIL'),
    (3, 'LETTER');
INSERT INTO sections(course_id, section_number, instructor_id, grades_type_id, times, locations) VALUES
    (1, 1, 1, 1, 'MWF 13:00 - 13:55', '213 ANB'),
    (2, 1, 2, 2, 'MR 13:00 - 13:55\nWF 11:00 - 11:55', 'B111 DWN\n201 BRG'),
    (2, 2, 2, 2, 'MR 15:00 - 15:55\nWF 11:00 - 11:55', 'B111 DWN\n201 BRG'),
    (2, 3, 2, 2, 'WF 11:00 - 11:55\nMR 13:00 - 13:55', '201 BRG\n103 DWN'),
    (3, 1, 3, 3, 'MWF 13:00 - 13:55', '105 ANB'),
    (4, 1, 4, 2, 'MWF 10:00 - 10:55\nR 09:00 - 09:55', '119 KRK\n103 DWN'),
    (4, 2, 4, 2, 'MWF 10:00 - 10:55\nR 09:00 - 09:55', '119 KRK\n119 DWN'),
    (4, 7, 5, 2, 'MWF 10:00 - 10:55\nR 09:00 - 09:55', '310 LINDE\nB111 DWN'),
    (4, 8, 5, 2, 'R 10:00 - 10:55\nMWF 10:00 - 10:55', '142 KCK\n310 LINDE'),
    (5, 1, 6, 1, 'TR 09:00 - 10:25', '105 ANB'),
    (6, 1, 7, 3, 'M 19:00 - 19:55\nTR 13:00 - 14:25', '200 BRD\n119 KRK'),
    (6, 2, 7, 3, 'TR 13:00 - 14:25\nM 20:00 - 20:55', '119 KRK\n200 BRD'),
    (6, 3, 7, 3, 'TR 13:00 - 14:25\nT 19:00 - 19:55', '119 KRK\n200 BRD'),
    (7, 1, 8, 2, 'F 09:00 - 09:55\nW 13:00 - 15:55', '151 CRL\n107 MEAD'),
    (8, 1, 8, 2, 'F 09:00 - 09:55\nW 13:00 - 15:55', '147 NYS\n107 MEAD'),
    (9, 1, 9, 2, 'W 13:00 - 15:55\nF 09:00 - 09:55', '107 MEAD\n147 NYS');
