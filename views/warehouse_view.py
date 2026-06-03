# 仓库管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.warehouse_service import (
    WarehouseStockInService, WarehouseStockOutService,
    WarehouseStockFlowService, WarehouseInventoryService,
    InventoryQueryService
)
from services.product_service import ProductService
from datetime import datetime

class WarehouseView:
    """仓库管理界面类"""

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

        title_label = ttk.Label(main_frame, text="📦 仓库管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_stock_in = ttk.Frame(tab_control)
        self.tab_stock_out = ttk.Frame(tab_control)
        self.tab_flow = ttk.Frame(tab_control)
        self.tab_inventory = ttk.Frame(tab_control)
        self.tab_query = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_stock_in, text='📥 入库管理')
        tab_control.add(self.tab_stock_out, text='📤 出库管理')
        tab_control.add(self.tab_flow, text='📊 库存流水')
        tab_control.add(self.tab_inventory, text='✅ 库存盘点')
        tab_control.add(self.tab_query, text='🔍 库存查询')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_stock_in_tab()
        self.setup_stock_out_tab()
        self.setup_flow_tab()
        self.setup_inventory_tab()
        self.setup_query_tab()
#图形界面
    def setup_stock_in_tab(self):
        """入库管理标签页"""
        frame = self.tab_stock_in
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增入库", command=self.add_stock_in, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除入库", command=self.delete_stock_in, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_stock_in, width=12).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("order_no", "in_type", "source_no", "handler", "status", "remark")
        self.stock_in_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.stock_in_tree.heading("order_no", text="入库单号")
        self.stock_in_tree.heading("in_type", text="入库类型")
        self.stock_in_tree.heading("source_no", text="来源单号")
        self.stock_in_tree.heading("handler", text="经办人")
        self.stock_in_tree.heading("status", text="状态")
        self.stock_in_tree.heading("remark", text="备注")

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
        
        stock_in_list = WarehouseStockInService.get_all_stock_in()
        type_map = {1: '采购入库', 2: '退货入库', 3: '其他'}
        status_map = {1: '待处理', 2: '已完成'}
        if stock_in_list:
            for si in stock_in_list:
                type_text = type_map.get(si[2], '其他')
                status_text = status_map.get(si[7], '未知')
                self.stock_in_tree.insert("", tk.END, values=(
                    si[1], type_text, si[3], si[4], status_text, si[8]
                ))

    def on_stock_in_select(self, event):
        """选择入库单"""
        selection = self.stock_in_tree.selection()
        if selection:
            item = self.stock_in_tree.item(selection[0])
            in_no = item['values'][0]
            stock_in_list = WarehouseStockInService.get_all_stock_in()
            for si in stock_in_list:
                if si[1] == in_no:
                    self.selected_stock_in_id = si[0]
                    break

    def delete_stock_in(self):
        """删除入库单"""
        if not self.selected_stock_in_id:
            messagebox.showwarning("提示", "请先选择要删除的入库单！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该入库单吗？\n删除后将恢复库存！"):
            if WarehouseStockInService.delete_stock_in(self.selected_stock_in_id):
                messagebox.showinfo("成功", "删除入库单成功！")
                self.load_stock_in()
                self.selected_stock_in_id = None
            else:
                messagebox.showerror("错误", "删除入库单失败！\n只有待处理的入库单可以删除。")

    def add_stock_in(self):
        """新增入库单"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增仓库入库")
        dialog.geometry("500x500")
        
        ttk.Label(dialog, text="入库类型:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        in_type_combobox = ttk.Combobox(dialog, values=["采购入库", "退货入库", "其他"], state="readonly", width=20)
        in_type_combobox.current(0)
        in_type_combobox.grid(row=0, column=1, padx=20, sticky=tk.W)
        
        ttk.Label(dialog, text="来源单号:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        source_no_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=source_no_var, width=43).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="经办人:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        handler_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=handler_var, width=43).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="仓库:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        warehouse_var = tk.StringVar(value="主仓库")
        ttk.Entry(dialog, textvariable=warehouse_var, width=43).grid(row=3, column=1, padx=20)
        
        ttk.Label(dialog, text="库位:").grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        location_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=location_var, width=43).grid(row=4, column=1, padx=20)

        product_frame = ttk.Frame(dialog)
        product_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(product_frame, text="产品:").pack(side=tk.LEFT)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(product_frame, values=product_names, state="readonly", width=20)
        product_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="数量:").pack(side=tk.LEFT)
        qty_entry = ttk.Entry(product_frame, width=8)
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="单价:").pack(side=tk.LEFT)
        price_entry = ttk.Entry(product_frame, width=10)
        price_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(product_frame, text="添加", command=lambda: self.add_stock_in_product(product_combobox, qty_entry, price_entry, product_listbox, products))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        product_listbox = tk.Listbox(dialog, width=60, height=5)
        product_listbox.grid(row=6, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_stock_in_products = []

        def save():
            if not self.selected_stock_in_products:
                messagebox.showwarning("提示", "请添加至少一个产品！")
                return
            
            in_type = in_type_combobox.current() + 1
            if WarehouseStockInService.add_stock_in(in_type, source_no_var.get(), 
                                                   handler_var.get(), warehouse_var.get(),
                                                   location_var.get(), self.selected_stock_in_products,
                                                   remark_var.get()):
                messagebox.showinfo("成功", "新增入库单成功！")
                self.load_stock_in()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增入库单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_stock_in_product(self, product_combobox, qty_entry, price_entry, listbox, products):
        """添加产品到入库列表"""
        idx = product_combobox.current()
        if idx < 0:
            return
        
        try:
            qty = int(qty_entry.get())
            price = float(price_entry.get())
            if qty <= 0 or price < 0:
                messagebox.showwarning("提示", "数量必须大于0，单价不能为负！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数字！")
            return
        
        product = products[idx]
        amount = qty * price
        product_info = {
            'product_id': product[0],
            'product_name': product[2],
            'quantity': qty,
            'unit': product[7],
            'price': price,
            'amount': amount
        }
        
        self.selected_stock_in_products.append(product_info)
        listbox.insert(tk.END, f"{product[2]} x {qty} @ {price:.2f} = {amount:.2f}")
        qty_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)

    def setup_stock_out_tab(self):
        """出库管理标签页"""
        frame = self.tab_stock_out
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增出库", command=self.add_stock_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_stock_out).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("order_no", "out_type", "source_no", "handler", "status", "remark")
        self.stock_out_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.stock_out_tree.heading("order_no", text="出库单号")
        self.stock_out_tree.heading("out_type", text="出库类型")
        self.stock_out_tree.heading("source_no", text="来源单号")
        self.stock_out_tree.heading("handler", text="经办人")
        self.stock_out_tree.heading("status", text="状态")
        self.stock_out_tree.heading("remark", text="备注")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stock_out_tree.yview)
        self.stock_out_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_out_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.load_stock_out()

    def load_stock_out(self):
        """加载出库单"""
        for item in self.stock_out_tree.get_children():
            self.stock_out_tree.delete(item)
        
        stock_out_list = WarehouseStockOutService.get_all_stock_out()
        type_map = {1: '销售出库', 2: '安装领料', 3: '维修领料', 4: '其他出库'}
        status_map = {1: '待处理', 2: '已完成'}
        if stock_out_list:
            for so in stock_out_list:
                type_text = type_map.get(so[2], '其他')
                status_text = status_map.get(so[6], '未知')
                self.stock_out_tree.insert("", tk.END, values=(
                    so[1], type_text, so[3], so[4], status_text, so[7]
                ))

    def add_stock_out(self):
        """新增出库单"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增仓库出库")
        dialog.geometry("500x480")
        
        ttk.Label(dialog, text="出库类型:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        out_type_combobox = ttk.Combobox(dialog, values=['销售出库', '安装领料', '维修领料', '其他出库'], state="readonly", width=30)
        out_type_combobox.grid(row=0, column=1, padx=20)
        out_type_combobox.current(0)
        
        ttk.Label(dialog, text="来源单号:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        source_no_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=source_no_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="经办人:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        handler_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=handler_var, width=33).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="仓库:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        warehouse_var = tk.StringVar(value="主仓库")
        ttk.Entry(dialog, textvariable=warehouse_var, width=33).grid(row=3, column=1, padx=20)

        product_frame = ttk.Frame(dialog)
        product_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(product_frame, text="产品:").pack(side=tk.LEFT)
        product_names = [f"{p[1]} - {p[2]} (库存:{p[6]})" for p in products]
        product_combobox = ttk.Combobox(product_frame, values=product_names, state="readonly", width=25)
        product_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="数量:").pack(side=tk.LEFT)
        qty_entry = ttk.Entry(product_frame, width=8)
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(product_frame, text="添加", command=lambda: self.add_stock_out_product(product_combobox, qty_entry, product_listbox, products))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        product_listbox = tk.Listbox(dialog, width=60, height=5)
        product_listbox.grid(row=5, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_stock_out_products = []

        def save():
            if not self.selected_stock_out_products:
                messagebox.showwarning("提示", "请添加至少一个产品！")
                return
            
            out_type = out_type_combobox.current() + 1
            
            if WarehouseStockOutService.add_stock_out(out_type, source_no_var.get(),
                                                    handler_var.get(), warehouse_var.get(),
                                                    self.selected_stock_out_products):
                messagebox.showinfo("成功", "新增出库单成功！")
                self.load_stock_out()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增出库单失败！库存不足或数据错误！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_stock_out_product(self, product_combobox, qty_entry, listbox, products):
        """添加产品到出库列表"""
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
        if product[6] < qty:
            messagebox.showwarning("提示", "库存不足！")
            return
        
        product_info = {
            'product_id': product[0],
            'product_name': product[2],
            'quantity': qty,
            'unit': product[7],
            'price': product[6],
            'amount': qty * product[6]
        }
        
        self.selected_stock_out_products.append(product_info)
        listbox.insert(tk.END, f"{product[2]} x {qty}")
        qty_entry.delete(0, tk.END)

    def setup_flow_tab(self):
        """库存流水标签页"""
        frame = self.tab_flow
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_flows).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("product_name", "change_qty", "unit", "balance_qty", "reason", "source_doc", "created_at")
        self.flow_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.flow_tree.heading("product_name", text="产品名称")
        self.flow_tree.heading("change_qty", text="变动数量")
        self.flow_tree.heading("unit", text="单位")
        self.flow_tree.heading("balance_qty", text="结存数量")
        self.flow_tree.heading("reason", text="变动原因")
        self.flow_tree.heading("source_doc", text="来源单据")
        self.flow_tree.heading("created_at", text="变动时间")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.flow_tree.yview)
        self.flow_tree.configure(yscrollcommand=scrollbar.set)
        
        self.flow_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.load_flows()

    def load_flows(self):
        """加载库存流水"""
        for item in self.flow_tree.get_children():
            self.flow_tree.delete(item)
        
        flows = WarehouseStockFlowService.get_all_flows()
        type_map = {1: '入库', 2: '出库', 3: '盘盈', 4: '盘亏'}
        if flows:
            for flow in flows:
                type_text = type_map.get(flow[1], '其他')
                self.flow_tree.insert("", tk.END, values=(
                    flow[3], f"{type_text}{flow[4]}", '件', flow[6], flow[7], flow[8], flow[9]
                ))

    def setup_inventory_tab(self):
        """库存盘点标签页"""
        frame = self.tab_inventory
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增盘点", command=self.add_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ 审批盘点", command=self.approve_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_inventories).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("inventory_no", "inventory_date", "status", "operator")
        self.inventory_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.inventory_tree.heading("inventory_no", text="盘点单号")
        self.inventory_tree.heading("inventory_date", text="盘点日期")
        self.inventory_tree.heading("status", text="状态")
        self.inventory_tree.heading("operator", text="操作员")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.inventory_tree.bind('<<TreeviewSelect>>', self.on_inventory_select)
        self.selected_inventory_id = None
        
        self.load_inventories()

    def load_inventories(self):
        """加载盘点记录"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        inventories = WarehouseInventoryService.get_all_inventories()
        status_map = {1: '待审批', 2: '已完成'}
        if inventories:
            for inv in inventories:
                status_text = status_map.get(inv[4], '未知')
                self.inventory_tree.insert("", tk.END, values=(
                    inv[1], inv[3], status_text, ''
                ))

    def on_inventory_select(self, event):
        """选择盘点记录"""
        selection = self.inventory_tree.selection()
        if selection:
            item = self.inventory_tree.item(selection[0])
            inventory_no = item['values'][0]
            inventories = WarehouseInventoryService.get_all_inventories()
            for inv in inventories:
                if inv[1] == inventory_no:
                    self.selected_inventory_id = inv[0]
                    break

    def add_inventory(self):
        """新增盘点记录"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增库存盘点")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="盘点日期:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(dialog, textvariable=date_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="操作员:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        operator_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=operator_var, width=33).grid(row=1, column=1, padx=20)

        product_frame = ttk.Frame(dialog)
        product_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10)
        
        ttk.Label(product_frame, text="产品:").pack(side=tk.LEFT)
        product_names = [f"{p[1]} - {p[2]} (系统:{p[6]})" for p in products]
        product_combobox = ttk.Combobox(product_frame, values=product_names, state="readonly", width=25)
        product_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(product_frame, text="实际数量:").pack(side=tk.LEFT)
        actual_entry = ttk.Entry(product_frame, width=8)
        actual_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(product_frame, text="添加", command=lambda: self.add_inventory_product(product_combobox, actual_entry, product_listbox, products))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        product_listbox = tk.Listbox(dialog, width=60, height=5)
        product_listbox.grid(row=3, column=0, columnspan=2, padx=20, pady=5)
        
        self.selected_inventory_products = []

        def save():
            if not self.selected_inventory_products:
                messagebox.showwarning("提示", "请添加至少一个产品！")
                return
            
            if WarehouseInventoryService.add_inventory(date_var.get(), 
                                                     self.selected_inventory_products, 
                                                     operator_var.get()):
                messagebox.showinfo("成功", "新增盘点记录成功！")
                self.load_inventories()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增盘点记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_inventory_product(self, product_combobox, actual_entry, listbox, products):
        """添加产品到盘点列表"""
        idx = product_combobox.current()
        if idx < 0:
            return
        
        try:
            actual_qty = int(actual_entry.get())
            if actual_qty < 0:
                messagebox.showwarning("提示", "数量不能为负！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效数量！")
            return
        
        product = products[idx]
        system_qty = product[6]
        diff_qty = actual_qty - system_qty
        reason = f"盘盈{abs(diff_qty)}" if diff_qty > 0 else (f"盘亏{abs(diff_qty)}" if diff_qty < 0 else "相符")
        
        product_info = {
            'product_id': product[0],
            'product_name': product[2],
            'system_qty': system_qty,
            'actual_qty': actual_qty,
            'diff_qty': diff_qty,
            'reason': reason
        }
        
        self.selected_inventory_products.append(product_info)
        listbox.insert(tk.END, f"{product[2]} 系统:{system_qty} 实际:{actual_qty} ({reason})")
        actual_entry.delete(0, tk.END)

    def approve_inventory(self):
        """审批盘点"""
        if not self.selected_inventory_id:
            messagebox.showwarning("提示", "请先选择盘点记录！")
            return
        
        if messagebox.askyesno("确认", "确定要审批该盘点记录并调整库存吗？"):
            if WarehouseInventoryService.approve_inventory(self.selected_inventory_id):
                messagebox.showinfo("成功", "审批成功！库存已调整！")
                self.load_inventories()
            else:
                messagebox.showerror("错误", "审批失败！")

    def setup_query_tab(self):
        """库存查询标签页"""
        frame = self.tab_query
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚠️ 低库存警告", command=self.show_low_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💰 库存价值", command=self.show_stock_value).pack(side=tk.LEFT, padx=5)

        # 搜索框
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_inventory).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("product_code", "name", "model", "category_name", "spec", "stock", "unit", "price", "supplier")
        self.query_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.query_tree.heading("product_code", text="商品编码")
        self.query_tree.heading("name", text="商品名称")
        self.query_tree.heading("model", text="型号")
        self.query_tree.heading("category_name", text="分类")
        self.query_tree.heading("spec", text="规格")
        self.query_tree.heading("stock", text="库存数量")
        self.query_tree.heading("unit", text="单位")
        self.query_tree.heading("price", text="单价")
        self.query_tree.heading("supplier", text="供应商")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.query_tree.yview)
        self.query_tree.configure(yscrollcommand=scrollbar.set)
        
        self.query_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.load_inventory()

    def load_inventory(self):
        """加载库存"""
        for item in self.query_tree.get_children():
            self.query_tree.delete(item)
        
        inventory = InventoryQueryService.get_all_inventory()
        if inventory:
            for item in inventory:
                self.query_tree.insert("", tk.END, values=(
                    item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]
                ))

    def search_inventory(self):
        """搜索库存"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.load_inventory()
            return
        
        inventory = InventoryQueryService.get_all_inventory()
        filtered = [item for item in inventory if keyword.lower() in str(item[1]).lower() or 
                    keyword.lower() in str(item[2]).lower()]
        
        for item in self.query_tree.get_children():
            self.query_tree.delete(item)
        
        if filtered:
            for item in filtered:
                self.query_tree.insert("", tk.END, values=(
                    item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]
                ))

    def show_low_stock(self):
        """显示低库存产品"""
        low_stock = InventoryQueryService.get_low_stock_products()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("低库存警告")
        dialog.geometry("600x300")
        
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("product_code", "name", "model", "stock", "unit")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        tree.heading("product_code", text="商品编码")
        tree.heading("name", text="商品名称")
        tree.heading("model", text="型号")
        tree.heading("stock", text="库存数量")
        tree.heading("unit", text="单位")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if low_stock:
            for item in low_stock:
                tree.insert("", tk.END, values=(item[1], item[2], item[3], item[4], item[5]))
        else:
            messagebox.showinfo("提示", "没有低库存产品！")
            dialog.destroy()

    def show_stock_value(self):
        """显示库存价值"""
        value = InventoryQueryService.get_stock_value()
        messagebox.showinfo("库存总价值", f"当前库存总价值为：¥ {value:,.2f}")
