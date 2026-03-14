# 数据库模块说明（MySQL）

本目录用于管理“基于无人机校园垃圾检测系统”的数据库相关资源，包括建库建表脚本、迁移脚本与测试数据脚本。

## 目录结构

- schema：数据库结构初始化脚本
- migrations：后续版本演进迁移脚本
- seeds：演示数据或测试数据脚本

## 初始化说明

初始化脚本文件：schema/init.sql

该脚本已包含以下内容：

1. 创建数据库 campus_waste_db（IF NOT EXISTS）
2. 指定字符集 utf8mb4 与排序规则 utf8mb4_unicode_ci
3. 创建核心业务表并添加详细中文注释
4. 建立索引与外键约束

## 执行方式

请在 MySQL 客户端执行：

```sql
SOURCE database/schema/init.sql;
```

或使用命令行执行：

```bash
mysql -u root -p < database/schema/init.sql
```

## 已定义核心表

1. users：系统用户表（管理员、环卫人员）
2. drones：无人机设备表（状态、位置、活跃时间）
3. detection_records：垃圾检测记录表（图像、坐标、置信度）
4. cleaning_tasks：清理任务表（任务分配与完成状态）

## 设计要点

- 所有表均包含自增主键 id
- 所有表均包含 created_at 与 updated_at 时间字段
- 表名与字段名均采用 snake_case 规范
- 外键关系体现“检测 -> 任务”的业务闭环
- 检测结果与任务状态字段已建立常用索引以提升查询效率
