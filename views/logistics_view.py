# 物流管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.logistics_service import (
    LogisticsOrderService, LogisticsTrackingService, LogisticsStatisticsService
)
from services.product_service import ProductService
from datetime import datetime

class LogisticsView:
    """物流管理界面类"""

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
        main_frame.rowconfigure(1, weight=1)

        title_label = ttk.Label(main_frame, text="📦 物流管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_order = ttk.Frame(tab_control)
        self.tab_statistics = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_order, text='📋 物流订单')
        tab_control.add(self.tab_statistics, text='📊 物流统计')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_order_tab()
        self.setup_statistics_tab()

    def setup_order_tab(self):
        """物流订单标签页"""
        frame = self.tab_order
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        # 左侧订单列表
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增订单", command=self.add_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑订单", command=self.edit_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_orders).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("order_no", "sender", "receiver", "status", "shipping_method", "tracking_no")
        self.order_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.order_tree.heading("order_no", text="订单号")
        self.order_tree.heading("sender", text="发货人")
        self.order_tree.heading("receiver", text="收货人")
        self.order_tree.heading("status", text="状态")
        self.order_tree.heading("shipping_method", text="运输方式")
        self.order_tree.heading("tracking_no", text="运单号")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        self.order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.order_tree.bind('<<TreeviewSelect>>', self.on_order_select)
        self.selected_order_id = None
        
        self.load_orders()

        # 右侧详情面板
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(3, weight=1)

        # 订单明细
        detail_frame = ttk.LabelFrame(right_frame, text="订单明细")
        detail_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        self.detail_tree = ttk.Treeview(detail_frame, columns=("product_name", "quantity", "weight", "volume"), show="headings")
        self.detail_tree.heading("product_name", text="产品名称")
        self.detail_tree.heading("quantity", text="数量")
        self.detail_tree.heading("weight", text="重量(kg)")
        self.detail_tree.heading("volume", text="体积(m³)")
        self.detail_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 物流跟踪
        tracking_frame = ttk.LabelFrame(right_frame, text="物流跟踪")
        tracking_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tracking_frame.columnconfigure(0, weight=1)
        tracking_frame.rowconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(tracking_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(btn_frame, text="➕ 添加跟踪", command=self.add_tracking).pack(side=tk.LEFT, padx=5)
        
        self.tracking_tree = ttk.Treeview(tracking_frame, columns=("tracking_time", "location", "status", "remark"), show="headings")
        self.tracking_tree.heading("tracking_time", text="时间")
        self.tracking_tree.heading("location", text="位置")
        self.tracking_tree.heading("status", text="状态")
        self.tracking_tree.heading("remark", text="备注")
        self.tracking_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 状态操作
        action_frame = ttk.LabelFrame(right_frame, text="状态操作")
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(action_frame, text="📤 发货", command=lambda: self.update_order_status(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🚚 运输中", command=lambda: self.update_order_status(3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✅ 签收", command=lambda: self.update_order_status(4)).pack(side=tk.LEFT, padx=5)

    def load_orders(self):
        """加载物流订单"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        orders = LogisticsOrderService.get_all_orders()
        if orders:
            for order in orders:
                status_text = LogisticsOrderService.get_status_text(order[4])
                self.order_tree.insert("", tk.END, values=(
                    order[1], order[2], order[3], status_text, order[5], order[7]
                ))

    def on_order_select(self, event):
        """选择订单"""
        selection = self.order_tree.selection()
        if selection:
            item = self.order_tree.item(selection[0])
            order_no = item['values'][0]
            orders = LogisticsOrderService.get_all_orders()
            for order in orders:
                if order[1] == order_no:
                    self.selected_order_id = order[0]
                    self.load_order_details(order[0])
                    self.load_tracking(order[0])
                    break

    def load_order_details(self, order_id):
        """加载订单明细"""
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        details = LogisticsOrderService.get_order_details(order_id)
        if details:
            for detail in details:
                self.detail_tree.insert("", tk.END, values=(detail[2], detail[3], detail[4], detail[5]))

    def load_tracking(self, order_id):
        """加载跟踪记录"""
        for item in self.tracking_tree.get_children():
            self.tracking_tree.delete(item)
        
        tracking = LogisticsTrackingService.get_tracking_by_order(order_id)
        if tracking:
            for track in tracking:
                self.tracking_tree.insert("", tk.END, values=(track[1], track[2], track[3], track[4]))

    def add_order(self):
        """新增物流订单"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增物流订单")
        dialog.geometry("500x500")
        
        ttk.Label(dialog, text="发货人:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        sender_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=sender_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="收货人:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        receiver_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=receiver_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="运输方式:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        shipping_methods = ['顺丰', '圆通', '中通', '韵达', 'EMS', '其他']
        shipping_combobox = ttk.Combobox(dialog, values=shipping_methods, state="readonly", width=27)
        shipping_combobox.grid(row=2, column=1, padx=20)
        shipping_combobox.current(0)
        
        ttk.Label(dialog, text="预计送达日期:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=33).grid(row=3, column=1, padx=20)

        product_frame = ttk.Frame(dialog)
        product_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(product_frame, text="产品:").pack(side=tk.LEFT)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(product_frame, values=product_names, state="readonly", width=20)
        product_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="数量:").pack(side=tk.LEFT)
        qty_entry = ttk.Entry(product_frame, width=8)
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="重量(kg):").pack(side=tk.LEFT)
        weight_entry = ttk.Entry(product_frame, width=8)
        weight_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(product_frame, text="添加", command=lambda: self.add_order_product(product_combobox, qty_entry, weight_entry, product_listbox, products))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        product_listbox = tk.Listbox(dialog, width=60, height=5)
        product_listbox.grid(row=5, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_order_products = []

        def save():
            if not self.selected_order_products:
                messagebox.showwarning("提示", "请添加至少一个产品！")
                return
            
            if LogisticsOrderService.add_order(sender_var.get(), receiver_var.get(), 
                                            shipping_combobox.get(), date_var.get(), 
                                            self.selected_order_products):
                messagebox.showinfo("成功", "新增物流订单成功！")
                self.load_orders()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增物流订单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_order_product(self, product_combobox, qty_entry, weight_entry, listbox, products):
        """添加产品到订单列表"""
        idx = product_combobox.current()
        if idx < 0:
            return
        
        try:
            qty = int(qty_entry.get())
            weight = float(weight_entry.get())
            if qty <= 0 or weight < 0:
                messagebox.showwarning("提示", "数量必须大于0，重量不能为负！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数字！")
            return
        
        product = products[idx]
        product_info = {
            'product_id': product[0],
            'product_name': product[2],
            'quantity': qty,
            'weight': weight,
            'volume': weight * 0.001  # 估算体积
        }
        
        self.selected_order_products.append(product_info)
        listbox.insert(tk.END, f"{product[2]} x {qty} ({weight}kg)")
        qty_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)

    def edit_order(self):
        """编辑订单"""
        if not self.selected_order_id:
            messagebox.showwarning("提示", "请先选择订单！")
            return
        
        order = LogisticsOrderService.get_order_by_id(self.selected_order_id)
        if not order:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑物流订单")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="发货人:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        sender_var = tk.StringVar(value=order[2])
        ttk.Entry(dialog, textvariable=sender_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="收货人:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        receiver_var = tk.StringVar(value=order[3])
        ttk.Entry(dialog, textvariable=receiver_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="运输方式:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        shipping_methods = ['顺丰', '圆通', '中通', '韵达', 'EMS', '其他']
        shipping_combobox = ttk.Combobox(dialog, values=shipping_methods, state="readonly", width=27)
        shipping_combobox.grid(row=2, column=1, padx=20)
        shipping_combobox.current(shipping_methods.index(order[5]) if order[5] in shipping_methods else 5)
        
        ttk.Label(dialog, text="运单号:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        tracking_var = tk.StringVar(value=order[7])
        ttk.Entry(dialog, textvariable=tracking_var, width=33).grid(row=3, column=1, padx=20)

        def save():
            if LogisticsOrderService.update_order(self.selected_order_id, sender_var.get(), 
                                               receiver_var.get(), shipping_combobox.get(), 
                                               order[4], tracking_var.get(), order[8]):
                messagebox.showinfo("成功", "修改订单成功！")
                self.load_orders()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改订单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_tracking(self):
        """添加跟踪记录"""
        if not self.selected_order_id:
            messagebox.showwarning("提示", "请先选择订单！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加跟踪记录")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="当前位置:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        location_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=location_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="状态:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['待发货', '已发货', '运输中', '派送中', '已签收'], state="readonly", width=27)
        status_combobox.grid(row=1, column=1, padx=20)
        status_combobox.current(0)
        
        ttk.Label(dialog, text="备注:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        remark_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=remark_var, width=33).grid(row=2, column=1, padx=20)

        def save():
            if LogisticsTrackingService.add_tracking(self.selected_order_id, 
                                                   location_var.get(), status_combobox.get(), remark_var.get()):
                messagebox.showinfo("成功", "添加跟踪记录成功！")
                self.load_tracking(self.selected_order_id)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加跟踪记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_order_status(self, status):
        """更新订单状态"""
        if not self.selected_order_id:
            messagebox.showwarning("提示", "请先选择订单！")
            return
        
        if LogisticsOrderService.update_status(self.selected_order_id, status):
            messagebox.showinfo("成功", "状态更新成功！")
            self.load_orders()
        else:
            messagebox.showerror("错误", "状态更新失败！")

    def setup_statistics_tab(self):
        """物流统计标签页"""
        frame = self.tab_statistics
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # 统计卡片
        stats_frame = ttk.Frame(frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        today_stats = LogisticsStatisticsService.get_daily_statistics(datetime.now().strftime("%Y-%m-%d"))[0]
        method_stats = LogisticsStatisticsService.get_shipping_method_statistics()
        
        card1 = ttk.LabelFrame(stats_frame, text="今日订单")
        card1.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(card1, text=str(today_stats[0]), font=("Microsoft YaHei", 20, "bold")).pack(pady=10)
        
        card2 = ttk.LabelFrame(stats_frame, text="今日完成")
        card2.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(card2, text=str(today_stats[1]), font=("Microsoft YaHei", 20, "bold")).pack(pady=10)
        
        card3 = ttk.LabelFrame(stats_frame, text="今日取消")
        card3.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(card3, text=str(today_stats[2]), font=("Microsoft YaHei", 20, "bold")).pack(pady=10)

        # 运输方式统计
        method_frame = ttk.LabelFrame(frame, text="运输方式分布")
        method_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        if method_stats:
            max_count = max([m[1] for m in method_stats])
            for method, count in method_stats:
                bar_frame = ttk.Frame(method_frame)
                bar_frame.pack(fill=tk.X, padx=10, pady=5)
                ttk.Label(bar_frame, text=method, width=10).pack(side=tk.LEFT)
                bar = ttk.Progressbar(bar_frame, mode='determinate', maximum=max_count)
                bar['value'] = count
                bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                ttk.Label(bar_frame, text=str(count), width=5).pack(side=tk.LEFT)

        # 订单趋势（简化展示）
        trend_frame = ttk.LabelFrame(frame, text="订单趋势")
        trend_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        trend_frame.columnconfigure(0, weight=1)
        
        ttk.Label(trend_frame, text="近7天订单趋势图（模拟数据）").pack(pady=20)
        canvas = tk.Canvas(trend_frame, width=800, height=200)
        canvas.pack()
        
        # 绘制简单柱状图
        data = [12, 18, 15, 22, 19, 25, 20]
        max_data = max(data)
        for i, value in enumerate(data):
            height = (value / max_data) * 150
            canvas.create_rectangle(i * 100 + 50, 180 - height, 
                                   i * 100 + 90, 180, fill="#4CAF50")
            canvas.create_text(i * 100 + 70, 195, text=str(value))
