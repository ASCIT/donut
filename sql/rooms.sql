DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS room_reservations;

CREATE TABLE rooms (
	id INT NOT NULL AUTO_INCREMENT,
	location VARCHAR(50) NOT NULL, -- e.g. SAC 23
	title VARCHAR(50) NOT NULL, -- e.g. ASCIT Screening Room
	description VARCHAR(255) NOT NULL, -- e.g. A room for watching DVDs and videos

	PRIMARY KEY(id),
	UNIQUE KEY(location)
);

CREATE TABLE room_reservations(
	id INT NOT NULL AUTO_INCREMENT,
	room_id INT NOT NULL,
	user_id INT NOT NULL,
	reason TEXT,
	start_time DATETIME NOT NULL,
	end_time DATETIME NOT NULL,

	PRIMARY KEY(id),
	FOREIGN KEY(user_id) REFERENCES members(user_id) ON DELETE CASCADE,
	FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);