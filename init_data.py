# 初始化测试数据
# 向商品表添加一些测试数据

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import execute_update, init_database
from services.product_service import ProductService

def init_test_data():
    """初始化测试数据"""
    print("正在初始化测试数据...")

    service = ProductService()

    # 测试商品数据
    test_products = [
        ("P001", "联想ThinkPad笔记本", "电脑", 5999.00, 50, "台", "联想集团", "ThinkPad T490商务本"),
        ("P002", "罗技无线鼠标", "外设", 159.00, 200, "个", "罗技电子", "M590静音无线鼠标"),
        ("P003", "戴尔显示器27寸", "显示器", 1899.00, 80, "台", "戴尔科技", "U2720Q 4K专业显示器"),
        ("P004", "金士顿8G内存条", "电脑配件", 299.00, 150, "条", "金士顿科技", "DDR4 2666MHz"),
        ("P005", "三星500G固态硬盘", "存储设备", 499.00, 100, "个", "三星电子", "970 EVO Plus NVMe"),
        ("P006", "机械键盘RGB", "外设", 399.00, 75, "把", "雷蛇科技", "黑寡妇蜘蛛轻量版"),
        ("P007", "TP-Link路由器", "网络设备", 249.00, 120, "台", "TP-Link", "AX3000 WiFi6路由器"),
        ("P008", "HP打印机", "办公设备", 1299.00, 30, "台", "惠普公司", "LaserJet Pro M404dn"),
        ("P009", "Sony耳机", "音频设备", 899.00, 60, "副", "索尼公司", "WH-1000XM4降噪耳机"),
        ("P010", "小米移动电源", "配件", 149.00, 300, "个", "小米科技", "20000mAh快充版"),
    ]

    # 检查是否已有数据
    count = service.get_product_count()
    if count > 0:
        print(f"数据库中已有 {count} 条商品数据，跳过初始化")
        return

    # 插入测试数据
    success_count = 0
    for product in test_products:
        if service.add_product(*product):
            success_count += 1
            print(f"✓ 添加商品: {product[1]}")

    print(f"\n成功添加 {success_count} 条测试数据！")


if __name__ == "__main__":
    # 初始化数据库
    init_database()
    # 初始化测试数据
    init_test_data()
