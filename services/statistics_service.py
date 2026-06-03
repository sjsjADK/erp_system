# 数据统计服务层
# 处理各业务模块的统计逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query
from datetime import datetime, timedelta

class SalesStatisticsService:
    """销售统计服务类"""

    @staticmethod
    def get_daily_sales(date):
        """获取每日销售统计"""
        sql = """
            SELECT COUNT(*) as total_orders, 
                   SUM(total_amount) as total_amount,
                   SUM(so.quantity) as total_quantity
            FROM sales_orders so
            LEFT JOIN sales_order_details sod ON so.id = sod.order_id
            WHERE DATE(so.created_at) = %s
        """
        return execute_query(sql, (date,))

    @staticmethod
    def get_monthly_sales(year, month):
        """获取月度销售统计"""
        sql = """
            SELECT COUNT(*) as total_orders,
                   SUM(total_amount) as total_amount,
                   SUM(so.quantity) as total_quantity
            FROM sales_orders so
            LEFT JOIN sales_order_details sod ON so.id = sod.order_id
            WHERE YEAR(so.created_at) = %s AND MONTH(so.created_at) = %s
        """
        return execute_query(sql, (year, month))

    @staticmethod
    def get_sales_by_product(top_n=10):
        """获取销量排行"""
        sql = """
            SELECT sod.product_name, SUM(sod.quantity) as total_qty, SUM(sod.total_price) as total_amount
            FROM sales_order_details sod
            LEFT JOIN sales_orders so ON sod.order_id = so.id
            GROUP BY sod.product_name
            ORDER BY total_qty DESC
            LIMIT %s
        """
        return execute_query(sql, (top_n,))

    @staticmethod
    def get_sales_trend(days=7):
        """获取销售趋势（近N天）"""
        sql = f"""
            SELECT DATE(so.created_at) as date, 
                   COUNT(DISTINCT so.id) as orders, 
                   SUM(sod.total_price) as amount
            FROM sales_orders so
            LEFT JOIN sales_order_details sod ON so.id = sod.order_id
            WHERE so.created_at >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
            GROUP BY DATE(so.created_at)
            ORDER BY date
        """
        return execute_query(sql)


class InventoryStatisticsService:
    """库存统计服务类"""

    @staticmethod
    def get_inventory_summary():
        """获取库存汇总"""
        sql = """
            SELECT COUNT(*) as product_count,
                   SUM(stock) as total_stock,
                   SUM(stock * price) as total_value,
                   SUM(CASE WHEN stock <= 10 THEN 1 ELSE 0 END) as low_stock_count
            FROM products
            WHERE status = 1
        """
        return execute_query(sql)

    @staticmethod
    def get_inventory_by_category():
        """按分类统计库存"""
        sql = """
            SELECT pc.name as category, 
                   COUNT(p.id) as product_count, 
                   SUM(p.stock) as total_stock,
                   SUM(p.stock * p.price) as total_value
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            WHERE p.status = 1
            GROUP BY pc.name
            ORDER BY total_stock DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_low_stock_products(threshold=10):
        """获取低库存产品"""
        sql = """
            SELECT p.product_code, p.name, p.stock, p.unit, p.price
            FROM products p
            WHERE p.stock <= %s AND p.status = 1
            ORDER BY p.stock ASC
        """
        return execute_query(sql, (threshold,))


class ProductionStatisticsService:
    """生产统计服务类"""

    @staticmethod
    def get_monthly_production(year, month):
        """获取月度生产统计"""
        sql = """
            SELECT COUNT(*) as total_orders,
                   SUM(plan_qty) as plan_qty,
                   SUM(actual_qty) as actual_qty,
                   SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as completed_orders
            FROM production_orders
            WHERE YEAR(plan_date) = %s AND MONTH(plan_date) = %s
        """
        return execute_query(sql, (year, month))

    @staticmethod
    def get_scrap_rate():
        """获取报废率"""
        sql = """
            SELECT 
                (SELECT COALESCE(SUM(quantity), 0) FROM production_scrap_records) as total_scrap,
                (SELECT COALESCE(SUM(actual_qty), 0) FROM production_orders WHERE status = 3) as total_produced
        """
        return execute_query(sql)


class AfterSalesStatisticsService:
    """售后统计服务类"""

    @staticmethod
    def get_monthly_after_sales(year, month):
        """获取月度售后统计"""
        sql = """
            SELECT COUNT(*) as total_orders,
                   SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as completed_orders,
                   SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as processing_count
            FROM after_sales_orders
            WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s
        """
        return execute_query(sql, (year, month))


class SystemStatisticsService:
    """系统统计服务类"""

    @staticmethod
    def get_user_count():
        """获取用户数量"""
        sql = "SELECT COUNT(*) FROM users"
        result = execute_query(sql)
        return result[0][0] if result else 0

    @staticmethod
    def get_order_summary():
        """获取订单汇总"""
        sql = """
            SELECT 
                (SELECT COUNT(*) FROM sales) as sales_count,
                (SELECT COUNT(*) FROM production_orders) as production_count,
                (SELECT COUNT(*) FROM after_sales_work_orders) as after_sales_count,
                (SELECT COUNT(*) FROM logistics_orders) as logistics_count
        """
        return execute_query(sql)
