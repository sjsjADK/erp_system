# 物流管理服务层
# 处理物流相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, execute_many
from datetime import datetime

class LogisticsOrderService:
    """物流订单服务类"""

    @staticmethod
    def get_all_orders():
        """获取所有物流订单"""
        sql = """
            SELECT lo.id, lo.order_no, lo.sender, lo.receiver, lo.status,
                   lo.logistics_company, lo.estimated_date, lo.logistics_no, lo.remark, lo.created_at
            FROM logistics_orders lo
            ORDER BY lo.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_order_by_id(order_id):
        """根据ID获取物流订单"""
        sql = "SELECT * FROM logistics_orders WHERE id = %s"
        results = execute_query(sql, (order_id,))
        return results[0] if results else None

    @staticmethod
    def get_order_details(order_id):
        """获取物流订单明细"""
        sql = """
            SELECT lod.id, lod.product_id, p.name as product_name, 
                   lod.quantity, lod.weight, lod.volume
            FROM logistics_order_items lod
            LEFT JOIN products p ON lod.product_id = p.id
            WHERE lod.order_id = %s
        """
        return execute_query(sql, (order_id,))

    @staticmethod
    def add_order(sender, receiver, logistics_company, estimated_date, details, 
                 logistics_no="", remark=""):
        """添加物流订单"""
        order_no = LogisticsOrderService.generate_order_no()
        
        sql = """
            INSERT INTO logistics_orders (order_no, sender, receiver, status, 
                                          logistics_company, estimated_date, logistics_no, remark)
            VALUES (%s, %s, %s, 1, %s, %s, %s, %s)
        """
        if not execute_update(sql, (order_no, sender, receiver, logistics_company, 
                                    estimated_date, logistics_no, remark)):
            return False
        
        sql = "SELECT LAST_INSERT_ID()"
        order_id = execute_query(sql)[0][0]
        
        detail_sql = """
            INSERT INTO logistics_order_items (order_id, product_id, product_name, 
                                                 quantity, weight, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = [(order_id, d['product_id'], d['product_name'], d['quantity'], 
                   d['weight'], d['volume']) for d in details]
        
        return execute_many(detail_sql, params)

    @staticmethod
    def update_order(order_id, sender, receiver, logistics_company, status, logistics_no, remark):
        """更新物流订单"""
        sql = """
            UPDATE logistics_orders 
            SET sender = %s, receiver = %s, logistics_company = %s, 
                status = %s, logistics_no = %s, remark = %s
            WHERE id = %s
        """
        return execute_update(sql, (sender, receiver, logistics_company, status, logistics_no, remark, order_id))

    @staticmethod
    def update_status(order_id, status):
        """更新订单状态"""
        sql = "UPDATE logistics_orders SET status = %s WHERE id = %s"
        return execute_update(sql, (status, order_id))

    @staticmethod
    def generate_order_no():
        """生成物流订单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM logistics_orders WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"WL{date_str}{str(count + 1).zfill(4)}"

    @staticmethod
    def get_status_text(status):
        """获取状态文本"""
        status_map = {1: '待发货', 2: '已发货', 3: '运输中', 4: '已签收', 5: '已取消'}
        return status_map.get(status, '未知')


class LogisticsTrackingService:
    """物流跟踪服务类"""

    @staticmethod
    def get_tracking_by_order(order_id):
        """获取物流跟踪记录"""
        sql = """
            SELECT lt.id, lt.tracking_time, lt.location, lt.status, lt.remark
            FROM logistics_tracking lt
            WHERE lt.order_id = %s
            ORDER BY lt.tracking_time DESC
        """
        return execute_query(sql, (order_id,))

    @staticmethod
    def add_tracking(order_id, location, status, remark=""):
        """添加跟踪记录"""
        sql = """
            INSERT INTO logistics_tracking (order_id, tracking_time, location, status, remark)
            VALUES (%s, NOW(), %s, %s, %s)
        """
        return execute_update(sql, (order_id, location, status, remark))


class LogisticsStatisticsService:
    """物流统计服务类"""

    @staticmethod
    def get_daily_statistics(date):
        """获取每日统计"""
        sql = """
            SELECT COUNT(*) as total_orders,
                   SUM(CASE WHEN status = 4 THEN 1 ELSE 0 END) as completed_orders,
                   SUM(CASE WHEN status = 5 THEN 1 ELSE 0 END) as cancelled_orders
            FROM logistics_orders
            WHERE DATE(created_at) = %s
        """
        return execute_query(sql, (date,))

    @staticmethod
    def get_logistics_company_statistics():
        """按运输方式统计"""
        sql = """
            SELECT logistics_company, COUNT(*) as count
            FROM logistics_orders
            GROUP BY logistics_company
            ORDER BY count DESC
        """
        return execute_query(sql)
