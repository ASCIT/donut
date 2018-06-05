DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS position_permissions;

CREATE TABLE permissions (
       permission_id INT NOT NULL AUTO_INCREMENT,
       permission_name VARCHAR(255),
PRIMARY KEY(permission_id)
);

CREATE TABLE position_permissions (
       pos_id INT NOT NULL,
       permission_id INT NOT NULL,
FOREIGN KEY(pos_id) REFERENCES positions(pos_id) 
ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY(permission_id) REFERENCES permissions(permission_id)
ON UPDATE CASCADE ON DELETE CASCADE
); 
