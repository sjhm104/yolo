CREATE DATABASE IF NOT EXISTS campus_waste_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE campus_waste_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS cleaning_tasks;
DROP TABLE IF EXISTS detection_records;
DROP TABLE IF EXISTS workers;
DROP TABLE IF EXISTS drones;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE workers (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	name VARCHAR(50) NOT NULL,
	phone VARCHAR(20) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE detection_records (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	video_source VARCHAR(100) NOT NULL,
	frame_time VARCHAR(20) NOT NULL,
	screenshot_url VARCHAR(255) NOT NULL,
	has_waste BOOLEAN NOT NULL DEFAULT FALSE,
	confidence FLOAT NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cleaning_tasks (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	record_id INT UNSIGNED NOT NULL,
	worker_id INT UNSIGNED NULL,
	status ENUM('pending', 'completed') NOT NULL DEFAULT 'pending',
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	completed_at DATETIME NULL,
	PRIMARY KEY (id),
	KEY idx_cleaning_tasks_record_id (record_id),
	KEY idx_cleaning_tasks_worker_id (worker_id),
	KEY idx_cleaning_tasks_status (status),
	CONSTRAINT fk_cleaning_tasks_record_id
		FOREIGN KEY (record_id)
		REFERENCES detection_records (id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT fk_cleaning_tasks_worker_id
		FOREIGN KEY (worker_id)
		REFERENCES workers (id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO workers (name, phone) VALUES
	('张三', '13800000001'),
	('李四', '13800000002'),
	('王五', '13800000003');
