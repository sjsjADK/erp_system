# 系统配置服务层
# 处理系统配置和日志相关的业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update
from datetime import datetime

class SystemConfigService:
    """系统配置服务类"""

    @staticmethod
    def get_config(key):
        """获取配置值"""
        sql = "SELECT config_value FROM system_config WHERE config_key = %s"
        results = execute_query(sql, (key,))
        return results[0][0] if results else None

    @staticmethod
    def set_config(key, value, description=""):
        """设置配置值"""
        # 先检查是否存在
        sql = "SELECT id FROM system_config WHERE config_key = %s"
        results = execute_query(sql, (key,))
        
        if results:
            # 更新
            sql = "UPDATE system_config SET config_value = %s, config_desc = %s WHERE config_key = %s"
            return execute_update(sql, (value, description, key))
        else:
            # 插入
            sql = "INSERT INTO system_config (config_key, config_value, config_desc) VALUES (%s, %s, %s)"
            return execute_update(sql, (key, value, description))

    @staticmethod
    def get_all_configs():
        """获取所有配置"""
        sql = "SELECT config_key, config_value, config_desc FROM system_config ORDER BY config_key"
        return execute_query(sql)

    @staticmethod
    def delete_config(key):
        """删除配置"""
        sql = "DELETE FROM system_config WHERE `key` = %s"
        return execute_update(sql, (key,))


class OperationLogService:
    """操作日志服务类"""

    @staticmethod
    def get_all_logs():
        """获取所有操作日志"""
        sql = """
            SELECT ol.id, ol.module, ol.operation, ol.content, 
                   ol.username, ol.created_at, ol.ip
            FROM operation_logs ol
            ORDER BY ol.created_at DESC
            LIMIT 100
        """
        return execute_query(sql)

    @staticmethod
    def add_log(module, operation, content, username="", ip=""):
        """添加操作日志"""
        sql = """
            INSERT INTO operation_logs (module, operation, content, username, ip)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_update(sql, (module, operation, content, username, ip))

    @staticmethod
    def get_logs_by_module(module):
        """按模块获取日志"""
        sql = """
            SELECT ol.id, ol.operation, ol.content, ol.username, ol.created_at
            FROM operation_logs ol
            WHERE ol.module = %s
            ORDER BY ol.created_at DESC
        """
        return execute_query(sql, (module,))

##面向对象——用户服务类
class UserService:
    """用户服务类"""

    @staticmethod
    def get_all_users():
        """获取所有用户"""
        sql = """
            SELECT u.id, u.username, u.real_name, 
                   (SELECT GROUP_CONCAT(r.name) FROM roles r WHERE FIND_IN_SET(r.id, u.role_ids)) as role_name,
                   u.status, u.created_at
            FROM users u
            ORDER BY u.created_at DESC
        """
        return execute_query(sql)

    @staticmethod
    def add_user(username, password, real_name, role_id=1, status=1):
        """添加用户"""
        sql = """
            INSERT INTO users (username, password_hash, real_name, role_ids, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_update(sql, (username, password, real_name, str(role_id), status))

    @staticmethod
    def update_user(user_id, username, real_name, role_id, status):
        """更新用户"""
        sql = """
            UPDATE users 
            SET username = %s, real_name = %s, role_ids = %s, status = %s
            WHERE id = %s
        """
        return execute_update(sql, (username, real_name, str(role_id), status, user_id))

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        sql = "DELETE FROM users WHERE id = %s"
        return execute_update(sql, (user_id,))

    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        sql = "SELECT * FROM users WHERE username = %s AND password_hash = %s AND status = 1"
        results = execute_query(sql, (username, password))
        return results[0] if results else None


class RoleService:
    """角色服务类"""

    @staticmethod
    def get_all_roles():
        """获取所有角色"""
        sql = "SELECT id, name, remark FROM roles ORDER BY id"
        return execute_query(sql)

    @staticmethod
    def add_role(name, remark=""):
        """添加角色"""
        sql = "INSERT INTO roles (name, remark) VALUES (%s, %s)"
        return execute_update(sql, (name, remark))

    @staticmethod
    def update_role(role_id, name, remark):
        """更新角色"""
        sql = "UPDATE roles SET name = %s, remark = %s WHERE id = %s"
        return execute_update(sql, (name, remark, role_id))

    @staticmethod
    def delete_role(role_id):
        """删除角色"""
        sql = "DELETE FROM roles WHERE id = %s"
        return execute_update(sql, (role_id,))
