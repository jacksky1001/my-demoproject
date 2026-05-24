# 视力中心蓝牙数据汇聚系统 - 阶段2设计文档

**版本**: 0.1.0
**日期**: 2026-05-23
**阶段**: 2 - 核心功能完善

---

## 1. 概述

基于阶段1的基础，阶段2完善核心功能，实现真实硬件对接和数据持久化。

## 2. 设计约束

| 项 | 决策 |
|------|------|
| **数据持久化** | SQLite数据库，替代内存存储 |
| **数据清理** | 自动清理（默认90天）+ 手动清理API |
| **打印队列** | 简单内存队列，服务重启后丢失 |
| **蓝牙打印机** | 直接实现Windows蓝牙打印（bleak库） |
| **设备数据接收** | 完整设计，假设能从蓝牙打印流中提取数据 |
| **前端** | 先实现基础功能，UI美化阶段3再做 |
| **生物测量仪** | PDF解析不了就先忽略 |

---

## 3. 架构设计

### 3.1 分层架构

继续保持清晰的分层架构：

```
┌─────────────────────────────────────────────────┐
│  API Layer + Frontend (新增设备管理/队列等API)  │
├─────────────────────────────────────────────────┤
│  Service Layer (新增队列服务、数据管理服务)      │
├─────────────────────────────────────────────────┤
│  Device Abstraction Layer (新增蓝牙服务端)       │
├─────────────────────────────────────────────────┤
│  Hardware Abstraction Layer (新增真实蓝牙打印)    │
├─────────────────────────────────────────────────┤
│  Infrastructure Layer (新增SQLite存储)           │
└─────────────────────────────────────────────────┘
```

---

## 4. 模块设计

### 4.1 新增模块

| 模块 | 位置 | 说明 |
|------|------|------|
| `database.py` | `src/core/` | SQLite数据库连接和管理 |
| `schemas.py` | `src/models/` | 数据库表结构定义 |
| `queue_service.py` | `src/services/` | 打印队列管理服务 |
| `data_management_service.py` | `src/services/` | 数据管理服务（查询、清理等） |
| `screening_parser.py` | `src/parsers/` | 视力筛查仪数据解析器 |
| `biometer_parser.py` | `src/parsers/` | 眼生物测量仪解析器（可选） |
| `bluetooth_server.py` | `src/adapters/` | 蓝牙SPP服务端（接收设备数据） |

### 4.2 修改模块

| 模块 | 位置 | 修改说明 |
|------|------|------|
| `printer_driver.py` | `src/drivers/` | 实现真实蓝牙打印机驱动 |
| `routes.py` | `src/api/` | 新增数据管理、队列管理、设备管理API |
| `views/*` | `web/src/views/` | 完善前端基础功能 |

---

## 5. 核心模块详细设计

### 5.1 SQLite 持久化

#### 5.1.1 数据库表结构

```sql
-- 检查记录表
CREATE TABLE IF NOT EXISTS records (
    id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    device_type TEXT NOT NULL,
    device_id TEXT,
    check_time DATETIME NOT NULL,
    data_json TEXT NOT NULL,  -- JSON格式存储完整数据
    printed BOOLEAN DEFAULT 0,
    print_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 打印队列表（预留结构，阶段2先用内存队列）
CREATE TABLE IF NOT EXISTS print_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending/printing/completed/failed
    retry_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_records_check_time ON records(check_time);
CREATE INDEX IF NOT EXISTS idx_records_patient_id ON records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_device_type ON records(device_type);
```

#### 5.1.2 数据管理服务

**职责**：
- 数据CRUD操作
- 按条件查询（时间范围、患者、设备类型）
- 自动清理过期数据（启动时 + 定时）
- 手动清理API
- 数据导出（JSON/CSV）

**API接口**：
- `GET /api/records?start=&end=&patient=&device=&page=&page_size=` - 查询记录
- `DELETE /api/records/{id}` - 删除单条记录
- `DELETE /api/records/batch?ids=` - 批量删除
- `POST /api/records/cleanup` - 手动触发清理
- `GET /api/records/export?format=json/csv` - 导出数据

### 5.2 真实蓝牙打印机驱动

**实现方案**：
- 使用 `bleak` 库进行蓝牙通信
- 扫描附近蓝牙设备
- 连接到打印机的SPP服务
- 发送ESC/POS命令
- 监控连接状态

**流程**：
1. 扫描蓝牙设备
2. 用户选择打印机
3. 建立BLE/SPP连接
4. 发送打印命令
5. 监控连接状态
6. 异常处理

### 5.3 蓝牙SPP服务端

**实现方案**：
- 系统模拟蓝牙打印机角色
- 使用蓝牙库创建SPP服务
- 等待设备连接
- 接收打印流数据
- 解析数据提取结构化内容
- 保存到数据库
- 触发自动打印

### 5.4 设备数据解析器

#### 5.4.1 视力筛查仪解析器

**职责**：
- 从蓝牙打印流中识别视力筛查数据
- 提取患者信息、检查结果
- 映射到统一数据模型

#### 5.4.2 眼生物测量仪解析器（可选）

**实现条件**：如果PDF文档能解析出协议就实现，否则跳过

---

## 6. 前端功能范围

### 6.1 页面功能清单

| 页面 | 功能 |
|------|------|
| **Dashboard** | 记录列表、查询、打印操作（基础已有，补充查询） |
| **设备管理** | 蓝牙设备扫描、打印机配置、连接状态 |
| **打印队列** | 队列显示、手动重试、取消任务 |
| **历史记录** | 查询历史数据、时间范围筛选 |
| **系统设置** | 数据保留天数、打印机选择、自动打印开关 |

---

## 7. 实现顺序

### P0 优先级
1. SQLite持久化 + 数据管理服务
2. 视力筛查仪数据解析器（框架）
3. 真实蓝牙打印机驱动
4. 蓝牙SPP服务端（接收数据框架）

### P1 优先级
5. 前端完整基础功能
6. 眼生物测量仪解析器（可选）

---

## 8. 接口设计

### 8.1 新增API接口

```
# 数据管理
GET    /api/records?start=&end=&patient=&device=
DELETE /api/records/{id}
DELETE /api/records/batch?ids=
POST   /api/records/cleanup
GET    /api/records/export

# 打印队列
GET    /api/queue
POST   /api/queue/{record_id}
DELETE /api/queue/{id}
POST   /api/queue/{id}/retry

# 设备管理
GET    /api/devices/bluetooth/scan
GET    /api/devices
POST   /api/devices
PUT    /api/devices/{id}
DELETE /api/devices/{id}
POST   /api/devices/{id}/connect
POST   /api/devices/{id}/disconnect
```

---

**文档结束**
