# 销售服务层
# 处理销售的相关业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, get_connection
from datetime import datetime

class SaleService:
    """销售服务类"""

    @staticmethod
    def get_all_sales():
        """获取所有销售记录"""
        sql = """
            SELECT id, order_no, customer_id, customer_name, 
                   total_amount, pay_status, status, delivery_info, 
                   DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at, remark
            FROM sales_orders
            ORDER BY created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def search_sales(keyword):
        """搜索销售记录"""
        sql = """
            SELECT id, order_no, customer_id, customer_name, 
                   total_amount, pay_status, status, delivery_info, 
                   DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at, remark
            FROM sales_orders
            WHERE customer_name LIKE %s OR order_no LIKE %s OR contact LIKE %s
            ORDER BY created_at DESC
        """
        keyword = f"%{keyword}%"
        return execute_query(sql, (keyword, keyword, keyword))

    @staticmethod
    def add_sale(product_id, product_name, quantity, unit_price, customer="", remark=""):
        """添加销售记录"""
        total_price = quantity * unit_price
        order_no = SaleService.generate_order_no()
        
        conn = get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 添加销售订单主表
            sql = """
                INSERT INTO sales_orders (order_no, customer_name, total_amount, status, remark)
                VALUES (%s, %s, %s, 1, %s)
            """
            cursor.execute(sql, (order_no, customer, total_price, remark))
            
            # 获取订单ID（使用同一个连接）
            cursor.execute("SELECT LAST_INSERT_ID()")
            order_id = cursor.fetchone()[0]
            
            # 添加销售订单明细
            detail_sql = """
                INSERT INTO sales_order_details (order_id, product_id, product_name, 
                                               quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(detail_sql, (order_id, product_id, product_name, quantity, unit_price, total_price))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # 减少库存
            from services.product_service import ProductService
            return ProductService.update_stock(product_id, -quantity)
            
        except Exception as e:
            print(f"添加销售失败: {e}")
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def delete_sale(sale_id):
        """删除销售记录"""
        conn = get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 先查询销售明细
            sql = "SELECT product_id, quantity FROM sales_order_details WHERE order_id = %s"
            cursor.execute(sql, (sale_id,))
            details = cursor.fetchall()
            
            # 删除明细
            sql = "DELETE FROM sales_order_details WHERE order_id = %s"
            cursor.execute(sql, (sale_id,))
            
            # 删除订单主表
            sql = "DELETE FROM sales_orders WHERE id = %s"
            cursor.execute(sql, (sale_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # 恢复库存
            from services.product_service import ProductService
            for detail in details:
                product_id, quantity = detail
                ProductService.update_stock(product_id, quantity)
            
            return True
            
        except Exception as e:
            print(f"删除销售失败: {e}")
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def get_sale_count():
        """获取销售记录总数"""
        sql = "SELECT COUNT(*) FROM sales_orders"
        results = execute_query(sql)
        return results[0][0] if results else 0

    @staticmethod
    def get_sales_by_date(start_date, end_date):
        """按日期范围查询销售记录"""
        sql = """
            SELECT id, order_no, customer_id, customer_name, 
                   total_amount, pay_status, status, delivery_info, 
                   DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at, remark
            FROM sales_orders
            WHERE DATE(created_at) BETWEEN %s AND %s
            ORDER BY created_at DESC
        """
        return execute_query(sql, (start_date, end_date))

    @staticmethod
    def get_sale_by_id(sale_id):
        """根据ID查询销售记录"""
        sql = """
            SELECT id, order_no, customer_id, customer_name, 
                   total_amount, pay_status, status, delivery_info, 
                   DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at, remark
            FROM sales_orders
            WHERE id = %s
        """
        results = execute_query(sql, (sale_id,))
        return results[0] if results else None

    @staticmethod
    def generate_order_no():
        """生成销售单号：日期+流水号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        
        # 查询今日的最大流水号
        sql = """
            SELECT MAX(SUBSTRING(order_no, 7, 4)) 
            FROM sales_orders 
            WHERE order_no LIKE CONCAT('XSD', %s, '%%')
        """
        result = execute_query(sql, (date_str,))
        count = int(result[0][0]) if result[0][0] else 0
        
        return f"XSD{date_str}{str(count + 1).zfill(4)}"