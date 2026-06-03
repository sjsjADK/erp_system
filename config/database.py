# 数据库配置模块
# 用于连接MySQL数据库

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'erp_system',
    'charset': 'utf8mb4'
}

def get_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_query(sql, params=None):
    """执行查询操作"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"查询失败: {e}")
        conn.close()
        return None

def execute_update(sql, params=None):
    """执行增删改操作"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        #提交事务，确保数据写入数据库
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"执行失败: {e}")
        #回滚事务，确保数据库状态一致，没commit的事务不会写入数据库
        conn.rollback()
        conn.close()
        return False

def execute_many(sql, params_list):
    """执行批量插入操作"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"批量执行失败: {e}")
        conn.rollback()
        conn.close()
        return False

def init_database():
    """初始化数据库和表"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS erp_system")
        cursor.execute("USE erp_system")

        # ============ 组织结构表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bureaus (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL COMMENT '路局名称',
                code VARCHAR(50) UNIQUE COMMENT '路局编码',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路局表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS segments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                bureau_id INT NOT NULL COMMENT '路局ID',
                name VARCHAR(100) NOT NULL COMMENT '站段名称',
                code VARCHAR(50) UNIQUE COMMENT '站段编码',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (bureau_id) REFERENCES bureaus(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站段表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                segment_id INT NOT NULL COMMENT '站段ID',
                name VARCHAR(100) NOT NULL COMMENT '站点名称',
                code VARCHAR(50) UNIQUE COMMENT '站点编码',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (segment_id) REFERENCES segments(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点表'
        """)

        # ============ 用户权限表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL COMMENT '角色名称',
                permissions TEXT COMMENT '权限JSON',
                data_scope VARCHAR(20) DEFAULT 'all' COMMENT '数据范围',
                sort_order INT DEFAULT 0 COMMENT '排序',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
                real_name VARCHAR(50) COMMENT '真实姓名',
                password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
                phone VARCHAR(20) COMMENT '电话',
                email VARCHAR(100) COMMENT '邮箱',
                position VARCHAR(50) COMMENT '职位',
                department VARCHAR(50) COMMENT '部门',
                role_ids VARCHAR(200) COMMENT '角色ID列表',
                data_scope VARCHAR(20) DEFAULT 'all' COMMENT '数据范围',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                last_login TIMESTAMP NULL COMMENT '最后登录时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'
        """)

        # ============ 客户表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL COMMENT '客户姓名',
                phone VARCHAR(20) COMMENT '电话',
                wechat VARCHAR(50) COMMENT '微信',
                address VARCHAR(200) COMMENT '地址',
                bureau_id INT COMMENT '路局ID',
                segment_id INT COMMENT '站段ID',
                station_id INT COMMENT '站点ID',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (bureau_id) REFERENCES bureaus(id),
                FOREIGN KEY (segment_id) REFERENCES segments(id),
                FOREIGN KEY (station_id) REFERENCES stations(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户表'
        """)

        # ============ 产品分类与产品表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL COMMENT '分类名称',
                code VARCHAR(50) UNIQUE COMMENT '分类编码',
                parent_id INT DEFAULT 0 COMMENT '父分类ID',
                sort_order INT DEFAULT 0 COMMENT '排序',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品分类表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY AUTO_INCREMENT,
                product_code VARCHAR(50) UNIQUE NOT NULL COMMENT '商品编码',
                name VARCHAR(100) NOT NULL COMMENT '商品名称',
                model VARCHAR(50) COMMENT '型号',
                category_id INT COMMENT '分类ID',
                spec VARCHAR(100) COMMENT '规格',
                price DECIMAL(10, 2) NOT NULL COMMENT '单价',
                stock INT DEFAULT 0 COMMENT '库存数量',
                unit VARCHAR(20) DEFAULT '件' COMMENT '单位',
                supplier VARCHAR(100) COMMENT '供应商',
                status TINYINT DEFAULT 1 COMMENT '状态 0-禁用 1-启用',
                description TEXT COMMENT '商品描述',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品表'
        """)
        
        # 检查并添加缺失字段
        cursor.execute("SHOW COLUMNS FROM products LIKE 'model'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE products ADD COLUMN model VARCHAR(50)")
        cursor.execute("SHOW COLUMNS FROM products LIKE 'category_id'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE products ADD COLUMN category_id INT")
        cursor.execute("SHOW COLUMNS FROM products LIKE 'spec'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE products ADD COLUMN spec VARCHAR(100)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL COMMENT '零部件名称',
                model VARCHAR(50) COMMENT '型号',
                category VARCHAR(50) COMMENT '分类',
                unit VARCHAR(20) DEFAULT '件' COMMENT '单位',
                price DECIMAL(10, 2) COMMENT '单价',
                stock INT DEFAULT 0 COMMENT '库存',
                status TINYINT DEFAULT 1 COMMENT '状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='零部件表'
        """)

        # ============ 卡号管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_management (
                id INT PRIMARY KEY AUTO_INCREMENT,
                card_no VARCHAR(50) UNIQUE NOT NULL COMMENT '卡号',
                bureau_id INT COMMENT '所属路局',
                status TINYINT DEFAULT 1 COMMENT '状态 1-可用 2-待入库 3-已入库 4-占用',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (bureau_id) REFERENCES bureaus(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='卡号管理表'
        """)

        # ============ SN码管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_sn_pools (
                id INT PRIMARY KEY AUTO_INCREMENT,
                model VARCHAR(50) NOT NULL COMMENT '产品型号',
                start_sn VARCHAR(50) NOT NULL COMMENT '起始SN',
                end_sn VARCHAR(50) NOT NULL COMMENT '结束SN',
                status TINYINT DEFAULT 1 COMMENT '状态 1-可用 2-部分使用 3-已用完',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SN码池表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_sn_pool_items (
                id INT PRIMARY KEY AUTO_INCREMENT,
                pool_id INT NOT NULL COMMENT 'SN池ID',
                sn VARCHAR(50) UNIQUE NOT NULL COMMENT 'SN码',
                status TINYINT DEFAULT 1 COMMENT '状态 1-可用 2-预留 3-已使用',
                reserved_order_id INT COMMENT '预留订单ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (pool_id) REFERENCES device_sn_pools(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SN码明细'
        """)

        # ============ 生产管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '生产订单号',
                product_id INT NOT NULL COMMENT '产品ID',
                plan_qty INT NOT NULL COMMENT '计划数量',
                actual_qty INT DEFAULT 0 COMMENT '实际数量',
                plan_date DATE COMMENT '计划日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待生产 2-生产中 3-已完成 4-已取消',
                responsible VARCHAR(50) COMMENT '负责人',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产订单表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_requisitions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                req_no VARCHAR(50) UNIQUE NOT NULL COMMENT '领料单号',
                production_order_id INT COMMENT '生产订单ID',
                requester VARCHAR(50) NOT NULL COMMENT '领料人',
                req_date DATE NOT NULL COMMENT '领料日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待审批 2-已审批 3-已作废',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (production_order_id) REFERENCES production_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产领料单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_requisition_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                req_id INT NOT NULL COMMENT '领料单ID',
                part_id INT NOT NULL COMMENT '零部件ID',
                part_name VARCHAR(100) NOT NULL COMMENT '零部件名称',
                quantity INT NOT NULL COMMENT '领料数量',
                unit VARCHAR(20) COMMENT '单位',
                FOREIGN KEY (req_id) REFERENCES material_requisitions(id),
                FOREIGN KEY (part_id) REFERENCES parts(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='领料明细'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_stock_in (
                id INT PRIMARY KEY AUTO_INCREMENT,
                in_no VARCHAR(50) UNIQUE NOT NULL COMMENT '入库单号',
                production_order_id INT COMMENT '生产订单ID',
                in_date DATE NOT NULL COMMENT '入库日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-草稿 2-待审批 3-已审批 4-已作废',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (production_order_id) REFERENCES production_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产入库单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_stock_in_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                in_id INT NOT NULL COMMENT '入库单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                card_no VARCHAR(50) COMMENT '卡号',
                quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
                FOREIGN KEY (in_id) REFERENCES production_stock_in(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产入库明细'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_scrap_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                scrap_no VARCHAR(50) UNIQUE NOT NULL COMMENT '报废单号',
                source_type TINYINT NOT NULL COMMENT '来源 1-生产报废 2-维修报废',
                source_id INT COMMENT '来源ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                quantity INT NOT NULL COMMENT '报废数量',
                reason VARCHAR(200) COMMENT '报废原因',
                responsible VARCHAR(50) COMMENT '责任人',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待审批 2-已审批',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产报废记录表'
        """)

        # ============ 仓库管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_in_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '入库单号',
                in_type TINYINT NOT NULL COMMENT '入库类型 1-采购入库 2-退货入库 3-其他',
                source_no VARCHAR(50) COMMENT '来源单号',
                handler VARCHAR(50) COMMENT '经办人',
                warehouse VARCHAR(50) COMMENT '仓库',
                location VARCHAR(50) COMMENT '库位',
                status TINYINT DEFAULT 1 COMMENT '状态 1-草稿 2-待审批 3-已审批 4-已作废',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库入库单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_in_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '入库单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                card_no VARCHAR(50) COMMENT '卡号',
                quantity INT NOT NULL COMMENT '数量',
                unit VARCHAR(20) DEFAULT '件' COMMENT '单位',
                FOREIGN KEY (order_id) REFERENCES stock_in_orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_out_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '出库单号',
                out_type TINYINT NOT NULL COMMENT '出库类型 1-销售出库 2-安装领料 3-维修领料 4-其他',
                source_no VARCHAR(50) COMMENT '来源单号',
                handler VARCHAR(50) COMMENT '经办人',
                warehouse VARCHAR(50) COMMENT '仓库',
                status TINYINT DEFAULT 1 COMMENT '状态 1-草稿 2-待审批 3-已审批 4-已作废',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库出库单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_out_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '出库单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                card_no VARCHAR(50) COMMENT '卡号',
                quantity INT NOT NULL COMMENT '数量',
                unit VARCHAR(20) DEFAULT '件' COMMENT '单位',
                FOREIGN KEY (order_id) REFERENCES stock_out_orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库明细'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INT PRIMARY KEY AUTO_INCREMENT,
                movement_no VARCHAR(50) UNIQUE NOT NULL COMMENT '流水单号',
                product_id INT NOT NULL COMMENT '产品ID',
                type TINYINT NOT NULL COMMENT '类型 1-入库 2-出库',
                quantity INT NOT NULL COMMENT '数量',
                before_stock INT COMMENT '变动前库存',
                after_stock INT COMMENT '变动后库存',
                source_type VARCHAR(20) COMMENT '来源类型',
                source_no VARCHAR(50) COMMENT '来源单号',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存流水表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_counts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                count_no VARCHAR(50) UNIQUE NOT NULL COMMENT '盘点单号',
                warehouse VARCHAR(50) COMMENT '仓库',
                count_date DATE NOT NULL COMMENT '盘点日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-进行中 2-已完成',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存盘点单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_count_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                count_id INT NOT NULL COMMENT '盘点单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                book_qty INT COMMENT '账面数量',
                actual_qty INT COMMENT '实际数量',
                diff_qty INT COMMENT '差异数量',
                FOREIGN KEY (count_id) REFERENCES inventory_counts(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盘点明细'
        """)

        # ============ 销售管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '销售订单号',
                customer_id INT COMMENT '客户ID',
                customer_name VARCHAR(100) COMMENT '客户名称',
                bureau_id INT COMMENT '路局ID',
                segment_id INT COMMENT '站段ID',
                station_id INT COMMENT '站点ID',
                contact VARCHAR(50) COMMENT '联系人',
                phone VARCHAR(20) COMMENT '联系电话',
                total_amount DECIMAL(12, 2) DEFAULT 0 COMMENT '总金额',
                pay_status TINYINT DEFAULT 1 COMMENT '付款状态 1-待付款 2-部分付款 3-已付清',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待处理 2-处理中 3-已完成 4-已取消',
                delivery_info VARCHAR(200) COMMENT '交付信息',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_order_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '订单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                quantity INT NOT NULL COMMENT '数量',
                unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
                total_price DECIMAL(10, 2) NOT NULL COMMENT '金额',
                FOREIGN KEY (order_id) REFERENCES sales_orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单明细'
        """)

        # ============ 安装管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installation_requisitions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                req_no VARCHAR(50) UNIQUE NOT NULL COMMENT '领料单号',
                sales_order_id INT COMMENT '销售订单ID',
                requester VARCHAR(50) NOT NULL COMMENT '领料人',
                req_date DATE NOT NULL COMMENT '领料日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待审批 2-已审批 3-已作废',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安装领料单'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installation_requisition_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                req_id INT NOT NULL COMMENT '领料单ID',
                product_id INT NOT NULL COMMENT '产品ID',
                product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                quantity INT NOT NULL COMMENT '数量',
                FOREIGN KEY (req_id) REFERENCES installation_requisitions(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安装领料明细'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installation_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                record_no VARCHAR(50) UNIQUE NOT NULL COMMENT '归档编号',
                sales_order_id INT COMMENT '销售订单ID',
                customer_id INT COMMENT '客户ID',
                customer_name VARCHAR(100) COMMENT '客户名称',
                install_location VARCHAR(200) COMMENT '安装地点',
                device_info TEXT COMMENT '设备信息',
                installer VARCHAR(50) COMMENT '安装人员',
                install_date DATE COMMENT '安装日期',
                status TINYINT DEFAULT 1 COMMENT '状态',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='安装归档记录'
        """)

        # ============ 售后管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS after_sales_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '售后工单号',
                customer_id INT COMMENT '客户ID',
                customer_name VARCHAR(100) COMMENT '客户名称',
                bureau_id INT COMMENT '路局ID',
                segment_id INT COMMENT '站段ID',
                station_id INT COMMENT '站点ID',
                contact VARCHAR(50) COMMENT '联系人',
                phone VARCHAR(20) COMMENT '联系电话',
                problem_summary VARCHAR(200) COMMENT '问题概要',
                address VARCHAR(200) COMMENT '地址',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待处理 2-处理中 3-已完成 4-已关闭',
                creator VARCHAR(50) COMMENT '创建人',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后工单表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS after_sales_order_items (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '工单ID',
                problem_desc VARCHAR(200) COMMENT '问题描述',
                status TINYINT DEFAULT 1 COMMENT '状态',
                FOREIGN KEY (order_id) REFERENCES after_sales_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后问题项'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '工单ID',
                processor VARCHAR(50) COMMENT '处理人',
                process_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '处理时间',
                process_type TINYINT COMMENT '处理类型 1-沟通 2-寄修 3-转维修 4-异常跳过 5-补充处理',
                content TEXT COMMENT '处理内容',
                result VARCHAR(100) COMMENT '处理结果',
                FOREIGN KEY (order_id) REFERENCES after_sales_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='处理记录表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS after_sales_devices (
                id INT PRIMARY KEY AUTO_INCREMENT,
                sn VARCHAR(50) COMMENT '设备SN',
                model VARCHAR(50) COMMENT '型号',
                order_id INT COMMENT '关联工单ID',
                problem VARCHAR(200) COMMENT '问题描述',
                customer_id INT COMMENT '客户ID',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待处理 2-维修中 3-待发货 4-已返还',
                handler VARCHAR(50) COMMENT '责任人',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES after_sales_orders(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后设备记录表'
        """)

        # ============ 售后缓存库表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS after_sales_cache_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '缓存单号',
                order_type TINYINT NOT NULL COMMENT '类型 1-入库 2-出库',
                source_no VARCHAR(50) COMMENT '来源单号',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待审批 2-已审批',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后缓存库单据'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS after_sales_cache_details (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '缓存单ID',
                product_id INT COMMENT '产品ID',
                product_name VARCHAR(100) COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                quantity INT NOT NULL COMMENT '数量',
                type TINYINT COMMENT '类型 1-替换件 2-维修件 3-其他',
                FOREIGN KEY (order_id) REFERENCES after_sales_cache_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后缓存库明细'
        """)

        # ============ 物流管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logistics_orders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '物流单号',
                sender VARCHAR(50) COMMENT '寄件人',
                sender_phone VARCHAR(20) COMMENT '寄件人电话',
                sender_address VARCHAR(200) COMMENT '寄件地址',
                receiver VARCHAR(50) COMMENT '收件人',
                receiver_phone VARCHAR(20) COMMENT '收件人电话',
                receiver_address VARCHAR(200) COMMENT '收件地址',
                logistics_company VARCHAR(50) COMMENT '物流公司',
                logistics_no VARCHAR(50) COMMENT '物流单号',
                fee DECIMAL(8, 2) COMMENT '费用',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待发货 2-已发货 3-运输中 4-已签收',
                order_type TINYINT COMMENT '订单类型 1-销售发货 2-售后寄修 3-返还客户',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流订单表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logistics_order_items (
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL COMMENT '物流单ID',
                product_id INT COMMENT '产品ID',
                product_name VARCHAR(100) COMMENT '产品名称',
                sn VARCHAR(50) COMMENT 'SN码',
                quantity INT DEFAULT 1 COMMENT '数量',
                FOREIGN KEY (order_id) REFERENCES logistics_orders(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流订单明细'
        """)

        # ============ 维修管理表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                record_no VARCHAR(50) UNIQUE NOT NULL COMMENT '维修记录号',
                device_sn VARCHAR(50) COMMENT '设备SN',
                fault_desc VARCHAR(200) COMMENT '故障描述',
                customer_id INT COMMENT '客户ID',
                customer_name VARCHAR(100) COMMENT '客户名称',
                source_type TINYINT COMMENT '来源 1-售后转修 2-直接报修',
                source_id INT COMMENT '来源ID',
                repairer VARCHAR(50) COMMENT '维修人员',
                repair_date DATE COMMENT '维修日期',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待维修 2-维修中 3-已完成 4-已报废',
                test_result VARCHAR(200) COMMENT '测试结果',
                remark VARCHAR(200) COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修记录表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_sub_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                repair_id INT NOT NULL COMMENT '维修记录ID',
                process_desc VARCHAR(200) COMMENT '维修过程描述',
                start_time TIMESTAMP COMMENT '开始时间',
                end_time TIMESTAMP COMMENT '结束时间',
                FOREIGN KEY (repair_id) REFERENCES repair_records(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修子记录'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_parts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                repair_id INT NOT NULL COMMENT '维修记录ID',
                part_id INT NOT NULL COMMENT '配件ID',
                part_name VARCHAR(100) COMMENT '配件名称',
                quantity INT DEFAULT 1 COMMENT '数量',
                FOREIGN KEY (repair_id) REFERENCES repair_records(id),
                FOREIGN KEY (part_id) REFERENCES parts(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修配件表'
        """)

        # ============ 设备生命周期表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_profiles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                sn VARCHAR(50) UNIQUE NOT NULL COMMENT '设备SN',
                product_id INT COMMENT '产品ID',
                product_name VARCHAR(100) COMMENT '产品名称',
                card_no VARCHAR(50) COMMENT '卡号',
                status TINYINT DEFAULT 1 COMMENT '状态 1-待入库 2-库存中 3-已销售 4-已安装 5-售后中 6-维修中 7-已报废',
                phase VARCHAR(20) COMMENT '阶段',
                location VARCHAR(100) COMMENT '位置',
                owner VARCHAR(100) COMMENT '归属',
                bureau_id INT COMMENT '所属路局',
                segment_id INT COMMENT '所属站段',
                station_id INT COMMENT '所属站点',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备档案表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_lifecycle_events (
                id INT PRIMARY KEY AUTO_INCREMENT,
                sn VARCHAR(50) NOT NULL COMMENT '设备SN',
                event_type VARCHAR(20) NOT NULL COMMENT '事件类型',
                event_desc VARCHAR(200) COMMENT '事件描述',
                operator VARCHAR(50) COMMENT '操作人',
                source_type VARCHAR(20) COMMENT '来源类型',
                source_no VARCHAR(50) COMMENT '来源单号',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备生命周期事件'
        """)

        # ============ 系统表 ============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INT PRIMARY KEY AUTO_INCREMENT,
                config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
                config_value TEXT COMMENT '配置值',
                config_desc VARCHAR(200) COMMENT '配置描述',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表'
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) COMMENT '操作人',
                user_id INT COMMENT '用户ID',
                operation VARCHAR(50) COMMENT '操作类型',
                module VARCHAR(50) COMMENT '操作模块',
                content TEXT COMMENT '操作内容',
                ip VARCHAR(50) COMMENT 'IP地址',
                result TINYINT DEFAULT 1 COMMENT '结果 1-成功 0-失败',
                reason VARCHAR(200) COMMENT '失败原因',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表'
        """)

        # 创建索引优化查询
        try:
            cursor.execute("DROP INDEX idx_products_category ON products")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_products_category ON products(category_id)")
        except:
            pass
        
        try:
            cursor.execute("DROP INDEX idx_sales_orders_customer ON sales_orders")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_sales_orders_customer ON sales_orders(customer_id)")
        except:
            pass
        
        try:
            cursor.execute("DROP INDEX idx_device_profiles_sn ON device_profiles")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_device_profiles_sn ON device_profiles(sn)")
        except:
            pass
        
        try:
            cursor.execute("DROP INDEX idx_device_lifecycle_sn ON device_lifecycle_events")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_device_lifecycle_sn ON device_lifecycle_events(sn)")
        except:
            pass

        # ============ 初始化默认角色 ============
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        if role_count == 0:
            roles_data = [
                (1, '系统管理员', '{"product": "all", "sale": "all", "production": "all", "warehouse": "all", "after_sales": "all", "logistics": "all", "maintenance": "all", "statistics": "all", "system": "all"}', 'all', 1, '系统最高权限'),
                (2, '仓库管理员', '{"warehouse": "all", "product": "read"}', 'all', 2, '仓库管理权限'),
                (3, '销售员', '{"sale": "all", "product": "read"}', 'all', 3, '销售管理权限'),
                (4, '生产主管', '{"production": "all", "product": "read"}', 'all', 4, '生产管理权限'),
                (5, '售后工程师', '{"after_sales": "all", "maintenance": "all"}', 'all', 5, '售后维修权限'),
                (6, '财务人员', '{"statistics": "read", "sale": "read", "warehouse": "read"}', 'all', 6, '财务统计权限')
            ]
            cursor.executemany("""
                INSERT INTO roles (id, name, permissions, data_scope, sort_order, remark)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, roles_data)

        # ============ 初始化默认用户 ============
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        if user_count == 0:
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, real_name, role_ids, status)
                VALUES (1, 'admin', 'admin', '系统管理员', '1', 1)
            """)

        conn.commit()
        cursor.close()
        conn.close()
        print("数据库初始化成功！")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
