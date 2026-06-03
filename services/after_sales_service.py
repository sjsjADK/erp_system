# 售后管理服务层
# 处理售后相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, execute_many
from datetime import datetime

class AfterSalesWorkOrderService:
    """售后工单服务类"""

    @staticmethod
    def get_all_work_orders():
        """获取所有售后工单"""
        sql = """
            SELECT aswo.id, aswo.order_no, c.name as customer_name, 
                   d.sn as device_sn, p.name as product_name, aswo.problem_type,
                   aswo.status, aswo.priority, aswo.report_time, aswo.assignee, aswo.remark
            FROM after_sales_orders aswo
            LEFT JOIN customers c ON aswo.customer_id = c.id
            LEFT JOIN device_profiles d ON aswo.device_id = d.id
            LEFT JOIN products p ON aswo.product_id = p.id
            ORDER BY aswo.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_work_order_by_id(order_id):
        """根据ID获取工单"""
        sql = """
            SELECT aswo.*, c.name as customer_name, d.sn as device_sn, p.name as product_name
            FROM after_sales_orders aswo
            LEFT JOIN customers c ON aswo.customer_id = c.id
            LEFT JOIN device_profiles d ON aswo.device_id = d.id
            LEFT JOIN products p ON aswo.product_id = p.id
            WHERE aswo.id = %s
        """
        results = execute_query(sql, (order_id,))
        return results[0] if results else None

    @staticmethod
    def add_work_order(customer_id, device_id, product_id, problem_type, 
                      report_time, priority=2, assignee="", remark=""):
        """添加售后工单"""
        order_no = AfterSalesWorkOrderService.generate_order_no()
        sql = """
            INSERT INTO after_sales_orders (order_no, customer_id, device_id, product_id, 
                                                 problem_type, status, priority, 
                                                 report_time, assignee, remark)
            VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s, %s)
        """
        return execute_update(sql, (order_no, customer_id, device_id, product_id, 
                                    problem_type, priority, report_time, assignee, remark))

    @staticmethod
    def update_work_order(order_id, customer_id, device_id, product_id, problem_type, 
                         status, priority, assignee, remark):
        """更新售后工单"""
        sql = """
            UPDATE after_sales_orders 
            SET customer_id = %s, device_id = %s, product_id = %s, problem_type = %s,
                status = %s, priority = %s, assignee = %s, remark = %s
            WHERE id = %s
        """
        return execute_update(sql, (customer_id, device_id, product_id, problem_type, 
                                    status, priority, assignee, remark, order_id))

    @staticmethod
    def update_status(order_id, status):
        """更新工单状态"""
        sql = "UPDATE after_sales_orders SET status = %s WHERE id = %s"
        return execute_update(sql, (status, order_id))

    @staticmethod
    def generate_order_no():
        """生成工单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM after_sales_orders WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"SH{date_str}{str(count + 1).zfill(4)}"

    @staticmethod
    def get_status_text(status):
        """获取状态文本"""
        status_map = {1: '待处理', 2: '处理中', 3: '已完成', 4: '已关闭'}
        return status_map.get(status, '未知')

    @staticmethod
    def get_priority_text(priority):
        """获取优先级文本"""
        priority_map = {1: '紧急', 2: '一般', 3: '低'}
        return priority_map.get(priority, '未知')


class ProblemItemService:
    """问题项服务类"""

    @staticmethod
    def get_problem_items_by_order(order_id):
        """根据工单ID获取问题项"""
        sql = """
            SELECT pi.id, pi.problem_desc, pi.problem_code, pi.status, pi.solution
            FROM problem_items pi
            WHERE pi.work_order_id = %s
        """
        return execute_query(sql, (order_id,))

    @staticmethod
    def add_problem_item(work_order_id, problem_desc, problem_code="", solution=""):
        """添加问题项"""
        sql = """
            INSERT INTO problem_items (work_order_id, problem_desc, problem_code, status, solution)
            VALUES (%s, %s, %s, 1, %s)
        """
        return execute_update(sql, (work_order_id, problem_desc, problem_code, solution))

    @staticmethod
    def update_problem_item(item_id, problem_desc, problem_code, status, solution):
        """更新问题项"""
        sql = """
            UPDATE problem_items 
            SET problem_desc = %s, problem_code = %s, status = %s, solution = %s
            WHERE id = %s
        """
        return execute_update(sql, (problem_desc, problem_code, status, solution, item_id))


class ProcessingRecordService:
    """处理记录服务类"""

    @staticmethod
    def get_records_by_order(order_id):
        """根据工单ID获取处理记录"""
        sql = """
            SELECT pr.id, pr.process_time, pr.process_content, pr.operator, pr.next_action
            FROM processing_records pr
            WHERE pr.work_order_id = %s
            ORDER BY pr.process_time DESC
        """
        return execute_query(sql, (order_id,))

    @staticmethod
    def add_record(work_order_id, process_content, operator="", next_action=""):
        """添加处理记录"""
        sql = """
            INSERT INTO processing_records (work_order_id, process_time, process_content, operator, next_action)
            VALUES (%s, NOW(), %s, %s, %s)
        """
        return execute_update(sql, (work_order_id, process_content, operator, next_action))


class AfterSalesDeviceService:
    """售后设备服务类"""

    @staticmethod
    def get_all_devices():
        """获取所有售后设备"""
        sql = """
            SELECT asd.id, asd.sn, p.name as product_name, asd.status, 
                   asd.location, asd.install_date, asd.last_maintain_date, asd.remark
            FROM after_sales_devices asd
            LEFT JOIN products p ON asd.product_id = p.id
            ORDER BY asd.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def add_device(sn, product_id, product_name, status=1, location="", 
                   install_date="", last_maintain_date="", remark=""):
        """添加售后设备"""
        sql = """
            INSERT INTO after_sales_devices (sn, product_id, product_name, status, 
                                              location, install_date, last_maintain_date, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_update(sql, (sn, product_id, product_name, status, 
                                    location, install_date, last_maintain_date, remark))

    @staticmethod
    def update_device(device_id, status, location, last_maintain_date, remark):
        """更新售后设备"""
        sql = """
            UPDATE after_sales_devices 
            SET status = %s, location = %s, last_maintain_date = %s, remark = %s
            WHERE id = %s
        """
        return execute_update(sql, (status, location, last_maintain_date, remark, device_id))

    @staticmethod
    def delete_device(device_id):
        """删除售后设备"""
        sql = "DELETE FROM after_sales_devices WHERE id = %s"
        return execute_update(sql, (device_id,))
