-- Audit log for the db_admin module. Every insert/update/delete performed
-- through the database explorer is recorded here with full before/after data.

CREATE TABLE IF NOT EXISTS db_admin_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    request_time DATETIME NOT NULL DEFAULT NOW(),
    action ENUM('insert', 'update', 'delete') NOT NULL,
    table_name VARCHAR(64) NOT NULL,
    row_pk VARCHAR(255) NOT NULL,
    old_data JSON NULL,
    new_data JSON NULL
);
