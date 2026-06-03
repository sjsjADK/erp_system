# 维修管理服务层
# 处理维修相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, execute_many
from datetime import datetime

class MaintenanceRecordService:
    """维修记录服务类"""

    @staticmethod
    def get_all_records():
        """获取所有维修记录"""
        sql = """
            SELECT mr.id, mr.record_no, mr.device_sn, p.name as product_name,
                   mr.fault_desc, mr.priority, mr.status, mr.report_time, 
                   mr.assignee, mr.repair_cost, mr.remark, mr.created_at
            FROM maintenance_records mr
            LEFT JOIN products p ON mr.product_id = p.id
            ORDER BY mr.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_record_by_id(record_id):
        """根据ID获取维修记录"""
        sql = "SELECT * FROM maintenance_records WHERE id = %s"
        results = execute_query(sql, (record_id,))
        return results[0] if results else None

    @staticmethod
    def add_record(device_sn, product_id, fault_desc, priority=2, report_time=None, 
                   assignee="", remark=""):
        """添加维修记录"""
        record_no = MaintenanceRecordService.generate_record_no()
        if report_time is None:
            report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        sql = """
            INSERT INTO maintenance_records (record_no, device_sn, product_id, fault_desc, 
                                             priority, status, report_time, assignee, remark)
            VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s)
        """
        return execute_update(sql, (record_no, device_sn, product_id, fault_desc, 
                                    priority, report_time, assignee, remark))

    @staticmethod
    def update_record(record_id, fault_desc, status, priority, assignee, repair_cost, remark):
        """更新维修记录"""
        sql = """
            UPDATE maintenance_records 
            SET fault_desc = %s, status = %s, priority = %s, 
                assignee = %s, repair_cost = %s, remark = %s
            WHERE id = %s
        """
        return execute_update(sql, (fault_desc, status, priority, assignee, repair_cost, remark, record_id))

    @staticmethod
    def update_status(record_id, status):
        """更新状态"""
        sql = "UPDATE maintenance_records SET status = %s WHERE id = %s"
        return execute_update(sql, (status, record_id))

    @staticmethod
    def generate_record_no():
        """生成维修单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM maintenance_records WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"WX{date_str}{str(count + 1).zfill(4)}"

    @staticmethod
    def get_status_text(status):
        """获取状态文本"""
        status_map = {1: '待维修', 2: '维修中', 3: '已完成', 4: '已取消'}
        return status_map.get(status, '未知')

    @staticmethod
    def get_priority_text(priority):
        """获取优先级文本"""
        priority_map = {1: '紧急', 2: '一般', 3: '低'}
        return priority_map.get(priority, '未知')


class MaintenanceSubRecordService:
    """维修子记录服务类"""

    @staticmethod
    def get_sub_records_by_main(main_record_id):
        """根据主记录ID获取子记录"""
        sql = """
            SELECT msr.id, msr.sub_record_no, msr.repair_content, 
                   msr.repair_time, msr.operator, msr.status
            FROM maintenance_sub_records msr
            WHERE msr.main_record_id = %s
            ORDER BY msr.repair_time DESC
        """
        return execute_query(sql, (main_record_id,))

    @staticmethod
    def add_sub_record(main_record_id, repair_content, repair_time=None, operator="", status=1):
        """添加维修子记录"""
        sub_no = MaintenanceSubRecordService.generate_sub_no()
        if repair_time is None:
            repair_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        sql = """
            INSERT INTO maintenance_sub_records (sub_record_no, main_record_id, 
                                                 repair_content, repair_time, operator, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_update(sql, (sub_no, main_record_id, repair_content, repair_time, operator, status))

    @staticmethod
    def generate_sub_no():
        """生成子记录号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM maintenance_sub_records WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"WX{date_str}S{str(count + 1).zfill(3)}"


class MaintenancePartsService:
    """维修配件服务类"""

    @staticmethod
    def get_parts_by_record(record_id):
        """根据维修记录ID获取配件"""
        sql = """
            SELECT mp.id, mp.part_id, p.name as part_name, mp.quantity, 
                   mp.price, mp.amount, mp.remark
            FROM maintenance_parts mp
            LEFT JOIN parts p ON mp.part_id = p.id
            WHERE mp.record_id = %s
        """
        return execute_query(sql, (record_id,))

    @staticmethod
    def add_parts(record_id, parts):
        """添加配件"""
        sql = """
            INSERT INTO maintenance_parts (record_id, part_id, part_name, quantity, price, amount, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = [(record_id, p['part_id'], p['part_name'], p['quantity'], 
                   p['price'], p['amount'], p['remark']) for p in parts]
        return execute_many(sql, params)


class MaintenanceStatisticsService:
    """维修统计服务类"""

    @staticmethod
    def get_monthly_statistics(year, month):
        """获取月度统计"""
        sql = """
            SELECT COUNT(*) as total_repairs,
                   SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as completed_repairs,
                   AVG(repair_cost) as avg_cost,
                   SUM(repair_cost) as total_cost
            FROM maintenance_records
            WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s
        """
        return execute_query(sql, (year, month))

    @staticmethod
    def get_fault_type_statistics():
        """按故障类型统计"""
        sql = """
            SELECT LEFT(fault_desc, 10) as fault_type, COUNT(*) as count
            FROM maintenance_records
            GROUP BY LEFT(fault_desc, 10)
            ORDER BY count DESC
            LIMIT 10
        """
        return execute_query(sql)
