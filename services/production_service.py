# 生产管理服务层
# 处理生产相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update, execute_many
from datetime import datetime

class ProductionOrderService:
    """生产订单服务类"""

    @staticmethod
    def get_all_orders():
        """获取所有生产订单"""
        sql = """
            SELECT po.id, po.order_no, p.name as product_name, po.plan_qty, 
                   po.actual_qty, po.plan_date, po.status, po.responsible, po.remark, po.created_at
            FROM production_orders po
            LEFT JOIN products p ON po.product_id = p.id
            ORDER BY po.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_order_by_id(order_id):
        """根据ID获取生产订单"""
        sql = """
            SELECT po.id, po.order_no, po.product_id, p.name as product_name, 
                   po.plan_qty, po.actual_qty, po.plan_date, po.status, po.responsible, po.remark
            FROM production_orders po
            LEFT JOIN products p ON po.product_id = p.id
            WHERE po.id = %s
        """
        results = execute_query(sql, (order_id,))
        return results[0] if results else None

    @staticmethod
    def add_order(product_id, plan_qty, plan_date, responsible="", remark=""):
        """添加生产订单"""
        order_no = ProductionOrderService.generate_order_no()
        sql = """
            INSERT INTO production_orders (order_no, product_id, plan_qty, plan_date, 
                                          status, responsible, remark)
            VALUES (%s, %s, %s, %s, 1, %s, %s)
        """
        return execute_update(sql, (order_no, product_id, plan_qty, plan_date, responsible, remark))

    @staticmethod
    def update_order(order_id, product_id, plan_qty, plan_date, status, responsible, remark):
        """更新生产订单"""
        sql = """
            UPDATE production_orders 
            SET product_id = %s, plan_qty = %s, plan_date = %s, 
                status = %s, responsible = %s, remark = %s
            WHERE id = %s
        """
        return execute_update(sql, (product_id, plan_qty, plan_date, status, responsible, remark, order_id))

    @staticmethod
    def delete_order(order_id):
        """删除生产订单"""
        sql = "DELETE FROM production_orders WHERE id = %s"
        return execute_update(sql, (order_id,))

    @staticmethod
    def update_status(order_id, status):
        """更新订单状态"""
        sql = "UPDATE production_orders SET status = %s WHERE id = %s"
        return execute_update(sql, (status, order_id))

    @staticmethod
    def generate_order_no():
        """生成生产订单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM production_orders WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"SC{date_str}{str(count + 1).zfill(4)}"

    @staticmethod
    def get_status_text(status):
        """获取状态文本"""
        status_map = {1: '待生产', 2: '生产中', 3: '已完成', 4: '已取消'}
        return status_map.get(status, '未知')


class MaterialRequisitionService:
    """生产领料服务类"""

    @staticmethod
    def get_all_requisitions():
        """获取所有领料单"""
        sql = """
            SELECT mr.id, mr.req_no, po.order_no as production_order, 
                   mr.requester, mr.req_date, mr.status, mr.remark
            FROM material_requisitions mr
            LEFT JOIN production_orders po ON mr.production_order_id = po.id
            ORDER BY mr.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_requisition_by_id(req_id):
        """根据ID获取领料单"""
        sql = "SELECT * FROM material_requisitions WHERE id = %s"
        results = execute_query(sql, (req_id,))
        return results[0] if results else None

    @staticmethod
    def get_requisition_details(req_id):
        """获取领料明细"""
        sql = """
            SELECT mrd.id, mrd.part_id, p.name as part_name, mrd.quantity, mrd.unit
            FROM material_requisition_details mrd
            LEFT JOIN parts p ON mrd.part_id = p.id
            WHERE mrd.req_id = %s
        """
        return execute_query(sql, (req_id,))

    @staticmethod
    def add_requisition(production_order_id, requester, req_date, details, remark=""):
        """添加领料单"""
        req_no = MaterialRequisitionService.generate_req_no()
        
        sql = """
            INSERT INTO material_requisitions (req_no, production_order_id, requester, 
                                              req_date, status, remark)
            VALUES (%s, %s, %s, %s, 1, %s)
        """
        if not execute_update(sql, (req_no, production_order_id, requester, req_date, remark)):
            return False
        
        # 获取新插入的ID
        sql = "SELECT LAST_INSERT_ID()"
        req_id = execute_query(sql)[0][0]
        
        # 插入明细
        detail_sql = """
            INSERT INTO material_requisition_details (req_id, part_id, part_name, quantity, unit)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = [(req_id, d['part_id'], d['part_name'], d['quantity'], d['unit']) for d in details]
        return execute_many(detail_sql, params)

    @staticmethod
    def approve_requisition(req_id):
        """审批领料单"""
        # 扣减零部件库存
        details = MaterialRequisitionService.get_requisition_details(req_id)
        for detail in details:
            part_id = detail[1]
            quantity = detail[3]
            sql = "UPDATE parts SET stock = stock - %s WHERE id = %s"
            if not execute_update(sql, (quantity, part_id)):
                return False
        
        # 更新状态
        sql = "UPDATE material_requisitions SET status = 2 WHERE id = %s"
        return execute_update(sql, (req_id,))

    @staticmethod
    def generate_req_no():
        """生成领料单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM material_requisitions WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"LL{date_str}{str(count + 1).zfill(4)}"


class ProductionStockInService:
    """生产入库服务类"""

    @staticmethod
    def get_all_stock_in():
        """获取所有入库单"""
        sql = """
            SELECT psi.id, psi.in_no, po.order_no as production_order, 
                   psi.in_date, psi.status, psi.remark, psi.created_at
            FROM production_stock_in psi
            LEFT JOIN production_orders po ON psi.production_order_id = po.id
            ORDER BY psi.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def get_stock_in_by_id(in_id):
        """根据ID获取入库单"""
        sql = "SELECT * FROM production_stock_in WHERE id = %s"
        results = execute_query(sql, (in_id,))
        return results[0] if results else None

    @staticmethod
    def get_stock_in_details(in_id):
        """获取入库明细"""
        sql = """
            SELECT psid.id, psid.product_id, p.name as product_name, 
                   psid.sn, psid.card_no, psid.quantity
            FROM production_stock_in_details psid
            LEFT JOIN products p ON psid.product_id = p.id
            WHERE psid.in_id = %s
        """
        return execute_query(sql, (in_id,))

    @staticmethod
    def add_stock_in(production_order_id, in_date, details, remark=""):
        """添加入库单"""
        in_no = ProductionStockInService.generate_in_no()
        
        sql = """
            INSERT INTO production_stock_in (in_no, production_order_id, in_date, status, remark)
            VALUES (%s, %s, %s, 1, %s)
        """
        if not execute_update(sql, (in_no, production_order_id, in_date, remark)):
            return False
        
        sql = "SELECT LAST_INSERT_ID()"
        in_id = execute_query(sql)[0][0]
        
        detail_sql = """
            INSERT INTO production_stock_in_details (in_id, product_id, product_name, sn, card_no, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = [(in_id, d['product_id'], d['product_name'], d['sn'], d['card_no'], d['quantity']) for d in details]
        return execute_many(detail_sql, params)

    @staticmethod
    def approve_stock_in(in_id):
        """审批入库单"""
        # 更新库存和设备档案
        details = ProductionStockInService.get_stock_in_details(in_id)
        for detail in details:
            product_id = detail[1]
            quantity = detail[5]
            sn = detail[3]
            card_no = detail[4]
            
            # 更新产品库存
            sql = "UPDATE products SET stock = stock + %s WHERE id = %s"
            if not execute_update(sql, (quantity, product_id)):
                return False
            
            # 创建设备档案
            if sn:
                sql = """
                    INSERT INTO device_profiles (sn, product_id, product_name, card_no, status)
                    SELECT %s, %s, p.name, %s, 2 FROM products p WHERE p.id = %s
                """
                execute_update(sql, (sn, product_id, card_no, product_id))
        
        # 更新入库单状态
        sql = "UPDATE production_stock_in SET status = 3 WHERE id = %s"
        return execute_update(sql, (in_id,))

    @staticmethod
    def generate_in_no():
        """生成入库单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM production_stock_in WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"SR{date_str}{str(count + 1).zfill(4)}"


class ProductionScrapService:
    """生产报废服务类"""

    @staticmethod
    def get_all_scraps():
        """获取所有报废记录"""
        sql = """
            SELECT psr.id, psr.scrap_no, psr.source_type, psr.product_id, 
                   psr.product_name, psr.quantity, psr.reason, psr.responsible, psr.status
            FROM production_scrap_records psr
            ORDER BY psr.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def add_scrap(source_type, source_id, product_id, product_name, quantity, reason, responsible=""):
        """添加报废记录"""
        scrap_no = ProductionScrapService.generate_scrap_no()
        sql = """
            INSERT INTO production_scrap_records (scrap_no, source_type, source_id, 
                                                  product_id, product_name, quantity, 
                                                  reason, responsible, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        return execute_update(sql, (scrap_no, source_type, source_id, product_id, 
                                    product_name, quantity, reason, responsible))

    @staticmethod
    def approve_scrap(scrap_id):
        """审批报废记录"""
        sql = "UPDATE production_scrap_records SET status = 2 WHERE id = %s"
        return execute_update(sql, (scrap_id,))

    @staticmethod
    def generate_scrap_no():
        """生成报废单号"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        sql = "SELECT COUNT(*) FROM production_scrap_records WHERE DATE(created_at) = CURDATE()"
        count = execute_query(sql)[0][0]
        return f"BF{date_str}{str(count + 1).zfill(4)}"
