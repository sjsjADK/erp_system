# 数据统计界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.statistics_service import (
    SalesStatisticsService, InventoryStatisticsService,
    ProductionStatisticsService, AfterSalesStatisticsService,
    SystemStatisticsService
)
from datetime import datetime

class StatisticsView:
    """数据统计界面类"""

    def __init__(self, parent):
        self.parent = parent
        self.parent.pack(fill=tk.BOTH, expand=True)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        """设置界面布局"""
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        title_label = ttk.Label(main_frame, text="📊 数据统计", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        # 今日概览卡片
        overview_frame = ttk.LabelFrame(main_frame, text="今日概览")
        overview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        today = datetime.now().strftime("%Y-%m-%d")
        sales_stats = SalesStatisticsService.get_daily_sales(today)[0]
        
        card_frame = ttk.Frame(overview_frame)
        card_frame.pack(fill=tk.X, padx=10, pady=10)
        
        cards = [
            ("今日订单", str(sales_stats[0])),
            ("今日销售额", f"¥{sales_stats[1]:,.2f}" if sales_stats[1] else "¥0.00"),
            ("今日销量", str(sales_stats[2])),
            ("系统用户", str(SystemStatisticsService.get_user_count()))
        ]
        
        for label, value in cards:
            card = ttk.LabelFrame(card_frame, text=label)
            card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            ttk.Label(card, text=value, font=("Microsoft YaHei", 20, "bold")).pack(pady=10)

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_sales = ttk.Frame(tab_control)
        self.tab_inventory = ttk.Frame(tab_control)
        self.tab_production = ttk.Frame(tab_control)
        self.tab_after_sales = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_sales, text='💰 销售统计')
        tab_control.add(self.tab_inventory, text='📦 库存统计')
        tab_control.add(self.tab_production, text='🏭 生产统计')
        tab_control.add(self.tab_after_sales, text='🛠️ 售后统计')
        
        tab_control.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_sales_tab()
        self.setup_inventory_tab()
        self.setup_production_tab()
        self.setup_after_sales_tab()

    def setup_sales_tab(self):
        """销售统计标签页"""
        frame = self.tab_sales
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # 月度销售
        month_frame = ttk.LabelFrame(frame, text="本月销售")
        month_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        now = datetime.now()
        monthly_sales = SalesStatisticsService.get_monthly_sales(now.year, now.month)[0]
        
        stats = [
            ("订单数", str(monthly_sales[0])),
            ("销售总额", f"¥{monthly_sales[1]:,.2f}" if monthly_sales[1] else "¥0.00"),
            ("销售总量", str(monthly_sales[2]))
        ]
        
        for label, value in stats:
            ttk.Label(month_frame, text=f"{label}: {value}").pack(side=tk.LEFT, padx=20, pady=10)

        # 销售趋势
        trend_frame = ttk.LabelFrame(frame, text="销售趋势（近7天）")
        trend_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        trend_frame.columnconfigure(0, weight=1)
        
        trend_data = SalesStatisticsService.get_sales_trend(7)
        
        canvas = tk.Canvas(trend_frame, width=800, height=200)
        canvas.pack(padx=10, pady=10)
        
        if trend_data:
            max_amount = max([d[2] for d in trend_data]) if trend_data else 1
            for i, (date, orders, amount) in enumerate(trend_data):
                height = (amount / max_amount) * 150 if max_amount > 0 else 0
                canvas.create_rectangle(i * 100 + 50, 180 - height, 
                                       i * 100 + 90, 180, fill="#2196F3")
                canvas.create_text(i * 100 + 70, 195, text=str(date)[5:])

        # 销量排行
        ranking_frame = ttk.LabelFrame(frame, text="销量排行榜")
        ranking_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ranking_frame.columnconfigure(0, weight=1)
        ranking_frame.rowconfigure(0, weight=1)
        
        tree = ttk.Treeview(ranking_frame, columns=("rank", "product_name", "quantity", "amount"), show="headings")
        tree.heading("rank", text="排名")
        tree.heading("product_name", text="产品名称")
        tree.heading("quantity", text="销量")
        tree.heading("amount", text="销售额")
        
        scrollbar = ttk.Scrollbar(ranking_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        sales_ranking = SalesStatisticsService.get_sales_by_product(10)
        for i, item in enumerate(sales_ranking, 1):
            tree.insert("", tk.END, values=(i, item[0], item[1], f"¥{item[2]:,.2f}"))

    def setup_inventory_tab(self):
        """库存统计标签页"""
        frame = self.tab_inventory
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # 库存汇总
        summary_frame = ttk.LabelFrame(frame, text="库存汇总")
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        inventory_summary = InventoryStatisticsService.get_inventory_summary()[0]
        
        stats = [
            ("产品种类", str(inventory_summary[0])),
            ("库存总量", str(inventory_summary[1])),
            ("库存价值", f"¥{inventory_summary[2]:,.2f}" if inventory_summary[2] else "¥0.00"),
            ("低库存产品", str(inventory_summary[3]))
        ]
        
        for label, value in stats:
            ttk.Label(summary_frame, text=f"{label}: {value}").pack(side=tk.LEFT, padx=20, pady=10)

        # 分类库存
        category_frame = ttk.LabelFrame(frame, text="分类库存")
        category_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        category_data = InventoryStatisticsService.get_inventory_by_category()
        if category_data:
            max_stock = max([c[2] for c in category_data])
            for category, count, stock, value in category_data:
                bar_frame = ttk.Frame(category_frame)
                bar_frame.pack(fill=tk.X, padx=10, pady=5)
                ttk.Label(bar_frame, text=category, width=15).pack(side=tk.LEFT)
                bar = ttk.Progressbar(bar_frame, mode='determinate', maximum=max_stock)
                bar['value'] = stock
                bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                ttk.Label(bar_frame, text=str(stock), width=8).pack(side=tk.LEFT)

        # 低库存警告
        low_frame = ttk.LabelFrame(frame, text="⚠️ 低库存产品")
        low_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        low_frame.columnconfigure(0, weight=1)
        low_frame.rowconfigure(0, weight=1)
        
        tree = ttk.Treeview(low_frame, columns=("product_code", "name", "stock", "unit", "price"), show="headings")
        tree.heading("product_code", text="商品编码")
        tree.heading("name", text="商品名称")
        tree.heading("stock", text="库存")
        tree.heading("unit", text="单位")
        tree.heading("price", text="单价")
        
        scrollbar = ttk.Scrollbar(low_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        low_stock = InventoryStatisticsService.get_low_stock_products()
        for item in low_stock:
            tree.insert("", tk.END, values=(item[0], item[1], item[2], item[3], f"¥{item[4]:,.2f}"))

    def setup_production_tab(self):
        """生产统计标签页"""
        frame = self.tab_production
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # 月度生产
        month_frame = ttk.LabelFrame(frame, text="本月生产")
        month_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        now = datetime.now()
        monthly_production = ProductionStatisticsService.get_monthly_production(now.year, now.month)[0]
        
        stats = [
            ("生产订单", str(monthly_production[0])),
            ("计划产量", str(monthly_production[1])),
            ("实际产量", str(monthly_production[2])),
            ("已完成", str(monthly_production[3]))
        ]
        
        for label, value in stats:
            ttk.Label(month_frame, text=f"{label}: {value}").pack(side=tk.LEFT, padx=20, pady=10)

        # 报废率
        scrap_frame = ttk.LabelFrame(frame, text="报废率")
        scrap_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        scrap_rate = ProductionStatisticsService.get_scrap_rate()[0]
        total_scrap = scrap_rate[0] if scrap_rate[0] else 0
        total_produced = scrap_rate[1] if scrap_rate[1] else 1
        rate = (total_scrap / total_produced) * 100
        
        ttk.Label(scrap_frame, text=f"报废数量: {total_scrap}").pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Label(scrap_frame, text=f"生产总量: {total_produced}").pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Label(scrap_frame, text=f"报废率: {rate:.2f}%").pack(side=tk.LEFT, padx=20, pady=10)

    def setup_after_sales_tab(self):
        """售后统计标签页"""
        frame = self.tab_after_sales
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # 月度售后
        month_frame = ttk.LabelFrame(frame, text="本月售后")
        month_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        now = datetime.now()
        monthly_after_sales = AfterSalesStatisticsService.get_monthly_after_sales(now.year, now.month)[0]
        
        stats = [
            ("售后工单", str(monthly_after_sales[0])),
            ("已完成", str(monthly_after_sales[1])),
            ("紧急工单", str(monthly_after_sales[2]))
        ]
        
        for label, value in stats:
            ttk.Label(month_frame, text=f"{label}: {value}").pack(side=tk.LEFT, padx=20, pady=10)
