DROP TABLE IF EXISTS marketplace_images;
DROP TABLE IF EXISTS marketplace_items;
DROP TABLE IF EXISTS marketplace_categories;
DROP TABLE IF EXISTS marketplace_textbooks;

CREATE TABLE marketplace_textbooks (
	textbook_id INT NOT NULL,
	textbook_title VARCHAR(255) NOT NULL,
	textbook_author VARCHAR(255) NOT NULL,
PRIMARY KEY(textbook_id),
UNIQUE KEY (textbook_title, textbook_author)
);

CREATE TABLE marketplace_categories (
	cat_id INT NOT NULL,
	cat_title VARCHAR(100) NOT NULL,
	cat_active BOOLEAN DEFAULT TRUE,
	cat_order INT,
PRIMARY KEY(cat_id),
UNIQUE KEY(cat_title)
);


CREATE TABLE marketplace_items (

	item_id INT NOT NULL,
	cat_id INT NOT NULL,
	user_id INT NOT NULL,
	item_title VARCHAR(255) NOT NULL,
	item_details TEXT,
	item_condition VARCHAR(20),
	item_price NUMERIC(6,2),
	item_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	item_active BOOLEAN DEFAULT true,
	textbook_id INT,
	textbook_edition VARCHAR(20),
	textbook_isbn VARCHAR(13),
PRIMARY KEY(item_id),
FOREIGN KEY(cat_id) REFERENCES marketplace_categories(cat_id),
FOREIGN KEY(user_id) REFERENCES users(user_id),
FOREIGN KEY(textbook_id) REFERENCES marketplace_textbooks(textbook_id)
);

CREATE TABLE marketplace_images (
	img_id INT NOT NULL,
	item_id INT NOT NULL,
	img_link VARCHAR(255),
PRIMARY KEY(img_id),
FOREIGN KEY(item_id) REFERENCES marketplace_items(item_id)
);


