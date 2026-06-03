# 售后管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.after_sales_service import (
    AfterSalesWorkOrderService, ProblemItemService,
    ProcessingRecordService, AfterSalesDeviceService
)
from services.product_service import ProductService
from datetime import datetime

class AfterSalesView:
    """售后管理界面类"""

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

        title_label = ttk.Label(main_frame, text="🛠️ 售后管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_work_order = ttk.Frame(tab_control)
        self.tab_device = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_work_order, text='📋 售后工单')
        tab_control.add(self.tab_device, text='📱 售后设备')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_work_order_tab()
        self.setup_device_tab()

    def setup_work_order_tab(self):
        """售后工单标签页"""
        frame = self.tab_work_order
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(1, weight=1)

        # 左侧工单列表
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增工单", command=self.add_work_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_work_orders).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("order_no", "customer_name", "product_name", "problem_type", "status", "priority", "assignee")
        self.work_order_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.work_order_tree.heading("order_no", text="工单号")
        self.work_order_tree.heading("customer_name", text="客户")
        self.work_order_tree.heading("product_name", text="产品")
        self.work_order_tree.heading("problem_type", text="问题类型")
        self.work_order_tree.heading("status", text="状态")
        self.work_order_tree.heading("priority", text="优先级")
        self.work_order_tree.heading("assignee", text="负责人")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.work_order_tree.yview)
        self.work_order_tree.configure(yscrollcommand=scrollbar.set)
        
        self.work_order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.work_order_tree.bind('<<TreeviewSelect>>', self.on_work_order_select)
        self.selected_work_order_id = None
        
        self.load_work_orders()

        # 右侧详情面板
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(3, weight=1)

        # 问题项
        problem_frame = ttk.LabelFrame(right_frame, text="问题项")
        problem_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        problem_frame.columnconfigure(0, weight=1)
        problem_frame.rowconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(problem_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(btn_frame, text="➕ 添加问题", command=self.add_problem_item).pack(side=tk.LEFT, padx=5)
        
        self.problem_tree = ttk.Treeview(problem_frame, columns=("problem_desc", "status", "solution"), show="headings")
        self.problem_tree.heading("problem_desc", text="问题描述")
        self.problem_tree.heading("status", text="状态")
        self.problem_tree.heading("solution", text="解决方案")
        self.problem_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.problem_tree.bind('<<TreeviewSelect>>', self.on_problem_select)
        self.selected_problem_id = None

        # 处理记录
        record_frame = ttk.LabelFrame(right_frame, text="处理记录")
        record_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        record_frame.columnconfigure(0, weight=1)
        record_frame.rowconfigure(2, weight=1)
        
        ttk.Button(record_frame, text="➕ 添加记录", command=self.add_processing_record).pack(side=tk.LEFT, padx=5)
        
        self.record_tree = ttk.Treeview(record_frame, columns=("process_time", "operator", "process_content"), show="headings")
        self.record_tree.heading("process_time", text="处理时间")
        self.record_tree.heading("operator", text="操作员")
        self.record_tree.heading("process_content", text="处理内容")
        self.record_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 工单操作
        action_frame = ttk.LabelFrame(right_frame, text="工单操作")
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(action_frame, text="▶️ 开始处理", command=lambda: self.update_order_status(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✅ 完成工单", command=lambda: self.update_order_status(3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔒 关闭工单", command=lambda: self.update_order_status(4)).pack(side=tk.LEFT, padx=5)

    def load_work_orders(self):
        """加载工单列表"""
        for item in self.work_order_tree.get_children():
            self.work_order_tree.delete(item)
        
        orders = AfterSalesWorkOrderService.get_all_work_orders()
        if orders:
            for order in orders:
                status_text = AfterSalesWorkOrderService.get_status_text(order[6])
                priority_text = AfterSalesWorkOrderService.get_priority_text(order[7])
                self.work_order_tree.insert("", tk.END, values=(
                    order[1], order[2], order[4], order[5], status_text, priority_text, order[9]
                ))

    def on_work_order_select(self, event):
        """选择工单"""
        selection = self.work_order_tree.selection()
        if selection:
            item = self.work_order_tree.item(selection[0])
            order_no = item['values'][0]
            orders = AfterSalesWorkOrderService.get_all_work_orders()
            for order in orders:
                if order[1] == order_no:
                    self.selected_work_order_id = order[0]
                    self.load_problem_items(order[0])
                    self.load_processing_records(order[0])
                    break

    def load_problem_items(self, order_id):
        """加载问题项"""
        for item in self.problem_tree.get_children():
            self.problem_tree.delete(item)
        
        problems = ProblemItemService.get_problem_items_by_order(order_id)
        status_map = {1: '待处理', 2: '处理中', 3: '已解决'}
        if problems:
            for problem in problems:
                status_text = status_map.get(problem[3], '未知')
                self.problem_tree.insert("", tk.END, values=(problem[1], status_text, problem[4]))

    def load_processing_records(self, order_id):
        """加载处理记录"""
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        records = ProcessingRecordService.get_records_by_order(order_id)
        if records:
            for record in records:
                self.record_tree.insert("", tk.END, values=(record[1], record[3], record[2]))

    def on_problem_select(self, event):
        """选择问题项"""
        selection = self.problem_tree.selection()
        if selection:
            pass

    def add_work_order(self):
        """新增工单"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增售后工单")
        dialog.geometry("400x400")
        
        ttk.Label(dialog, text="问题类型:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        problem_types = ['设备故障', '安装问题', '软件问题', '其他']
        problem_combobox = ttk.Combobox(dialog, values=problem_types, state="readonly", width=27)
        problem_combobox.grid(row=0, column=1, padx=20)
        problem_combobox.current(0)
        
        ttk.Label(dialog, text="优先级:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        priority_combobox = ttk.Combobox(dialog, values=['紧急', '一般', '低'], state="readonly", width=27)
        priority_combobox.grid(row=1, column=1, padx=20)
        priority_combobox.current(1)
        
        ttk.Label(dialog, text="报告时间:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        time_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        ttk.Entry(dialog, textvariable=time_var, width=30).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="负责人:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        assignee_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=assignee_var, width=30).grid(row=3, column=1, padx=20)
        
        ttk.Label(dialog, text="备注:").grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        remark_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=remark_var, width=30).grid(row=4, column=1, padx=20)

        def save():
            problem_type = problem_combobox.get()
            priority = priority_combobox.current() + 1
            
            if AfterSalesWorkOrderService.add_work_order(None, None, None, problem_type, 
                                                       time_var.get(), priority, assignee_var.get(), remark_var.get()):
                messagebox.showinfo("成功", "新增工单成功！")
                self.load_work_orders()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增工单失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_problem_item(self):
        """添加问题项"""
        if not self.selected_work_order_id:
            messagebox.showwarning("提示", "请先选择工单！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加问题项")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="问题描述:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="问题代码:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        code_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=code_var, width=30).grid(row=1, column=1, padx=20)

        def save():
            if ProblemItemService.add_problem_item(self.selected_work_order_id, desc_var.get(), code_var.get()):
                messagebox.showinfo("成功", "添加问题项成功！")
                self.load_problem_items(self.selected_work_order_id)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加问题项失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_processing_record(self):
        """添加处理记录"""
        if not self.selected_work_order_id:
            messagebox.showwarning("提示", "请先选择工单！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加处理记录")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="操作员:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        operator_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=operator_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="处理内容:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        content_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=content_var, width=30).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="下一步动作:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        next_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=next_var, width=30).grid(row=2, column=1, padx=20)

        def save():
            if ProcessingRecordService.add_record(self.selected_work_order_id, 
                                                content_var.get(), operator_var.get(), next_var.get()):
                messagebox.showinfo("成功", "添加处理记录成功！")
                self.load_processing_records(self.selected_work_order_id)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加处理记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_order_status(self, status):
        """更新工单状态"""
        if not self.selected_work_order_id:
            messagebox.showwarning("提示", "请先选择工单！")
            return
        
        if AfterSalesWorkOrderService.update_status(self.selected_work_order_id, status):
            messagebox.showinfo("成功", "状态更新成功！")
            self.load_work_orders()
        else:
            messagebox.showerror("错误", "状态更新失败！")

    def setup_device_tab(self):
        """售后设备标签页"""
        frame = self.tab_device
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增设备", command=self.add_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑设备", command=self.edit_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除设备", command=self.delete_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_devices).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("sn", "product_name", "status", "location", "install_date", "last_maintain_date")
        self.device_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.device_tree.heading("sn", text="设备SN")
        self.device_tree.heading("product_name", text="产品名称")
        self.device_tree.heading("status", text="状态")
        self.device_tree.heading("location", text="位置")
        self.device_tree.heading("install_date", text="安装日期")
        self.device_tree.heading("last_maintain_date", text="最后维护日期")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        self.device_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.device_tree.bind('<<TreeviewSelect>>', self.on_device_select)
        self.selected_device_id = None
        
        self.load_devices()

    def load_devices(self):
        """加载设备列表"""
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        devices = AfterSalesDeviceService.get_all_devices()
        status_map = {1: '正常', 2: '维修中', 3: '已报废'}
        if devices:
            for device in devices:
                status_text = status_map.get(device[3], '未知')
                self.device_tree.insert("", tk.END, values=(
                    device[1], device[2], status_text, device[4], device[5], device[6]
                ))

    def on_device_select(self, event):
        """选择设备"""
        selection = self.device_tree.selection()
        if selection:
            item = self.device_tree.item(selection[0])
            sn = item['values'][0]
            devices = AfterSalesDeviceService.get_all_devices()
            for device in devices:
                if device[1] == sn:
                    self.selected_device_id = device[0]
                    break

    def add_device(self):
        """新增设备"""
        products = ProductService.get_all_products()
        if not products:
            messagebox.showwarning("提示", "没有可用产品！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增售后设备")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="设备SN:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        sn_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=sn_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="选择产品:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        product_names = [f"{p[1]} - {p[2]}" for p in products]
        product_combobox = ttk.Combobox(dialog, values=product_names, state="readonly", width=27)
        product_combobox.grid(row=1, column=1, padx=20)
        product_combobox.current(0)
        
        ttk.Label(dialog, text="状态:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['正常', '维修中', '已报废'], state="readonly", width=27)
        status_combobox.grid(row=2, column=1, padx=20)
        status_combobox.current(0)
        
        ttk.Label(dialog, text="安装位置:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        location_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=location_var, width=30).grid(row=3, column=1, padx=20)

        def save():
            idx = product_combobox.current()
            product = products[idx]
            status = status_combobox.current() + 1
            
            if AfterSalesDeviceService.add_device(sn_var.get(), product[0], product[2], 
                                                status, location_var.get()):
                messagebox.showinfo("成功", "新增设备成功！")
                self.load_devices()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增设备失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_device(self):
        """编辑设备"""
        if not self.selected_device_id:
            messagebox.showwarning("提示", "请先选择设备！")
            return
        
        devices = AfterSalesDeviceService.get_all_devices()
        device = None
        for d in devices:
            if d[0] == self.selected_device_id:
                device = d
                break
        
        if not device:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑售后设备")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="状态:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['正常', '维修中', '已报废'], state="readonly", width=27)
        status_combobox.grid(row=0, column=1, padx=20)
        status_combobox.current(device[3] - 1)
        
        ttk.Label(dialog, text="安装位置:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        location_var = tk.StringVar(value=device[4])
        ttk.Entry(dialog, textvariable=location_var, width=30).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="最后维护日期:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        date_var = tk.StringVar(value=device[6] if device[6] else "")
        ttk.Entry(dialog, textvariable=date_var, width=30).grid(row=2, column=1, padx=20)

        def save():
            status = status_combobox.current() + 1
            
            if AfterSalesDeviceService.update_device(self.selected_device_id, status, 
                                                  location_var.get(), date_var.get(), ""):
                messagebox.showinfo("成功", "修改设备成功！")
                self.load_devices()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改设备失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_device(self):
        """删除设备"""
        if not self.selected_device_id:
            messagebox.showwarning("提示", "请先选择设备！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该设备吗？"):
            if AfterSalesDeviceService.delete_device(self.selected_device_id):
                messagebox.showinfo("成功", "删除设备成功！")
                self.load_devices()
                self.selected_device_id = None
            else:
                messagebox.showerror("错误", "删除设备失败！")
