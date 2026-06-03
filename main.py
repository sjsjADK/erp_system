# ERP系统主程序入口
# 简易ERP系统 - 完整功能版本

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import init_database
from views.product_view import ProductView
from views.sale_view import SaleView
from views.production_view import ProductionView
from views.warehouse_view import WarehouseView
from views.after_sales_view import AfterSalesView
from views.logistics_view import LogisticsView
from views.maintenance_view import MaintenanceView
from views.statistics_view import StatisticsView
from views.system_view import SystemView
import tkinter as tk
from tkinter import ttk


class MainApp:
    """主应用程序，支持多模块切换"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ERP系统（初学者）")
        self.root.geometry("1200x750")
        
        # 设置窗口图标（如果有）
        try:
            self.root.iconbitmap("erp.ico")
        except:
            pass
        
        self.current_frame = None
        self.setup_ui()
        self.show_product_view()
    
    def setup_ui(self):
        """设置主界面"""
        # 菜单栏
        menubar = tk.Menu(self.root)
        
        # 商品管理菜单
        product_menu = tk.Menu(menubar, tearoff=0)
        product_menu.add_command(label="📦 商品管理", command=self.show_product_view)
        menubar.add_cascade(label="商品管理", menu=product_menu)
        
        # 销售管理菜单
        sale_menu = tk.Menu(menubar, tearoff=0)
        sale_menu.add_command(label="💰 销售管理", command=self.show_sale_view)
        menubar.add_cascade(label="销售管理", menu=sale_menu)
        
        # 生产管理菜单
        production_menu = tk.Menu(menubar, tearoff=0)
        production_menu.add_command(label="🏭 生产管理", command=self.show_production_view)
        menubar.add_cascade(label="生产管理", menu=production_menu)
        
        # 仓库管理菜单
        warehouse_menu = tk.Menu(menubar, tearoff=0)
        warehouse_menu.add_command(label="📦 仓库管理", command=self.show_warehouse_view)
        menubar.add_cascade(label="仓库管理", menu=warehouse_menu)
        
        # 售后管理菜单
        after_sales_menu = tk.Menu(menubar, tearoff=0)
        after_sales_menu.add_command(label="🛠️ 售后管理", command=self.show_after_sales_view)
        menubar.add_cascade(label="售后管理", menu=after_sales_menu)
        
        # 物流管理菜单
        logistics_menu = tk.Menu(menubar, tearoff=0)
        logistics_menu.add_command(label="📦 物流管理", command=self.show_logistics_view)
        menubar.add_cascade(label="物流管理", menu=logistics_menu)
        
        # 维修管理菜单
        maintenance_menu = tk.Menu(menubar, tearoff=0)
        maintenance_menu.add_command(label="🔧 维修管理", command=self.show_maintenance_view)
        menubar.add_cascade(label="维修管理", menu=maintenance_menu)
        
        # 统计分析菜单
        statistics_menu = tk.Menu(menubar, tearoff=0)
        statistics_menu.add_command(label="📊 数据统计", command=self.show_statistics_view)
        menubar.add_cascade(label="统计分析", menu=statistics_menu)
        
        # 系统管理菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        system_menu.add_command(label="⚙️ 系统配置", command=self.show_system_view)
        system_menu.add_separator()
        system_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="系统管理", menu=system_menu)
        
        self.root.config(menu=menubar)
        
        # 顶部标题和快捷切换栏
        top_frame = ttk.Frame(self.root, padding="15")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="🏪 ERP系统（初学者）", font=("Microsoft YaHei", 20, "bold")).pack(side=tk.LEFT)
        
        # 快捷切换按钮组
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # 第一排按钮
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill=tk.X)
        
        ttk.Button(row1_frame, text="📦 商品", command=self.show_product_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1_frame, text="💰 销售", command=self.show_sale_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1_frame, text="🏭 生产", command=self.show_production_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1_frame, text="📦 仓库", command=self.show_warehouse_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row1_frame, text="🛠️ 售后", command=self.show_after_sales_view, width=12).pack(side=tk.LEFT, padx=3)
        
        # 第二排按钮
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill=tk.X)
        
        ttk.Button(row2_frame, text="📦 物流", command=self.show_logistics_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row2_frame, text="🔧 维修", command=self.show_maintenance_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row2_frame, text="📊 统计", command=self.show_statistics_view, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(row2_frame, text="⚙️ 系统", command=self.show_system_view, width=12).pack(side=tk.LEFT, padx=3)
        
        # 内容区域
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def clear_content(self):
        """清除内容区域"""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
    
    def show_product_view(self):
        """显示商品管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = ProductView(self.current_frame)
        self.root.title("ERP系统（初学者） - 商品管理")
    
    def show_sale_view(self):
        """显示销售管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = SaleView(self.current_frame)
        self.root.title("ERP系统（初学者） - 销售管理")
    
    def show_production_view(self):
        """显示生产管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = ProductionView(self.current_frame)
        self.root.title("ERP系统（初学者） - 生产管理")
    
    def show_warehouse_view(self):
        """显示仓库管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = WarehouseView(self.current_frame)
        self.root.title("ERP系统（初学者） - 仓库管理")
    
    def show_after_sales_view(self):
        """显示售后管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = AfterSalesView(self.current_frame)
        self.root.title("ERP系统（初学者） - 售后管理")
    
    def show_logistics_view(self):
        """显示物流管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = LogisticsView(self.current_frame)
        self.root.title("ERP系统（初学者） - 物流管理")
    
    def show_maintenance_view(self):
        """显示维修管理界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = MaintenanceView(self.current_frame)
        self.root.title("ERP系统（初学者） - 维修管理")
    
    def show_statistics_view(self):
        """显示数据统计界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = StatisticsView(self.current_frame)
        self.root.title("ERP系统（初学者） - 数据统计")
    
    def show_system_view(self):
        """显示系统配置界面"""
        self.clear_content()
        self.current_frame = ttk.Frame(self.content_frame)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        app = SystemView(self.current_frame)
        self.root.title("ERP系统（初学者） - 系统配置")


def main():
    """主函数"""
    print("=" * 60)
    print("ERP系统（初学者）")
    print("=" * 60)

    # 初始化数据库
    print("\n[1/3] 初始化数据库...")
    if not init_database():
        print("数据库初始化失败，请检查MySQL服务是否启动")
        input("按回车键退出...")
        return

    # 启动GUI
    print("[2/3] 启动主界面...")
    print("[3/3] 系统就绪！")
    print("\n系统模块列表:")
    print("  [P] 商品管理    - 商品信息管理、库存查询")
    print("  [S] 销售管理    - 销售订单、销售统计")
    print("  [M] 生产管理    - 生产订单、领料、入库、报废")
    print("  [W] 仓库管理    - 入库、出库、库存流水、盘点")
    print("  [A] 售后管理    - 售后工单、设备管理")
    print("  [L] 物流管理    - 物流订单、跟踪")
    print("  [R] 维修管理    - 维修记录、配件管理")
    print("  [D] 数据统计    - 各模块统计报表")
    print("  [C] 系统配置    - 用户、角色、日志")

    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()