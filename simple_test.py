import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置临时 PATH
os.environ['PATH'] = "C:\\Users\\ASUS\\python-sdk\\python3.13.2;" + os.environ.get('PATH', '')

from config.database import execute_query, get_connection

print("测试数据库连接和查询...")

# 测试连接
conn = get_connection()
if conn:
    print("[OK] 数据库连接成功")
    conn.close()
else:
    print("[FAIL] 数据库连接失败")
    sys.exit(1)

# 测试简单查询
print("\n测试查询 sales_orders 表...")
sql = "SELECT * FROM sales_orders LIMIT 5"
result = execute_query(sql)
if result is None:
    print("[FAIL] 查询失败")
elif len(result) == 0:
    print("[OK] 查询成功，表为空")
else:
    print(f"[OK] 查询成功，返回 {len(result)} 条记录")
    for row in result:
        print(f"  {row}")

print("\n测试查询 products 表...")
sql = "SELECT id, product_code, name, stock FROM products LIMIT 3"
result = execute_query(sql)
if result is None:
    print("[FAIL] 查询失败")
elif len(result) == 0:
    print("[OK] 查询成功，表为空")
else:
    print(f"[OK] 查询成功，返回 {len(result)} 条记录")
    for row in result:
        print(f"  {row}")

print("\n测试完成！")