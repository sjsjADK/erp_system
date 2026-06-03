# 商品服务层
# 处理商品的相关业务逻辑

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_query, execute_update

class ProductService:
    """商品服务类"""

    @staticmethod
    def get_all_products():
        """获取所有商品"""
        sql = "SELECT id, product_code, name, model, category_id, spec, price, stock, unit, supplier, description FROM products ORDER BY id"
        return execute_query(sql)

    @staticmethod
    def search_products(keyword):
        """搜索商品"""
        sql = """
            SELECT id, product_code, name, model, category_id, spec, price, stock, unit, supplier, description
            FROM products
            WHERE name LIKE %s OR product_code LIKE %s OR model LIKE %s
            ORDER BY id
        """
        keyword = f"%{keyword}%"
        return execute_query(sql, (keyword, keyword, keyword))

    @staticmethod
    def get_product_by_id(product_id):
        """根据ID获取商品"""
        sql = "SELECT id, product_code, name, model, category_id, spec, price, stock, unit, supplier, description FROM products WHERE id = %s"
        results = execute_query(sql, (product_id,))
        return results[0] if results else None

    @staticmethod
    def add_product(product_code, name, model, category_id, spec, price, stock, unit, supplier, description):
        """添加商品"""
        sql = """
            INSERT INTO products (product_code, name, model, category_id, spec, price, stock, unit, supplier, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_update(sql, (product_code, name, model, category_id, spec, price, stock, unit, supplier, description))

    @staticmethod
    def update_product(product_id, product_code, name, model, category_id, spec, price, stock, unit, supplier, description):
        """更新商品"""
        sql = """
            UPDATE products
            SET product_code = %s, name = %s, model = %s, category_id = %s, spec = %s,
                price = %s, stock = %s, unit = %s, supplier = %s, description = %s
            WHERE id = %s
        """
        return execute_update(sql, (product_code, name, model, category_id, spec, price, stock, unit, supplier, description, product_id))

    @staticmethod
    def delete_product(product_id):
        """删除商品"""
        sql = "DELETE FROM products WHERE id = %s"
        return execute_update(sql, (product_id,))

    @staticmethod
    def update_stock(product_id, quantity):
        """更新库存"""
        sql = "UPDATE products SET stock = stock + %s WHERE id = %s"
        return execute_update(sql, (quantity, product_id))

    @staticmethod
    def get_low_stock_products(threshold=10):
        """获取低库存商品"""
        sql = "SELECT id, product_code, name, stock FROM products WHERE stock < %s ORDER BY stock"
        return execute_query(sql, (threshold,))

    @staticmethod
    def get_product_count():
        """获取商品总数"""
        sql = "SELECT COUNT(*) FROM products"
        results = execute_query(sql)
        return results[0][0] if results else 0

    @staticmethod
    def get_category_stats():
        """获取各分类统计"""
        sql = """
            SELECT pc.name as category_name, COUNT(p.id) as count, SUM(p.stock) as total_stock 
            FROM products p 
            LEFT JOIN product_categories pc ON p.category_id = pc.id 
            GROUP BY p.category_id, pc.name
        """
        return execute_query(sql)
