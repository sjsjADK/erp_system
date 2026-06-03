# 生产管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from services.production_service import (
    ProductionOrderService, MaterialRequisitionService,
    ProductionStockInService, ProductionScrapService
)
from services.product_service import ProductService
from services.product_service import ProductService as PartsService

class ProductionView:
    """生产管理界面类"""

    def __init__(self, parent):
        self.parent = parent
        self.parent.pack(fill=tk.BOTH, expand=True)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.setup_ui()

    def setup_ui(self):
        """设置界面布局"""
        # 主框架
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="🏭 生产管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        # 标签页
        tab_control = ttk.Notebook(main_frame)
        
        self.tab_order = ttk.Frame(tab_control)
        self.tab_requisition = ttk.Frame(tab_control)
        self.tab_stock_in = ttk.Frame(tab_control)
        self.tab_scrap = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_order, text='📋 生产订单')
        tab_control.add(self.tab_requisition, text='📦 生产领料')
        tab_control.add(self.tab_stock_in, text='📥 生产入库')
        tab_control.add(self.tab_scrap, text='🗑️ 生产报废')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置标签页布局
        self.setup_order_tab()
        self.setup_requisition_tab()
        self.setup_stock_in_tab()
        self.setup_scrap_tab()

    def setup_order_tab(self):
        """生产订单标签页"""
        frame = self.tab_order
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # 搜索栏
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(search_frame, text="➕ 新增订单", command=self.add_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="✏️ 编辑订单", command=self.edit_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🗑️ 删除订单", command=self.delete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄 刷新", command=self.load_orders).pack(side=tk.LEFT, padx=5)

        # 表格
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("order_no", "product_name", "plan_qty", "actual_qty", "plan_date", "status", "responsible")
        self.order_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.order_tree.heading("order_no", text="订单号")
        self.order_tree.heading("product_name", text="产品名称")
        self.order_tree.heading("plan_qty", text="计划数量")
        self.order_tree.heading("actual_qty", text="实际数量")
        self.order_tree.heading("plan_date", text="计划日期")
        self.order_tree.heading("status", text="状态")
        self.order_tree.heading("responsible", text="负责人")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        self.order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.order_tree.bind('<<TreeviewSelect>>', self.on_order_select)
        self.selected_order_id = None
        
        self.load_orders()

    def load_orders(self):
        """加载生产订单"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        orders = ProductionOrderService.get_all_orders()
        if orders:
            for order in orders:
                status_text = ProductionOrderService.get_status_text(order[6])
                self.order_tree.insert("", tk.END, values=(
                    order[1], order[2], order[3], order[4], order[5], status_text, order[7]
                ))

    def on_order_select(self, event):
        """选择订单"""
        selection = self.order_tree.selection()
        if selection:
            item = self.order_tree.item(selection[0])
            order_no = item['values'][0]
            orders = ProductionOrderService.get_all_orders()
            for order in orders:
                if order[1] == order_no:
                    self.selected_order_id = order[0]
                    break

    def add_order(self):
        """新增订单"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增生产订单")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="选择产品:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(dialog, values=product_names, state="readonly", width=30)
        product_combobox.grid(row=0, column=1, padx=20)
        product_combobox.current(0)
        
        ttk.Label(dialog, text="计划数量:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        qty_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=qty_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="计划日期:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=33).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="负责人:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        responsible_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=responsible_var, width=33).grid(row=3, column=1, padx=20)

        def save():
            idx = product_combobox.current()
            product_id = products[idx][0]
            try:
                plan_qty = int(qty_var.get())
            except ValueError:
                messagebox.showwarning("提示", "请输入有效的数量！")
                return
            
            if ProductionOrderService.add_order(product_id, plan_qty, date_var.get(), responsible_var.get()):
                messagebox.showinfo("成功", "新增订单成功！")
                self.load_orders()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增订单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_order(self):
        """编辑订单"""
        if not self.selected_order_id:
            messagebox.showwarning("提示", "请先选择订单！")
            return
        
        order = ProductionOrderService.get_order_by_id(self.selected_order_id)
        if not order:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑生产订单")
        dialog.geometry("400x350")
        
        products = ProductService.get_all_products()
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        
        ttk.Label(dialog, text="选择产品:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        product_combobox = ttk.Combobox(dialog, values=product_names, state="readonly", width=30)
        product_combobox.grid(row=0, column=1, padx=20)
        
        # 设置默认值
        for i, p in enumerate(products):
            if p[0] == order[2]:
                product_combobox.current(i)
                break
        
        ttk.Label(dialog, text="计划数量:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        qty_var = tk.StringVar(value=str(order[4]))
        ttk.Entry(dialog, textvariable=qty_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="计划日期:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=str(order[5]))
        ttk.Entry(dialog, textvariable=date_var, width=33).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="状态:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['待生产', '生产中', '已完成', '已取消'], state="readonly", width=27)
        status_combobox.grid(row=3, column=1, padx=20)
        status_combobox.current(order[6] - 1)
        
        ttk.Label(dialog, text="负责人:").grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        responsible_var = tk.StringVar(value=order[7])
        ttk.Entry(dialog, textvariable=responsible_var, width=33).grid(row=4, column=1, padx=20)

        def save():
            idx = product_combobox.current()
            product_id = products[idx][0]
            try:
                plan_qty = int(qty_var.get())
            except ValueError:
                messagebox.showwarning("提示", "请输入有效的数量！")
                return
            
            status = status_combobox.current() + 1
            if ProductionOrderService.update_order(self.selected_order_id, product_id, plan_qty, 
                                                  date_var.get(), status, responsible_var.get(), order[8]):
                messagebox.showinfo("成功", "修改订单成功！")
                self.load_orders()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改订单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_order(self):
        """删除订单"""
        if not self.selected_order_id:
            messagebox.showwarning("提示", "请先选择订单！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该订单吗？"):
            if ProductionOrderService.delete_order(self.selected_order_id):
                messagebox.showinfo("成功", "删除订单成功！")
                self.load_orders()
                self.selected_order_id = None
            else:
                messagebox.showerror("错误", "删除订单失败！")

    def setup_requisition_tab(self):
        """生产领料标签页"""
        frame = self.tab_requisition
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增领料", command=self.add_requisition).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ 审批领料", command=self.approve_requisition).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_requisitions).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("req_no", "production_order", "requester", "req_date", "status")
        self.requisition_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.requisition_tree.heading("req_no", text="领料单号")
        self.requisition_tree.heading("production_order", text="生产订单")
        self.requisition_tree.heading("requester", text="领料人")
        self.requisition_tree.heading("req_date", text="领料日期")
        self.requisition_tree.heading("status", text="状态")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.requisition_tree.yview)
        self.requisition_tree.configure(yscrollcommand=scrollbar.set)
        
        self.requisition_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.requisition_tree.bind('<<TreeviewSelect>>', self.on_requisition_select)
        self.selected_requisition_id = None
        
        self.load_requisitions()

    def load_requisitions(self):
        """加载领料单"""
        for item in self.requisition_tree.get_children():
            self.requisition_tree.delete(item)
        
        requisitions = MaterialRequisitionService.get_all_requisitions()
        status_map = {1: '待审批', 2: '已审批', 3: '已作废'}
        if requisitions:
            for req in requisitions:
                status_text = status_map.get(req[5], '未知')
                self.requisition_tree.insert("", tk.END, values=(
                    req[1], req[2], req[3], req[4], status_text
                ))

    def on_requisition_select(self, event):
        """选择领料单"""
        selection = self.requisition_tree.selection()
        if selection:
            item = self.requisition_tree.item(selection[0])
            req_no = item['values'][0]
            reqs = MaterialRequisitionService.get_all_requisitions()
            for req in reqs:
                if req[1] == req_no:
                    self.selected_requisition_id = req[0]
                    break

    def add_requisition(self):
        """新增领料单"""
        orders = ProductionOrderService.get_all_orders()
        if not orders:
            messagebox.showwarning("提示", "没有可用生产订单！")
            return
        
        parts = PartsService.get_all_products()
        if not parts:
            messagebox.showwarning("提示", "没有可用零部件！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增生产领料")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="选择生产订单:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        order_names = [f"{o[1]} - {o[2]}" for o in orders]
        order_combobox = ttk.Combobox(dialog, values=order_names, state="readonly", width=40)
        order_combobox.grid(row=0, column=1, padx=20)
        order_combobox.current(0)
        
        ttk.Label(dialog, text="领料人:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        requester_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=requester_var, width=43).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="领料日期:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=43).grid(row=2, column=1, padx=20)

        # 零部件选择区域
        part_frame = ttk.Frame(dialog)
        part_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(part_frame, text="零部件:").pack(side=tk.LEFT)
        part_names = [f"{p[1]} - {p[2]}" for p in parts]
        part_combobox = ttk.Combobox(part_frame, values=part_names, state="readonly", width=20)
        part_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(part_frame, text="数量:").pack(side=tk.LEFT)
        qty_entry = ttk.Entry(part_frame, width=10)
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        add_part_btn = ttk.Button(part_frame, text="添加", command=lambda: self.add_part_to_list(part_combobox, qty_entry, part_listbox, parts))
        add_part_btn.pack(side=tk.LEFT, padx=5)
        
        part_listbox = tk.Listbox(dialog, width=60, height=5)
        part_listbox.grid(row=4, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_parts = []

        def save():
            if not self.selected_parts:
                messagebox.showwarning("提示", "请添加至少一个零部件！")
                return
            
            idx = order_combobox.current()
            order_id = orders[idx][0]
            
            if MaterialRequisitionService.add_requisition(order_id, requester_var.get(), date_var.get(), self.selected_parts):
                messagebox.showinfo("成功", "新增领料单成功！")
                self.load_requisitions()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增领料单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_part_to_list(self, part_combobox, qty_entry, listbox, parts):
        """添加零部件到列表"""
        idx = part_combobox.current()
        if idx < 0:
            return
        
        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                messagebox.showwarning("提示", "数量必须大于0！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数量！")
            return
        
        part = parts[idx]
        part_info = {
            'part_id': part[0],
            'part_name': part[2],
            'quantity': qty,
            'unit': part[7]
        }
        
        self.selected_parts.append(part_info)
        listbox.insert(tk.END, f"{part[2]} x {qty} {part[7]}")
        qty_entry.delete(0, tk.END)

    def approve_requisition(self):
        """审批领料单"""
        if not self.selected_requisition_id:
            messagebox.showwarning("提示", "请先选择领料单！")
            return
        
        if messagebox.askyesno("确认", "确定要审批该领料单吗？"):
            if MaterialRequisitionService.approve_requisition(self.selected_requisition_id):
                messagebox.showinfo("成功", "审批成功！")
                self.load_requisitions()
            else:
                messagebox.showerror("错误", "审批失败！")

    def setup_stock_in_tab(self):
        """生产入库标签页"""
        frame = self.tab_stock_in
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增入库", command=self.add_stock_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ 审批入库", command=self.approve_stock_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_stock_in).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("in_no", "production_order", "in_date", "status")
        self.stock_in_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.stock_in_tree.heading("in_no", text="入库单号")
        self.stock_in_tree.heading("production_order", text="生产订单")
        self.stock_in_tree.heading("in_date", text="入库日期")
        self.stock_in_tree.heading("status", text="状态")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stock_in_tree.yview)
        self.stock_in_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_in_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.stock_in_tree.bind('<<TreeviewSelect>>', self.on_stock_in_select)
        self.selected_stock_in_id = None
        
        self.load_stock_in()

    def load_stock_in(self):
        """加载入库单"""
        for item in self.stock_in_tree.get_children():
            self.stock_in_tree.delete(item)
        
        stock_in_list = ProductionStockInService.get_all_stock_in()
        status_map = {1: '草稿', 2: '待审批', 3: '已审批', 4: '已作废'}
        if stock_in_list:
            for si in stock_in_list:
                status_text = status_map.get(si[5], '未知')
                self.stock_in_tree.insert("", tk.END, values=(
                    si[1], si[2], si[3], status_text
                ))

    def on_stock_in_select(self, event):
        """选择入库单"""
        selection = self.stock_in_tree.selection()
        if selection:
            item = self.stock_in_tree.item(selection[0])
            in_no = item['values'][0]
            stock_in_list = ProductionStockInService.get_all_stock_in()
            for si in stock_in_list:
                if si[1] == in_no:
                    self.selected_stock_in_id = si[0]
                    break

    def add_stock_in(self):
        """新增入库单"""
        orders = ProductionOrderService.get_all_orders()
        if not orders:
            messagebox.showwarning("提示", "没有可用生产订单！")
            return
        
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增生产入库")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="选择生产订单:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        order_names = [f"{o[1]} - {o[2]}" for o in orders]
        order_combobox = ttk.Combobox(dialog, values=order_names, state="readonly", width=40)
        order_combobox.grid(row=0, column=1, padx=20)
        order_combobox.current(0)
        
        ttk.Label(dialog, text="入库日期:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=43).grid(row=1, column=1, padx=20)

        product_frame = ttk.Frame(dialog)
        product_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(product_frame, text="产品:").pack(side=tk.LEFT)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(product_frame, values=product_names, state="readonly", width=20)
        product_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="SN码:").pack(side=tk.LEFT)
        sn_entry = ttk.Entry(product_frame, width=15)
        sn_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="数量:").pack(side=tk.LEFT)
        qty_entry = ttk.Entry(product_frame, width=8)
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(product_frame, text="添加", command=lambda: self.add_product_to_list(product_combobox, sn_entry, qty_entry, product_listbox, products))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        product_listbox = tk.Listbox(dialog, width=60, height=5)
        product_listbox.grid(row=3, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_products = []

        def save():
            if not self.selected_products:
                messagebox.showwarning("提示", "请添加至少一个产品！")
                return
            
            idx = order_combobox.current()
            order_id = orders[idx][0]
            
            if ProductionStockInService.add_stock_in(order_id, date_var.get(), self.selected_products):
                messagebox.showinfo("成功", "新增入库单成功！")
                self.load_stock_in()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增入库单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_product_to_list(self, product_combobox, sn_entry, qty_entry, listbox, products):
        """添加产品到列表"""
        idx = product_combobox.current()
        if idx < 0:
            return
        
        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                messagebox.showwarning("提示", "数量必须大于0！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数量！")
            return
        
        product = products[idx]
        product_info = {
            'product_id': product[0],
            'product_name': product[2],
            'sn': sn_entry.get(),
            'card_no': '',
            'quantity': qty
        }
        
        self.selected_products.append(product_info)
        listbox.insert(tk.END, f"{product[2]} x {qty} (SN: {sn_entry.get()})")
        sn_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)

    def approve_stock_in(self):
        """审批入库单"""
        if not self.selected_stock_in_id:
            messagebox.showwarning("提示", "请先选择入库单！")
            return
        
        if messagebox.askyesno("确认", "确定要审批该入库单吗？"):
            if ProductionStockInService.approve_stock_in(self.selected_stock_in_id):
                messagebox.showinfo("成功", "审批成功！")
                self.load_stock_in()
            else:
                messagebox.showerror("错误", "审批失败！")

    def setup_scrap_tab(self):
        """生产报废标签页"""
        frame = self.tab_scrap
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增报废", command=self.add_scrap).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ 审批报废", command=self.approve_scrap).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_scraps).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("scrap_no", "source_type", "product_name", "quantity", "reason", "responsible", "status")
        self.scrap_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.scrap_tree.heading("scrap_no", text="报废单号")
        self.scrap_tree.heading("source_type", text="来源")
        self.scrap_tree.heading("product_name", text="产品名称")
        self.scrap_tree.heading("quantity", text="数量")
        self.scrap_tree.heading("reason", text="报废原因")
        self.scrap_tree.heading("responsible", text="责任人")
        self.scrap_tree.heading("status", text="状态")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.scrap_tree.yview)
        self.scrap_tree.configure(yscrollcommand=scrollbar.set)
        
        self.scrap_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.scrap_tree.bind('<<TreeviewSelect>>', self.on_scrap_select)
        self.selected_scrap_id = None
        
        self.load_scraps()

    def load_scraps(self):
        """加载报废记录"""
        for item in self.scrap_tree.get_children():
            self.scrap_tree.delete(item)
        
        scraps = ProductionScrapService.get_all_scraps()
        source_map = {1: '生产报废', 2: '维修报废'}
        status_map = {1: '待审批', 2: '已审批'}
        if scraps:
            for scrap in scraps:
                source_text = source_map.get(scrap[2], '未知')
                status_text = status_map.get(scrap[8], '未知')
                self.scrap_tree.insert("", tk.END, values=(
                    scrap[1], source_text, scrap[4], scrap[5], scrap[6], scrap[7], status_text
                ))

    def on_scrap_select(self, event):
        """选择报废记录"""
        selection = self.scrap_tree.selection()
        if selection:
            item = self.scrap_tree.item(selection[0])
            scrap_no = item['values'][0]
            scraps = ProductionScrapService.get_all_scraps()
            for scrap in scraps:
                if scrap[1] == scrap_no:
                    self.selected_scrap_id = scrap[0]
                    break

    def add_scrap(self):
        """新增报废记录"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增报废记录")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="来源类型:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        source_combobox = ttk.Combobox(dialog, values=['生产报废', '维修报废'], state="readonly", width=27)
        source_combobox.grid(row=0, column=1, padx=20)
        source_combobox.current(0)
        
        ttk.Label(dialog, text="选择产品:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(dialog, values=product_names, state="readonly", width=27)
        product_combobox.grid(row=1, column=1, padx=20)
        product_combobox.current(0)
        
        ttk.Label(dialog, text="报废数量:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        qty_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=qty_var, width=30).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="报废原因:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        reason_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=reason_var, width=30).grid(row=3, column=1, padx=20)
        
        ttk.Label(dialog, text="责任人:").grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        responsible_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=responsible_var, width=30).grid(row=4, column=1, padx=20)

        def save():
            source_type = source_combobox.current() + 1
            idx = product_combobox.current()
            product = products[idx]
            
            try:
                quantity = int(qty_var.get())
                if quantity <= 0:
                    messagebox.showwarning("提示", "数量必须大于0！")
                    return
            except ValueError:
                messagebox.showwarning("提示", "请输入有效数量！")
                return
            
            if ProductionScrapService.add_scrap(source_type, None, product[0], product[2], 
                                                quantity, reason_var.get(), responsible_var.get()):
                messagebox.showinfo("成功", "新增报废记录成功！")
                self.load_scraps()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增报废记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def approve_scrap(self):
        """审批报废记录"""
        if not self.selected_scrap_id:
            messagebox.showwarning("提示", "请先选择报废记录！")
            return
        
        if messagebox.askyesno("确认", "确定要审批该报废记录吗？"):
            if ProductionScrapService.approve_scrap(self.selected_scrap_id):
                messagebox.showinfo("成功", "审批成功！")
                self.load_scraps()
            else:
                messagebox.showerror("错误", "审批失败！")
