# 商品管理界面
# 使用Tkinter编写的图形界面

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.product_service import ProductService

class ProductView:
    """商品管理界面类"""

    def __init__(self, parent):
        self.parent = parent
        self.service = ProductService()
        # 设置父容器配置
        self.parent.pack(fill=tk.BOTH, expand=True)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """设置界面"""
        # 标题
        title_frame = tk.Frame(self.parent, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="📦 商品管理",
            font=("Microsoft YaHei", 20, "bold"),
            fg="white",
            bg='#2c3e50'
        ).pack(pady=15)

        # 搜索栏
        search_frame = tk.Frame(self.parent, pady=10)
        search_frame.pack(fill=tk.X, padx=10)

        tk.Label(search_frame, text="搜索:", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Microsoft YaHei", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 搜索", command=self.search_products, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔄 重置", command=self.load_products, width=10).pack(side=tk.LEFT, padx=5)

        # 表格区域
        table_frame = tk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 定义列
        columns = ("ID", "商品编码", "名称", "型号", "类别", "规格", "价格", "库存", "单位", "供应商")

        # 创建表格
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # 设置列
        self.tree.heading("ID", text="ID")
        self.tree.heading("商品编码", text="商品编码")
        self.tree.heading("名称", text="名称")
        self.tree.heading("型号", text="型号")
        self.tree.heading("类别", text="类别")
        self.tree.heading("规格", text="规格")
        self.tree.heading("价格", text="价格")
        self.tree.heading("库存", text="库存")
        self.tree.heading("单位", text="单位")
        self.tree.heading("供应商", text="供应商")

        # 设置列宽
        self.tree.column("ID", width=50, anchor='center')
        self.tree.column("商品编码", width=100, anchor='center')
        self.tree.column("名称", width=120, anchor='center')
        self.tree.column("型号", width=100, anchor='center')
        self.tree.column("类别", width=80, anchor='center')
        self.tree.column("规格", width=100, anchor='center')
        self.tree.column("价格", width=80, anchor='center')
        self.tree.column("库存", width=80, anchor='center')
        self.tree.column("单位", width=60, anchor='center')
        self.tree.column("供应商", width=120, anchor='center')

        # 添加滚动条
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选中事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # 按钮区域
        btn_frame = tk.Frame(self.parent, pady=10)
        btn_frame.pack(fill=tk.X, padx=10)

        tk.Button(btn_frame, text="➕ 添加商品", command=self.add_product, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ 修改商品", command=self.edit_product, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ 删除商品", command=self.delete_product, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 低库存警告", command=self.show_low_stock, width=12).pack(side=tk.LEFT, padx=5)

        # 统计信息
        self.stats_label = tk.Label(btn_frame, text="", font=("Microsoft YaHei", 10), fg='#7f8c8d')
        self.stats_label.pack(side=tk.RIGHT, padx=10)

        self.selected_id = None

    def load_products(self):
        """加载商品列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = self.service.get_all_products()
        if products:
            for product in products:
                self.tree.insert('', tk.END, values=product)

        self.update_stats()
        self.search_entry.delete(0, tk.END)

    def search_products(self):
        """搜索商品"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_products()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        products = self.service.search_products(keyword)
        if products:
            for product in products:
                self.tree.insert('', tk.END, values=product)

        self.update_stats()

    def on_select(self, event):
        """选中表格行"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]

    def add_product(self):
        """添加商品"""
        self.open_product_dialog("添加商品", None)

    def edit_product(self):
        """修改商品"""
        if not self.selected_id:
            messagebox.showwarning("提示", "请先选择要修改的商品")
            return
        self.open_product_dialog("修改商品", self.selected_id)

    def delete_product(self):
        """删除商品"""
        if not self.selected_id:
            messagebox.showwarning("提示", "请先选择要删除的商品")
            return

        if messagebox.askyesno("确认", "确定要删除这件商品吗？"):
            if self.service.delete_product(self.selected_id):
                messagebox.showinfo("成功", "商品删除成功")
                self.load_products()
            else:
                messagebox.showerror("错误", "商品删除失败")

    def show_low_stock(self):
        """显示低库存商品"""
        low_stock_window = tk.Toplevel(self.parent)
        low_stock_window.title("低库存警告")
        low_stock_window.geometry("500x300")

        tk.Label(low_stock_window, text="⚠️ 库存低于10件的商品", font=("Microsoft YaHei", 14, "bold")).pack(pady=10)

        products = self.service.get_low_stock_products(10)

        if not products:
            tk.Label(low_stock_window, text="✅ 所有商品库存充足", font=("Microsoft YaHei", 12)).pack(pady=50)
            return

        for product in products:
            tk.Label(
                low_stock_window,
                text=f"❌ {product[2]} (编码:{product[1]}) - 库存: {product[3]}件",
                font=("Microsoft YaHei", 11),
                fg='#e74c3c'
            ).pack(pady=5)

    def open_product_dialog(self, title, product_id):
        """打开商品编辑对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("500x600")
        dialog.resizable(False, False)

        # 设置为模态窗口
        dialog.transient(self.parent)
        dialog.grab_set()

        # 商品信息
        fields = {}
        labels = ["商品编码:", "名称:", "型号:", "类别:", "规格:", "价格:", "库存:", "单位:", "供应商:", "描述:"]

        for i, label in enumerate(labels):
            tk.Label(dialog, text=label, font=("Microsoft YaHei", 11), width=10, anchor='w').grid(row=i, column=0, padx=10, pady=6)

            if label == "描述:":
                fields['description'] = tk.Text(dialog, width=35, height=4, font=("Microsoft YaHei", 11))
                fields['description'].grid(row=i, column=1, padx=10, pady=6)
            else:
                entry = tk.Entry(dialog, width=38, font=("Microsoft YaHei", 11))
                entry.grid(row=i, column=1, padx=10, pady=6)
                field_key = label.replace(":", "").strip()
                fields[field_key] = entry

        # 如果是修改，加载商品信息
        if product_id:
            product = self.service.get_product_by_id(product_id)
            if product:
                fields['商品编码'].insert(0, product[1])
                fields['名称'].insert(0, product[2])
                fields['型号'].insert(0, product[3] or "")
                fields['类别'].insert(0, product[4] or "")
                fields['规格'].insert(0, product[5] or "")
                fields['价格'].insert(0, product[6])
                fields['库存'].insert(0, product[7])
                fields['单位'].insert(0, product[8])
                fields['供应商'].insert(0, product[9] or "")
                fields['description'].insert('1.0', product[10] or "")

        # 按钮
        def save():
            try:
                product_code = fields['商品编码'].get().strip()
                name = fields['名称'].get().strip()
                model = fields['型号'].get().strip()
                category_id = int(fields['类别'].get().strip()) if fields['类别'].get().strip() else None
                spec = fields['规格'].get().strip()
                price = float(fields['价格'].get().strip())
                stock = int(fields['库存'].get().strip())
                unit = fields['单位'].get().strip()
                supplier = fields['供应商'].get().strip()
                description = fields['description'].get('1.0', tk.END).strip()

                if not product_code or not name:
                    messagebox.showwarning("提示", "商品编码和名称不能为空")
                    return

                if product_id:
                    success = self.service.update_product(product_id, product_code, name, model, category_id, spec, price, stock, unit, supplier, description)
                    msg = "商品更新成功"
                else:
                    success = self.service.add_product(product_code, name, model, category_id, spec, price, stock, unit, supplier, description)
                    msg = "商品添加成功"

                if success:
                    messagebox.showinfo("成功", msg)
                    dialog.destroy()
                    self.load_products()
                else:
                    messagebox.showerror("错误", "保存失败")

            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

        tk.Button(dialog, text="💾 保存", command=save, width=12, bg='#27ae60', fg='white', font=("Microsoft YaHei", 11)).grid(row=8, column=0, columnspan=2, pady=20)

    def update_stats(self):
        """更新统计信息"""
        count = self.service.get_product_count()
        self.stats_label.config(text=f"商品总数: {count}")


def main():
    """主函数"""
    root = tk.Tk()
    root.title("ERP系统 - 商品管理")
    root.geometry("900x600")

    app = ProductView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
