# 维修管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.maintenance_service import (
    MaintenanceRecordService, MaintenanceSubRecordService,
    MaintenancePartsService, MaintenanceStatisticsService
)
from services.product_service import ProductService
from datetime import datetime

class MaintenanceView:
    """维修管理界面类"""

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

        title_label = ttk.Label(main_frame, text="🔧 维修管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_record = ttk.Frame(tab_control)
        self.tab_statistics = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_record, text='📋 维修记录')
        tab_control.add(self.tab_statistics, text='📊 维修统计')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_record_tab()
        self.setup_statistics_tab()

    def setup_record_tab(self):
        """维修记录标签页"""
        frame = self.tab_record
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        # 左侧维修记录列表
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 新增维修", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑维修", command=self.edit_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_records).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("record_no", "device_sn", "product_name", "fault_desc", "priority", "status", "assignee")
        self.record_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.record_tree.heading("record_no", text="维修单号")
        self.record_tree.heading("device_sn", text="设备SN")
        self.record_tree.heading("product_name", text="产品名称")
        self.record_tree.heading("fault_desc", text="故障描述")
        self.record_tree.heading("priority", text="优先级")
        self.record_tree.heading("status", text="状态")
        self.record_tree.heading("assignee", text="负责人")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.record_tree.yview)
        self.record_tree.configure(yscrollcommand=scrollbar.set)
        
        self.record_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.record_tree.bind('<<TreeviewSelect>>', self.on_record_select)
        self.selected_record_id = None
        
        self.load_records()

        # 右侧详情面板
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(4, weight=1)

        # 维修子记录
        sub_frame = ttk.LabelFrame(right_frame, text="维修进度")
        sub_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        sub_frame.columnconfigure(0, weight=1)
        sub_frame.rowconfigure(1, weight=1)
        
        ttk.Button(sub_frame, text="➕ 添加进度", command=self.add_sub_record).pack(side=tk.LEFT, padx=5)
        
        self.sub_tree = ttk.Treeview(sub_frame, columns=("sub_record_no", "repair_content", "repair_time", "operator"), show="headings")
        self.sub_tree.heading("sub_record_no", text="子单号")
        self.sub_tree.heading("repair_content", text="维修内容")
        self.sub_tree.heading("repair_time", text="维修时间")
        self.sub_tree.heading("operator", text="操作员")
        self.sub_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 维修配件
        parts_frame = ttk.LabelFrame(right_frame, text="维修配件")
        parts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        parts_frame.columnconfigure(0, weight=1)
        parts_frame.rowconfigure(1, weight=1)
        
        ttk.Button(parts_frame, text="➕ 添加配件", command=self.add_parts).pack(side=tk.LEFT, padx=5)
        
        self.parts_tree = ttk.Treeview(parts_frame, columns=("part_name", "quantity", "price", "amount"), show="headings")
        self.parts_tree.heading("part_name", text="配件名称")
        self.parts_tree.heading("quantity", text="数量")
        self.parts_tree.heading("price", text="单价")
        self.parts_tree.heading("amount", text="金额")
        self.parts_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 状态操作
        action_frame = ttk.LabelFrame(right_frame, text="状态操作")
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(action_frame, text="▶️ 开始维修", command=lambda: self.update_record_status(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✅ 完成维修", command=lambda: self.update_record_status(3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔒 取消维修", command=lambda: self.update_record_status(4)).pack(side=tk.LEFT, padx=5)

        # 维修费用
        cost_frame = ttk.LabelFrame(right_frame, text="维修费用")
        cost_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(cost_frame, text="维修成本:").pack(side=tk.LEFT, padx=5)
        self.cost_var = tk.StringVar(value="0.00")
        ttk.Entry(cost_frame, textvariable=self.cost_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(cost_frame, text="保存费用", command=self.save_cost).pack(side=tk.LEFT, padx=5)

    def load_records(self):
        """加载维修记录"""
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        records = MaintenanceRecordService.get_all_records()
        if records:
            for record in records:
                status_text = MaintenanceRecordService.get_status_text(record[6])
                priority_text = MaintenanceRecordService.get_priority_text(record[5])
                self.record_tree.insert("", tk.END, values=(
                    record[1], record[2], record[3], record[4], priority_text, status_text, record[8]
                ))

    def on_record_select(self, event):
        """选择维修记录"""
        selection = self.record_tree.selection()
        if selection:
            item = self.record_tree.item(selection[0])
            record_no = item['values'][0]
            records = MaintenanceRecordService.get_all_records()
            for record in records:
                if record[1] == record_no:
                    self.selected_record_id = record[0]
                    self.load_sub_records(record[0])
                    self.load_parts(record[0])
                    self.cost_var.set(str(record[9]) if record[9] else "0.00")
                    break

    def load_sub_records(self, record_id):
        """加载子记录"""
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
        
        sub_records = MaintenanceSubRecordService.get_sub_records_by_main(record_id)
        if sub_records:
            for sub in sub_records:
                self.sub_tree.insert("", tk.END, values=(sub[1], sub[2], sub[3], sub[4]))

    def load_parts(self, record_id):
        """加载配件"""
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
        
        parts = MaintenancePartsService.get_parts_by_record(record_id)
        if parts:
            for part in parts:
                self.parts_tree.insert("", tk.END, values=(part[2], part[3], part[4], part[5]))

    def add_record(self):
        """新增维修记录"""
        products = ProductService.get_all_products()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("新增维修记录")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="设备SN:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        sn_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=sn_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="故障描述:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        fault_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=fault_var, width=30).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="优先级:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        priority_combobox = ttk.Combobox(dialog, values=['紧急', '一般', '低'], state="readonly", width=27)
        priority_combobox.grid(row=2, column=1, padx=20)
        priority_combobox.current(1)
        
        ttk.Label(dialog, text="负责人:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        assignee_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=assignee_var, width=30).grid(row=3, column=1, padx=20)

        def save():
            priority = priority_combobox.current() + 1
            
            if MaintenanceRecordService.add_record(sn_var.get(), None, fault_var.get(), priority, 
                                                 None, assignee_var.get()):
                messagebox.showinfo("成功", "新增维修记录成功！")
                self.load_records()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "新增维修记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_record(self):
        """编辑维修记录"""
        if not self.selected_record_id:
            messagebox.showwarning("提示", "请先选择维修记录！")
            return
        
        record = MaintenanceRecordService.get_record_by_id(self.selected_record_id)
        if not record:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑维修记录")
        dialog.geometry("400x400")
        
        ttk.Label(dialog, text="故障描述:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        fault_var = tk.StringVar(value=record[4])
        ttk.Entry(dialog, textvariable=fault_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="优先级:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        priority_combobox = ttk.Combobox(dialog, values=['紧急', '一般', '低'], state="readonly", width=27)
        priority_combobox.grid(row=1, column=1, padx=20)
        priority_combobox.current(record[5] - 1)
        
        ttk.Label(dialog, text="状态:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['待维修', '维修中', '已完成', '已取消'], state="readonly", width=27)
        status_combobox.grid(row=2, column=1, padx=20)
        status_combobox.current(record[6] - 1)
        
        ttk.Label(dialog, text="负责人:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        assignee_var = tk.StringVar(value=record[8])
        ttk.Entry(dialog, textvariable=assignee_var, width=30).grid(row=3, column=1, padx=20)
        
        ttk.Label(dialog, text="维修费用:").grid(row=4, column=0, sticky=tk.W, padx=20, pady=10)
        cost_var = tk.StringVar(value=str(record[9]) if record[9] else "0.00")
        ttk.Entry(dialog, textvariable=cost_var, width=30).grid(row=4, column=1, padx=20)

        def save():
            priority = priority_combobox.current() + 1
            status = status_combobox.current() + 1
            
            if MaintenanceRecordService.update_record(self.selected_record_id, fault_var.get(), 
                                                   status, priority, assignee_var.get(), 
                                                   float(cost_var.get()) if cost_var.get() else 0, record[10]):
                messagebox.showinfo("成功", "修改维修记录成功！")
                self.load_records()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改维修记录失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_sub_record(self):
        """添加维修子记录"""
        if not self.selected_record_id:
            messagebox.showwarning("提示", "请先选择维修记录！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加维修进度")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="维修内容:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        content_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=content_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="操作员:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        operator_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=operator_var, width=33).grid(row=1, column=1, padx=20)

        def save():
            if MaintenanceSubRecordService.add_sub_record(self.selected_record_id, 
                                                       content_var.get(), None, operator_var.get()):
                messagebox.showinfo("成功", "添加维修进度成功！")
                self.load_sub_records(self.selected_record_id)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加维修进度失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_parts(self):
        """添加维修配件"""
        if not self.selected_record_id:
            messagebox.showwarning("提示", "请先选择维修记录！")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加维修配件")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="配件名称:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="数量:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        qty_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=qty_var, width=30).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="单价:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        price_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=price_var, width=30).grid(row=2, column=1, padx=20)

        def save():
            try:
                qty = int(qty_var.get())
                price = float(price_var.get())
                if qty <= 0 or price < 0:
                    messagebox.showwarning("提示", "数量必须大于0，单价不能为负！")
                    return
            except ValueError:
                messagebox.showwarning("提示", "请输入有效数字！")
                return
            
            parts = [{
                'part_id': None,
                'part_name': name_var.get(),
                'quantity': qty,
                'price': price,
                'amount': qty * price,
                'remark': ''
            }]
            
            if MaintenancePartsService.add_parts(self.selected_record_id, parts):
                messagebox.showinfo("成功", "添加配件成功！")
                self.load_parts(self.selected_record_id)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加配件失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_record_status(self, status):
        """更新维修记录状态"""
        if not self.selected_record_id:
            messagebox.showwarning("提示", "请先选择维修记录！")
            return
        
        if MaintenanceRecordService.update_status(self.selected_record_id, status):
            messagebox.showinfo("成功", "状态更新成功！")
            self.load_records()
        else:
            messagebox.showerror("错误", "状态更新失败！")

    def save_cost(self):
        """保存维修费用"""
        if not self.selected_record_id:
            messagebox.showwarning("提示", "请先选择维修记录！")
            return
        
        try:
            cost = float(self.cost_var.get())
        except ValueError:
            messagebox.showwarning("提示", "请输入有效金额！")
            return
        
        record = MaintenanceRecordService.get_record_by_id(self.selected_record_id)
        if MaintenanceRecordService.update_record(self.selected_record_id, record[4], record[6], 
                                               record[5], record[8], cost, record[10]):
            messagebox.showinfo("成功", "费用保存成功！")
        else:
            messagebox.showerror("错误", "费用保存失败！")

    def setup_statistics_tab(self):
        """维修统计标签页"""
        frame = self.tab_statistics
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # 统计卡片
        stats_frame = ttk.Frame(frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        now = datetime.now()
        monthly_stats = MaintenanceStatisticsService.get_monthly_statistics(now.year, now.month)[0]
        fault_stats = MaintenanceStatisticsService.get_fault_type_statistics()
        
        card1 = ttk.LabelFrame(stats_frame, text="本月维修")
        card1.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(card1, text=str(monthly_stats[0]), font=("Microsoft YaHei", 20, "bold")).pack(pady=10)
        
        card2 = ttk.LabelFrame(stats_frame, text="本月完成")
        card2.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(card2, text=str(monthly_stats[1]), font=("Microsoft YaHei", 20, "bold")).pack(pady=10)
        
        card3 = ttk.LabelFrame(stats_frame, text="平均费用")
        card3.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        avg_cost = monthly_stats[2] if monthly_stats[2] else 0
        ttk.Label(card3, text=f"¥{avg_cost:.2f}", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)
        
        card4 = ttk.LabelFrame(stats_frame, text="总费用")
        card4.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        total_cost = monthly_stats[3] if monthly_stats[3] else 0
        ttk.Label(card4, text=f"¥{total_cost:.2f}", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

        # 故障类型统计
        fault_frame = ttk.LabelFrame(frame, text="故障类型分布")
        fault_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        if fault_stats:
            for fault_type, count in fault_stats:
                ttk.Label(fault_frame, text=f"{fault_type}...: {count}次").pack(anchor=tk.W, padx=10, pady=2)
