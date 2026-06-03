# ERP系统（初学者版）

一套基于Python Tkinter开发的企业资源管理系统，适用于中小型企业的业务管理需求。

## 📋 功能模块

| 模块 | 功能说明 |
|------|----------|
| 📦 商品管理 | 商品信息管理、库存查询、低库存预警 |
| 💰 销售管理 | 销售订单、销售统计、库存扣减 |
| 🏭 生产管理 | 生产订单、领料、入库、报废 |
| 📦 仓库管理 | 入库、出库、库存流水、盘点 |
| 🛠️ 售后管理 | 售后工单、设备管理 |
| 📦 物流管理 | 物流订单、跟踪 |
| 🔧 维修管理 | 维修记录、配件管理 |
| 📊 数据统计 | 各模块统计报表 |
| ⚙️ 系统配置 | 用户、角色、日志 |

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **GUI框架**: Tkinter（内置）
- **数据库**: MySQL 8.0+
- **驱动**: PyMySQL

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/erp-system.git
cd erp-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**

修改 `config/database.py` 中的数据库配置：
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'erp_system',
    'charset': 'utf8mb4'
}
```

4. **运行系统**
```bash
python main.py
```

## 📁 项目结构

```
erp_system/
├── main.py              # 主程序入口
├── init_data.py         # 初始化数据
├── config/              # 配置层
│   └── database.py      # 数据库连接与操作封装
├── services/            # 业务服务层
│   ├── product_service.py      # 商品服务
│   ├── sale_service.py         # 销售服务
│   ├── production_service.py   # 生产服务
│   ├── warehouse_service.py    # 仓库服务
│   ├── after_sales_service.py  # 售后服务
│   ├── logistics_service.py    # 物流服务
│   ├── maintenance_service.py  # 维修服务
│   └── statistics_service.py   # 统计服务
└── views/               # 界面视图层
    ├── product_view.py         # 商品管理界面
    ├── sale_view.py            # 销售管理界面
    ├── production_view.py      # 生产管理界面
    ├── warehouse_view.py       # 仓库管理界面
    ├── after_sales_view.py     # 售后管理界面
    ├── logistics_view.py       # 物流管理界面
    ├── maintenance_view.py     # 维修管理界面
    ├── statistics_view.py      # 数据统计界面
    └── system_view.py          # 系统配置界面
```

## 📌 数据库初始化

系统首次运行时会自动创建数据库和表结构，并初始化默认用户：
- 用户名: `admin`
- 密码: `admin`

## 📝 使用说明

1. 确保MySQL服务已启动
2. 运行 `main.py` 启动系统
3. 使用默认账号登录系统（后续版本会添加登录功能）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
