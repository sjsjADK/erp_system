# 使用Tkinter创建图形用户界面

import tkinter as tk
from tkinter import ttk, messagebox
from services.system_service import (
    SystemConfigService, OperationLogService, UserService, RoleService
)

class SystemView:
    """系统配置界面类"""

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

        title_label = ttk.Label(main_frame, text="⚙️ 系统配置", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        tab_control = ttk.Notebook(main_frame)
        
        self.tab_config = ttk.Frame(tab_control)
        self.tab_logs = ttk.Frame(tab_control)
        self.tab_users = ttk.Frame(tab_control)
        self.tab_roles = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_config, text='⚙️ 系统配置')
        tab_control.add(self.tab_logs, text='📝 操作日志')
        tab_control.add(self.tab_users, text='👥 用户管理')
        tab_control.add(self.tab_roles, text='🎭 角色管理')
        
        tab_control.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_config_tab()
        self.setup_logs_tab()
        self.setup_users_tab()
        self.setup_roles_tab()

    def setup_config_tab(self):
        """系统配置标签页"""
        frame = self.tab_config
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 添加配置", command=self.add_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑配置", command=self.edit_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除配置", command=self.delete_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_configs).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("key", "value", "description")
        self.config_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.config_tree.heading("key", text="配置键")
        self.config_tree.heading("value", text="配置值")
        self.config_tree.heading("description", text="描述")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=scrollbar.set)
        
        self.config_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.config_tree.bind('<<TreeviewSelect>>', self.on_config_select)
        self.selected_config_key = None
        
        self.load_configs()

    def load_configs(self):
        """加载配置"""
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        configs = SystemConfigService.get_all_configs()
        if configs:
            for config in configs:
                self.config_tree.insert("", tk.END, values=(config[0], config[1], config[2]))

    def on_config_select(self, event):
        """选择配置"""
        selection = self.config_tree.selection()
        if selection:
            item = self.config_tree.item(selection[0])
            self.selected_config_key = item['values'][0]

    def add_config(self):
        """添加配置"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加系统配置")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="配置键:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        key_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=key_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="配置值:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        value_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=value_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=33).grid(row=2, column=1, padx=20)

        def save():
            if not key_var.get().strip():
                messagebox.showwarning("提示", "请输入配置键！")
                return
            
            if SystemConfigService.set_config(key_var.get(), value_var.get(), desc_var.get()):
                messagebox.showinfo("成功", "添加配置成功！")
                self.load_configs()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加配置失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_config(self):
        """编辑配置"""
        if not self.selected_config_key:
            messagebox.showwarning("提示", "请先选择配置！")
            return
        
        configs = SystemConfigService.get_all_configs()
        config = None
        for c in configs:
            if c[0] == self.selected_config_key:
                config = c
                break
        
        if not config:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑系统配置")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="配置键:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        ttk.Label(dialog, text=self.selected_config_key).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="配置值:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        value_var = tk.StringVar(value=config[1])
        ttk.Entry(dialog, textvariable=value_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        desc_var = tk.StringVar(value=config[2])
        ttk.Entry(dialog, textvariable=desc_var, width=33).grid(row=2, column=1, padx=20)

        def save():
            if SystemConfigService.set_config(self.selected_config_key, value_var.get(), desc_var.get()):
                messagebox.showinfo("成功", "修改配置成功！")
                self.load_configs()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改配置失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_config(self):
        """删除配置"""
        if not self.selected_config_key:
            messagebox.showwarning("提示", "请先选择配置！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该配置吗？"):
            if SystemConfigService.delete_config(self.selected_config_key):
                messagebox.showinfo("成功", "删除配置成功！")
                self.load_configs()
                self.selected_config_key = None
            else:
                messagebox.showerror("错误", "删除配置失败！")

    def setup_logs_tab(self):
        """操作日志标签页"""
        frame = self.tab_logs
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_logs).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("module", "operation", "description", "operator", "operation_time", "ip_address")
        self.logs_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.logs_tree.heading("module", text="模块")
        self.logs_tree.heading("operation", text="操作")
        self.logs_tree.heading("description", text="描述")
        self.logs_tree.heading("operator", text="操作员")
        self.logs_tree.heading("operation_time", text="操作时间")
        self.logs_tree.heading("ip_address", text="IP地址")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.logs_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.load_logs()

    def load_logs(self):
        """加载操作日志"""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        logs = OperationLogService.get_all_logs()
        if logs:
            for log in logs:
                self.logs_tree.insert("", tk.END, values=(log[1], log[2], log[3], log[4], log[5], log[6]))

    def setup_users_tab(self):
        """用户管理标签页"""
        frame = self.tab_users
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 添加用户", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑用户", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除用户", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_users).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("id", "username", "real_name", "role_name", "status", "created_at")
        self.users_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("username", text="用户名")
        self.users_tree.heading("real_name", text="真实姓名")
        self.users_tree.heading("role_name", text="角色")
        self.users_tree.heading("status", text="状态")
        self.users_tree.heading("created_at", text="创建时间")
        self.users_tree.column("id", width=0, stretch=tk.NO)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        self.selected_user_id = None
        
        self.load_users()

    def load_users(self):
        """加载用户"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = UserService.get_all_users()
        status_map = {1: '启用', 0: '禁用'}
        if users:
            for user in users:
                status_text = status_map.get(user[4], '未知')
                self.users_tree.insert("", tk.END, values=(user[0], user[1], user[2], user[3], status_text, user[5]))

    def on_user_select(self, event):
        """选择用户"""
        selection = self.users_tree.selection()
        if selection:
            item = self.users_tree.item(selection[0])
            values = item['values']
            if values and len(values) > 0:
                self.selected_user_id = values[0]

    def add_user(self):
        """添加用户"""
        roles = RoleService.get_all_roles()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加用户")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="用户名:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="密码:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="*", width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="真实姓名:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        real_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=real_name_var, width=33).grid(row=2, column=1, padx=20)
        
        ttk.Label(dialog, text="角色:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        role_names = [r[1] for r in roles]
        role_combobox = ttk.Combobox(dialog, values=role_names, state="readonly", width=27)
        role_combobox.grid(row=3, column=1, padx=20)
        role_combobox.current(0)

        def save():
            if not username_var.get().strip() or not password_var.get().strip():
                messagebox.showwarning("提示", "用户名和密码不能为空！")
                return
            
            idx = role_combobox.current()
            role_id = roles[idx][0] if roles else 1
            
            if UserService.add_user(username_var.get(), password_var.get(), real_name_var.get(), role_id):
                messagebox.showinfo("成功", "添加用户成功！")
                self.load_users()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加用户失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_user(self):
        """编辑用户"""
        if not self.selected_user_id:
            messagebox.showwarning("提示", "请先选择用户！")
            return
        
        users = UserService.get_all_users()
        user = None
        for u in users:
            if u[0] == self.selected_user_id:
                user = u
                break
        
        if not user:
            return
        
        roles = RoleService.get_all_roles()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑用户")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="用户名:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        username_var = tk.StringVar(value=user[1])
        ttk.Entry(dialog, textvariable=username_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="真实姓名:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        real_name_var = tk.StringVar(value=user[2])
        ttk.Entry(dialog, textvariable=real_name_var, width=33).grid(row=1, column=1, padx=20)
        
        ttk.Label(dialog, text="角色:").grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        role_names = [r[1] for r in roles]
        role_combobox = ttk.Combobox(dialog, values=role_names, state="readonly", width=27)
        role_combobox.grid(row=2, column=1, padx=20)
        
        # 找到当前角色索引
        role_idx = 0
        for i, r in enumerate(roles):
            if r[1] == user[3]:
                role_idx = i
                break
        role_combobox.current(role_idx)
        
        ttk.Label(dialog, text="状态:").grid(row=3, column=0, sticky=tk.W, padx=20, pady=10)
        status_combobox = ttk.Combobox(dialog, values=['启用', '禁用'], state="readonly", width=27)
        status_combobox.grid(row=3, column=1, padx=20)
        status_combobox.current(user[4])

        def save():
            idx = role_combobox.current()
            role_id = roles[idx][0] if roles else 1
            
            if UserService.update_user(self.selected_user_id, username_var.get(), real_name_var.get(), 
                                    role_id, status_combobox.current()):
                messagebox.showinfo("成功", "修改用户成功！")
                self.load_users()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改用户失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_user(self):
        """删除用户"""
        if not self.selected_user_id:
            messagebox.showwarning("提示", "请先选择用户！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该用户吗？"):
            if UserService.delete_user(self.selected_user_id):
                messagebox.showinfo("成功", "删除用户成功！")
                self.load_users()
                self.selected_user_id = None
            else:
                messagebox.showerror("错误", "删除用户失败！")

    def setup_roles_tab(self):
        """角色管理标签页"""
        frame = self.tab_roles
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="➕ 添加角色", command=self.add_role).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ 编辑角色", command=self.edit_role).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ 删除角色", command=self.delete_role).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 刷新", command=self.load_roles).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("name", "description")
        self.roles_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.roles_tree.heading("name", text="角色名称")
        self.roles_tree.heading("description", text="描述")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.roles_tree.yview)
        self.roles_tree.configure(yscrollcommand=scrollbar.set)
        
        self.roles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.roles_tree.bind('<<TreeviewSelect>>', self.on_role_select)
        self.selected_role_id = None
        
        self.load_roles()

    def load_roles(self):
        """加载角色"""
        for item in self.roles_tree.get_children():
            self.roles_tree.delete(item)
        
        roles = RoleService.get_all_roles()
        if roles:
            for role in roles:
                self.roles_tree.insert("", tk.END, values=(role[1], role[2]))

    def on_role_select(self, event):
        """选择角色"""
        selection = self.roles_tree.selection()
        if selection:
            item = self.roles_tree.item(selection[0])
            name = item['values'][0]
            roles = RoleService.get_all_roles()
            for role in roles:
                if role[1] == name:
                    self.selected_role_id = role[0]
                    break

    def add_role(self):
        """添加角色"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加角色")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="角色名称:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="描述:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=33).grid(row=1, column=1, padx=20)

        def save():
            if not name_var.get().strip():
                messagebox.showwarning("提示", "角色名称不能为空！")
                return
            
            if RoleService.add_role(name_var.get(), desc_var.get()):
                messagebox.showinfo("成功", "添加角色成功！")
                self.load_roles()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加角色失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_role(self):
        """编辑角色"""
        if not self.selected_role_id:
            messagebox.showwarning("提示", "请先选择角色！")
            return
        
        roles = RoleService.get_all_roles()
        role = None
        for r in roles:
            if r[0] == self.selected_role_id:
                role = r
                break
        
        if not role:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑角色")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="角色名称:").grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        name_var = tk.StringVar(value=role[1])
        ttk.Entry(dialog, textvariable=name_var, width=33).grid(row=0, column=1, padx=20)
        
        ttk.Label(dialog, text="描述:").grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        desc_var = tk.StringVar(value=role[2])
        ttk.Entry(dialog, textvariable=desc_var, width=33).grid(row=1, column=1, padx=20)

        def save():
            if not name_var.get().strip():
                messagebox.showwarning("提示", "角色名称不能为空！")
                return
            
            if RoleService.update_role(self.selected_role_id, name_var.get(), desc_var.get()):
                messagebox.showinfo("成功", "修改角色成功！")
                self.load_roles()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "修改角色失败！")

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="保存", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_role(self):
        """删除角色"""
        if not self.selected_role_id:
            messagebox.showwarning("提示", "请先选择角色！")
            return
        
        if messagebox.askyesno("确认", "确定要删除该角色吗？"):
            if RoleService.delete_role(self.selected_role_id):
                messagebox.showinfo("成功", "删除角色成功！")
                self.load_roles()
                self.selected_role_id = None
            else:
                messagebox.showerror("错误", "删除角色失败！")
