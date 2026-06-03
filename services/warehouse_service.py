# 仓库管理服务层
# 处理仓库相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, execute_many, get_connection
from datetime import datetime

class WarehouseStockInService:
    """仓库入库服务类"""

    @staticmethod
    def get_all_stock_in():
        """获取所有入库单"""
        sql = """
            SELECT si.id, si.order_no, si.in_type, si.source_no, si.handler,
                   si.warehouse, si.location, si.status, si.remark, si.created_at
            FROM stock_in_orders si
            ORDER BY si.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_stock_in_by_id(in_id):
        """根据ID获取入库单"""
        sql = "SELECT * FROM stock_in_orders WHERE id = %s"
        results = execute_query(sql, (in_id,))
        return results[0] if results else None

    @staticmethod
    def get_stock_in_details(in_id):
        """获取入库明细"""
        sql = """
            SELECT sid.id, sid.product_id, sid.product_name,
                   sid.sn, sid.card_no, sid.quantity, sid.unit
            FROM stock_in_details sid
            WHERE sid.order_id = %s
        """
        return execute_query(sql, (in_id,))

    @staticmethod
    def add_stock_in(in_type, source_no, handler, warehouse, location, details, remark=""):
        """添加入库单"""
        order_no = WarehouseStockInService.generate_in_no()
        
        conn = get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO stock_in_orders (order_no, in_type, source_no, handler, warehouse, location, status, remark)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
            """
            cursor.execute(sql, (order_no, in_type, source_no, handler, warehouse, location, remark))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            in_id = cursor.fetchone()[0]

            detail_sql = """
                INSERT INTO stock_in_details (order_id, product_id, product_name, sn, card_no, quantity, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = [(in_id, d['product_id'], d['product_name'], d.get('sn', ''),
                       d.get('card_no', ''), d['quantity'], d.get('unit', '件')) for d in details]
            
            cursor.executemany(detail_sql, params)

            for detail in details:
                sql = "UPDATE products SET stock = stock + %s WHERE id = %s"
                cursor.execute(sql, (detail['quantity'], detail['product_id']))

            conn.commit()
            cursor.close()
            conn.close()

            for detail in details:
                WarehouseStockFlowService.add_flow(1, detail['product_id'], detail['product_name'],
                                                  detail['quantity'], '入库', order_no)

            return True
            
        except Exception as e:
            print(f"添加入库单失败: {e}")
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def generate_in_no():
        """生成入库单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM stock_in_orders WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"RK{date_str}{str(count + 1).zfill(4)}"

    @staticmethod
    def delete_stock_in(in_id):
        """删除入库单"""
        in_info = WarehouseStockInService.get_stock_in_by_id(in_id)
        if not in_info:
            return False

        if in_info[8] != 1:
            return False

        details = WarehouseStockInService.get_stock_in_details(in_id)

        for detail in details:
            sql = "UPDATE products SET stock = stock - %s WHERE id = %s"
            if not execute_update(sql, (detail[5], detail[1])):
                return False

        sql = "DELETE FROM stock_in_details WHERE order_id = %s"
        if not execute_update(sql, (in_id,)):
            return False

        sql = "DELETE FROM stock_in_orders WHERE id = %s"
        return execute_update(sql, (in_id,))


class WarehouseStockOutService:
    """仓库出库服务类"""

    @staticmethod
    def get_all_stock_out():
        """获取所有出库单"""
        sql = """
            SELECT so.id, so.order_no, so.out_type, so.source_no, so.handler,
                   so.warehouse, so.status, so.remark, so.created_at
            FROM stock_out_orders so
            ORDER BY so.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_stock_out_by_id(out_id):
        """根据ID获取出库单"""
        sql = "SELECT * FROM stock_out_orders WHERE id = %s"
        results = execute_query(sql, (out_id,))
        return results[0] if results else None

    @staticmethod
    def get_stock_out_details(out_id):
        """获取出库明细"""
        sql = """
            SELECT sod.id, sod.product_id, sod.product_name,
                   sod.sn, sod.card_no, sod.quantity, sod.unit
            FROM stock_out_details sod
            WHERE sod.order_id = %s
        """
        return execute_query(sql, (out_id,))

    @staticmethod
    def add_stock_out(out_type, source_no, handler, warehouse, details, remark=""):
        """添加出库单"""
        for detail in details:
            sql = "SELECT stock FROM products WHERE id = %s"
            results = execute_query(sql, (detail['product_id'],))
            if not results or results[0][0] < detail['quantity']:
                return False

        order_no = WarehouseStockOutService.generate_out_no()
        
        conn = get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO stock_out_orders (order_no, out_type, source_no, handler, warehouse, status, remark)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
            """
            cursor.execute(sql, (order_no, out_type, source_no, handler, warehouse, remark))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            out_id = cursor.fetchone()[0]

            detail_sql = """
                INSERT INTO stock_out_details (order_id, product_id, product_name, sn, card_no, quantity, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = [(out_id, d['product_id'], d['product_name'], d.get('sn', ''),
                       d.get('card_no', ''), d['quantity'], d.get('unit', '件')) for d in details]
            
            cursor.executemany(detail_sql, params)

            for detail in details:
                sql = "UPDATE products SET stock = stock - %s WHERE id = %s"
                cursor.execute(sql, (detail['quantity'], detail['product_id']))

            conn.commit()
            cursor.close()
            conn.close()

            type_map = {1: '销售出库', 2: '安装领料', 3: '维修领料', 4: '其他出库'}
            type_name = type_map.get(out_type, '出库')
            for detail in details:
                WarehouseStockFlowService.add_flow(2, detail['product_id'], detail['product_name'],
                                                  detail['quantity'], type_name, order_no)

            return True
            
        except Exception as e:
            print(f"添加出库单失败: {e}")
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def generate_out_no():
        """生成出库单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM stock_out_orders WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"CK{date_str}{str(count + 1).zfill(4)}"


class WarehouseStockFlowService:
    """库存流水服务类"""

    @staticmethod
    def get_all_flows():
        """获取所有库存流水"""
        sql = """
            SELECT sm.id, sm.type, sm.product_id, p.name as product_name,
                   sm.quantity, sm.before_stock, sm.after_stock,
                   sm.source_type, sm.source_no, sm.created_at
            FROM stock_movements sm
            LEFT JOIN products p ON sm.product_id = p.id
            ORDER BY sm.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def add_flow(flow_type, product_id, product_name, quantity, reason, source_no=""):
        """添加库存流水"""
        sql = "SELECT stock FROM products WHERE id = %s"
        results = execute_query(sql, (product_id,))
        before_stock = results[0][0] if results else 0
        after_stock = before_stock + quantity if flow_type == 1 else before_stock - quantity

        movement_no = WarehouseStockFlowService.generate_movement_no()

        sql = """
            INSERT INTO stock_movements (movement_no, product_id, type, quantity,
                                         before_stock, after_stock, source_type, source_no)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_update(sql, (movement_no, product_id, flow_type, quantity,
                                    before_stock, after_stock, reason, source_no))

    @staticmethod
    def generate_movement_no():
        """生成流水单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d%H%M%S")
        return f"LD{date_str}"


class WarehouseInventoryService:
    """库存盘点服务类"""

    @staticmethod
    def get_all_inventories():
        """获取所有盘点记录"""
        sql = """
            SELECT ic.id, ic.count_no, ic.warehouse, ic.count_date, ic.status,
                   ic.remark, ic.created_at
            FROM inventory_counts ic
            ORDER BY ic.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_inventory_by_id(inventory_id):
        """根据ID获取盘点记录"""
        sql = "SELECT * FROM inventory_counts WHERE id = %s"
        results = execute_query(sql, (inventory_id,))
        return results[0] if results else None

    @staticmethod
    def get_inventory_details(inventory_id):
        """获取盘点明细"""
        sql = "SELECT * FROM inventory_count_details WHERE count_id = %s"
        return execute_query(sql, (inventory_id,))

    @staticmethod
    def add_inventory(warehouse, count_date, details, remark=""):
        """添加盘点记录"""
        count_no = WarehouseInventoryService.generate_inventory_no()
        
        conn = get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO inventory_counts (count_no, warehouse, count_date, status, remark)
                VALUES (%s, %s, %s, 1, %s)
            """
            cursor.execute(sql, (count_no, warehouse, count_date, remark))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            inventory_id = cursor.fetchone()[0]

            detail_sql = """
                INSERT INTO inventory_count_details (count_id, product_id, product_name,
                                                    book_qty, actual_qty, diff_qty)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = [(inventory_id, d['product_id'], d['product_name'], d['system_qty'],
                       d['actual_qty'], d['diff_qty']) for d in details]
            
            cursor.executemany(detail_sql, params)

            conn.commit()
            cursor.close()
            conn.close()

            return True
            
        except Exception as e:
            print(f"添加盘点记录失败: {e}")
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def approve_inventory(inventory_id):
        """审批盘点并调整库存"""
        details = WarehouseInventoryService.get_inventory_details(inventory_id)
        for detail in details:
            product_id = detail[1]
            diff_qty = detail[5]

            if diff_qty != 0:
                sql = "UPDATE products SET stock = stock + %s WHERE id = %s"
                if not execute_update(sql, (diff_qty, product_id)):
                    return False

                reason = '盘盈' if diff_qty > 0 else '盘亏'
                WarehouseStockFlowService.add_flow(3 if diff_qty > 0 else 4, product_id,
                                                  detail[2], abs(diff_qty), reason, '')

        sql = "UPDATE inventory_counts SET status = 2 WHERE id = %s"
        return execute_update(sql, (inventory_id,))

    @staticmethod
    def generate_inventory_no():
        """生成盘点单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM inventory_counts WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"PD{date_str}{str(count + 1).zfill(4)}"


class InventoryQueryService:
    """库存查询服务类"""

    @staticmethod
    def get_all_inventory():
        """获取当前库存"""
        sql = """
            SELECT p.id, p.product_code, p.name, p.model, pc.name as category_name,
                   p.spec, p.stock, p.unit, p.price, p.supplier
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            ORDER BY p.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_low_stock_products(threshold=10):
        """获取低库存产品"""
        sql = """
            SELECT p.id, p.product_code, p.name, p.model, p.stock, p.unit, p.price
            FROM products p
            WHERE p.stock <= %s
            ORDER BY p.stock ASC
        """
        return execute_query(sql, (threshold,))

    @staticmethod
    def get_inventory_by_product(product_id):
        """获取指定产品的库存记录"""
        sql = """
            SELECT sm.id, sm.type, sm.quantity, sm.before_stock, sm.after_stock,
                   sm.source_type, sm.source_no, sm.created_at
            FROM stock_movements sm
            WHERE sm.product_id = %s
            ORDER BY sm.created_at DESC
        """
        return execute_query(sql, (product_id,))

    @staticmethod
    def get_stock_value():
        """获取库存总价值"""
        sql = "SELECT COALESCE(SUM(stock * price), 0) FROM products"
        results = execute_query(sql)
        return results[0][0] if results else 0