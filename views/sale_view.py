# 销售管理界面
# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.sale_service import SaleService
from services.product_service import ProductService

class SaleView:
    """销售管理界面类"""

    def __init__(self, parent):
        self.parent = parent
        # 设置父容器配置
        self.parent.pack(fill=tk.BOTH, expand=True)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        self.selected_sale_id = None
        self.selected_product_id = None
        
        self.setup_ui()
        self.refresh_sales()
        self.refresh_products()

    def setup_ui(self):
        """设置界面布局"""
        
        # 主框架
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="📋 销售管理", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        # 搜索和统计区
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="🔍 搜索:").grid(row=0, column=0, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_sales())

        ttk.Button(search_frame, text="搜索", command=self.search_sales).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(search_frame, text="刷新", command=self.refresh_sales).grid(row=0, column=3)

        # 统计信息
        self.stats_label = ttk.Label(main_frame, text="", font=("Microsoft YaHei", 10))
        self.stats_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

        # 表格区
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        columns = ("sale_no", "product_name", "quantity", "unit_price", "total_price", "customer", "sale_date", "remark")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("sale_no", text="销售单号")
        self.tree.heading("product_name", text="商品名称")
        self.tree.heading("quantity", text="数量")
        self.tree.heading("unit_price", text="单价")
        self.tree.heading("total_price", text="总金额")
        self.tree.heading("customer", text="客户")
        self.tree.heading("sale_date", text="销售时间")
        self.tree.heading("remark", text="备注")

        self.tree.column("sale_no", width=120)
        self.tree.column("product_name", width=150)
        self.tree.column("quantity", width=60)
        self.tree.column("unit_price", width=80)
        self.tree.column("total_price", width=90)
        self.tree.column("customer", width=100)
        self.tree.column("sale_date", width=150)
        self.tree.column("remark", width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # 按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(15, 0))

        ttk.Button(button_frame, text="➕ 添加销售", command=self.add_sale_dialog, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除销售", command=self.delete_sale, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="📊 销售统计", command=self.show_sales_stats, width=15).grid(row=0, column=2, padx=5)

    def refresh_sales(self):
        """刷新销售列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sales = SaleService.get_all_sales()
        if sales:
            for sale in sales:
                self.tree.insert("", tk.END, values=(
                    sale[1], sale[3], sale[4], f"¥{sale[5]:.2f}", f"¥{sale[6]:.2f}", 
                    sale[7], sale[8], sale[9]
                ))
        
        count = SaleService.get_sale_count()
        self.stats_label.config(text=f"📊 销售记录总数: {count} 条")

    def refresh_products(self):
        """刷新商品列表"""
        self.products = ProductService.get_all_products()

    def search_sales(self):
        """搜索销售记录"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_sales()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sales = SaleService.search_sales(keyword)
        if sales:
            for sale in sales:
                self.tree.insert("", tk.END, values=(
                    sale[1], sale[3], sale[4], f"¥{sale[5]:.2f}", f"¥{sale[6]:.2f}", 
                    sale[7], sale[8], sale[9]
                ))

    def on_select(self, event):
        """选择销售记录"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            sale_no = item['values'][0]
            
            # 通过销售单号查找ID
            sales = SaleService.get_all_sales()
            for sale in sales:
                if sale[1] == sale_no:
                    self.selected_sale_id = sale[0]
                    break

    def add_sale_dialog(self):
        """添加销售对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加销售")
        dialog.geometry("450x450")
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="选择商品:", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky=tk.W, pady=(20, 5), padx=20)
        
        product_names = [f"{p[1]} - {p[2]} (库存:{p[5]})" for p in self.products] if self.products else []
        self.product_combobox = ttk.Combobox(dialog, values=product_names, state="readonly", width=40)
        self.product_combobox.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20)
        if product_names:
            self.product_combobox.current(0)
        
        ttk.Label(dialog, text="销售数量:", font=("Microsoft YaHei", 10)).grid(row=2, column=0, sticky=tk.W, pady=(15, 5), padx=20)
        quantity_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=quantity_var, width=43).grid(row=3, column=0, sticky=(tk.W, tk.E), padx=20)

        ttk.Label(dialog, text="客户:", font=("Microsoft YaHei", 10)).grid(row=4, column=0, sticky=tk.W, pady=(15, 5), padx=20)
        customer_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=customer_var, width=43).grid(row=5, column=0, sticky=(tk.W, tk.E), padx=20)

        ttk.Label(dialog, text="备注:", font=("Microsoft YaHei", 10)).grid(row=6, column=0, sticky=tk.W, pady=(15, 5), padx=20)
        remark_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=remark_var, width=43).grid(row=7, column=0, sticky=(tk.W, tk.E), padx=20)

        def save():
            if not product_names:
                messagebox.showwarning("提示", "没有可选商品！")
                return
                
            idx = self.product_combobox.current()
            if idx < 0:
                messagebox.showwarning("提示", "请选择商品！")
                return
                
            product = self.products[idx]
            product_id = product[0]
            product_name = product[2]
            unit_price = product[4]
            stock = product[5]
            
            try:
                quantity = int(quantity_var.get().strip())
                if quantity <= 0:
                    messagebox.showwarning("提示", "数量必须大于0！")
                    return
                if quantity > stock:
                    messagebox.showwarning("提示", f"库存不足！当前库存: {stock}")
                    return
            except ValueError:
                messagebox.showwarning("提示", "请输入有效的数量！")
                return
            
            customer = customer_var.get().strip()
            remark = remark_var.get().strip()

            if SaleService.add_sale(product_id, product_name, quantity, unit_price, customer, remark):
                messagebox.showinfo("成功", "添加销售成功！")
                self.refresh_sales()
                self.refresh_products()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加销售失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=8, column=0, pady=(25, 0))
        
        ttk.Button(button_frame, text="保存", command=save, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=12).grid(row=0, column=1, padx=5)

    def delete_sale(self):
        """删除销售"""
        if not self.selected_sale_id:
            messagebox.showwarning("提示", "请先选择要删除的销售记录！")
            return
        
        if not messagebox.askyesno("确认", "确定要删除这条销售记录吗？\n删除后库存将自动恢复。"):
            return
        
        if SaleService.delete_sale(self.selected_sale_id):
            messagebox.showinfo("成功", "删除销售记录成功！")
            self.selected_sale_id = None
            self.refresh_sales()
            self.refresh_products()
        else:
            messagebox.showerror("错误", "删除销售记录失败！")

    def show_sales_stats(self):
        """显示销售统计"""
        stats_dialog = tk.Toplevel(self.parent)
        stats_dialog.title("销售统计")
        stats_dialog.geometry("500x400")
        stats_dialog.transient(self.parent)
        stats_dialog.grab_set()

        ttk.Label(stats_dialog, text="📊 销售统计", font=("Microsoft YaHei", 14, "bold")).grid(row=0, column=0, pady=(20, 15), padx=20)

        sales = SaleService.get_all_sales()
        if not sales:
            ttk.Label(stats_dialog, text="暂无销售记录").grid(row=1, column=0, pady=20, padx=20)
            return

        total_sales = len(sales)
        total_amount = sum(s[6] for s in sales)
        total_quantity = sum(s[4] for s in sales)

        stats_text = f"""
📈 总体统计
─────────────────
销售记录数: {total_sales} 条
销售总数量: {total_quantity} 件
销售总金额: ¥{total_amount:.2f}
        """

        ttk.Label(stats_dialog, text=stats_text, justify=tk.LEFT, font=("Microsoft YaHei", 11)).grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)

        # 商品销售排名
        from collections import defaultdict
        product_sales = defaultdict(lambda: {'quantity': 0, 'amount': 0})
        for sale in sales:
            name = sale[3]
            product_sales[name]['quantity'] += sale[4]
            product_sales[name]['amount'] += sale[6]

        sorted_products = sorted(product_sales.items(), key=lambda x: x[1]['amount'], reverse=True)
        
        rank_text = "\n🏆 热销商品 TOP 5\n─────────────────\n"
        for i, (name, data) in enumerate(sorted_products[:5], 1):
            rank_text += f"{i}. {name}: {data['quantity']}件 (¥{data['amount']:.2f})\n"

        ttk.Label(stats_dialog, text=rank_text, justify=tk.LEFT, font=("Microsoft YaHei", 10)).grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)

        ttk.Button(stats_dialog, text="关闭", command=stats_dialog.destroy, width=15).grid(row=3, column=0, pady=20)
