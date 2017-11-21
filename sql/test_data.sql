/* Test data / initial data */
INSERT INTO members(uid, last_name, first_name, email) VALUES
        ('1957540', 'Qu', 'David', 'davidqu12345@gmail.com'),
     	('1984853', 'Eng', 'Robert', 'reng@caltech.edu');

INSERT INTO marketplace_categories(cat_title, cat_order) VALUES
    ('Furniture', 1),
    ('Textbooks', 2);

INSERT INTO marketplace_items(cat_id, user_id, item_title, item_details, item_condition, item_price) VALUES
    (1, 1, 'A table', "It\'s a pretty cool table, I guess", 'Good', 5.99);

INSERT INTO groups(group_id, group_name, type)
    VALUES (1, 'Donut Devteam', '');

INSERT INTO group_members(user_id, group_id) VALUES
       (1, 1),
       (2, 1);

INSERT INTO positions(group_id, pos_id, pos_name) VALUES
    (1, 1, 'Head'),
    (1, 2, 'Secretary');
