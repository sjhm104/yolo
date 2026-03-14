CREATE DATABASE IF NOT EXISTS campus_waste_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE campus_waste_db;

CREATE TABLE IF NOT EXISTS users (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户主键ID，系统内用户的唯一标识，自增生成，供其他业务表进行关联引用',
	username VARCHAR(50) NOT NULL COMMENT '用户登录账号，要求全局唯一，用于身份认证与后台登录',
	password_hash VARCHAR(255) NOT NULL COMMENT '用户密码哈希值，存储加密后的密码摘要，不保存明文密码，保障账户安全',
	real_name VARCHAR(50) NOT NULL COMMENT '用户真实姓名，用于任务分配、人员管理与报表展示',
	role ENUM('admin', 'cleaner') NOT NULL DEFAULT 'cleaner' COMMENT '用户角色类型：admin表示系统管理员，cleaner表示环卫执行人员，默认cleaner',
	phone VARCHAR(20) NULL COMMENT '用户联系电话，便于紧急联络、任务通知与现场沟通',
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，表示该用户数据首次写入数据库的时间戳',
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间，表示该用户数据最近一次被修改的时间戳',
	PRIMARY KEY (id),
	UNIQUE KEY uk_users_username (username),
	KEY idx_users_username (username),
	KEY idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表，存储管理员与环卫人员的基础账户信息';

CREATE TABLE IF NOT EXISTS drones (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '无人机主键ID，系统内无人机设备的唯一标识，自增生成',
	drone_code VARCHAR(50) NOT NULL COMMENT '无人机唯一编号，对应设备铭牌编号或系统编码，用于设备唯一识别',
	status ENUM('idle', 'flying', 'offline') NOT NULL DEFAULT 'offline' COMMENT '无人机运行状态：idle空闲待命，flying飞行作业中，offline离线不可用，默认offline',
	current_lat DECIMAL(10,7) NULL COMMENT '无人机当前纬度坐标，单位为度，采用WGS84坐标系，允许为空表示暂未上报',
	current_lng DECIMAL(10,7) NULL COMMENT '无人机当前经度坐标，单位为度，采用WGS84坐标系，允许为空表示暂未上报',
	last_active_time DATETIME NULL COMMENT '无人机最后活跃时间，表示设备最近一次心跳或数据上传时间',
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，表示该无人机设备信息首次入库时间',
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间，表示该无人机设备信息最近一次更新的时间戳',
	PRIMARY KEY (id),
	UNIQUE KEY uk_drones_drone_code (drone_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='无人机设备表，维护设备编号、状态与定位等运行信息';

CREATE TABLE IF NOT EXISTS detection_records (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '检测记录主键ID，系统每次图像识别结果的唯一标识，自增生成',
	drone_id INT UNSIGNED NULL COMMENT '拍摄无人机ID，外键关联drones.id，允许为空以兼容设备记录被删除后的历史数据保留',
	image_url VARCHAR(255) NOT NULL COMMENT '无人机回传图像的相对路径或资源地址，用于结果回显与后续复核',
	latitude DECIMAL(10,7) NOT NULL COMMENT '拍摄点纬度坐标，单位为度，采用WGS84坐标系',
	longitude DECIMAL(10,7) NOT NULL COMMENT '拍摄点经度坐标，单位为度，采用WGS84坐标系',
	has_waste BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否检测出垃圾，TRUE表示检测到垃圾目标，FALSE表示未检测到',
	confidence FLOAT NULL COMMENT 'AI识别置信度，取值通常在0到1之间，例如0.95表示95%的识别置信水平',
	detected_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '检测识别时间，表示算法完成当前记录识别的业务时间点',
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，表示该检测记录写入数据库的时间戳',
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间，表示该检测记录最近一次被修订的时间戳',
	PRIMARY KEY (id),
	KEY idx_detection_records_has_waste (has_waste),
	KEY idx_detection_records_drone_id (drone_id),
	CONSTRAINT fk_detection_records_drone_id
		FOREIGN KEY (drone_id)
		REFERENCES drones (id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='垃圾检测记录表，保存无人机图像识别结果与地理位置信息';

CREATE TABLE IF NOT EXISTS cleaning_tasks (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '清理任务主键ID，系统内每条清理任务的唯一标识，自增生成',
	record_id INT UNSIGNED NOT NULL COMMENT '关联检测记录ID，外键关联detection_records.id，标识该任务来源于哪条检测结果',
	cleaner_id INT UNSIGNED NULL COMMENT '分配的环卫人员ID，外键关联users.id，允许为空表示任务尚未分配具体执行人',
	status ENUM('pending', 'assigned', 'completed') NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending待处理，assigned已分配，completed已完成，默认pending',
	assigned_time DATETIME NULL COMMENT '任务分配时间，记录任务指派给环卫人员的业务时间点',
	completed_time DATETIME NULL COMMENT '任务完成时间，记录现场清理完成并回传确认的业务时间点',
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，表示该清理任务首次生成入库的时间戳',
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间，表示该清理任务最近一次状态或信息变更时间戳',
	PRIMARY KEY (id),
	KEY idx_cleaning_tasks_record_id (record_id),
	KEY idx_cleaning_tasks_cleaner_id (cleaner_id),
	KEY idx_cleaning_tasks_status (status),
	CONSTRAINT fk_cleaning_tasks_record_id
		FOREIGN KEY (record_id)
		REFERENCES detection_records (id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT fk_cleaning_tasks_cleaner_id
		FOREIGN KEY (cleaner_id)
		REFERENCES users (id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='清理任务表，将检测到的垃圾记录转化为可跟踪的环卫处置任务';
