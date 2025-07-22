"""
Module Adapter Component
-----------------------
This module provides adapter classes to bridge between standalone module classes
and the StandardCourseUI interface expected by the main application.
"""

import tkinter as tk

class ModuleAdapter:
    """
    适配器类，用于将独立模块类包装为符合主应用预期接口的类
    
    这个适配器解决了独立模块类未继承StandardCourseUI类导致的AttributeError问题，
    同时保持了UI的一致性和功能的完整性。
    """
    
    @staticmethod
    def adapt(module_class, parent_frame=None, title=None, additional_setup=None):
        """
        创建一个适配后的模块类的实例
        
        参数:
            module_class: 要适配的独立模块类
            parent_frame: 父容器框架
            title: 标题
            additional_setup: 额外的设置回调函数
            
        返回:
            适配后的模块实例
        """
        # 确保有父容器
        if parent_frame is None:
            parent_frame = tk.Frame()
            
        # 创建内容容器
        content_frame = tk.Frame(parent_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 实例化模块类
        module_instance = module_class(content_frame)
        
        # 添加所需的接口方法
        # create_buttons方法是常见的缺失方法
        if not hasattr(module_instance, 'create_buttons'):
            def create_buttons(button_data=None):
                pass
            module_instance.create_buttons = create_buttons
            
        # 如果有额外设置，执行它
        if additional_setup:
            additional_setup(module_instance)
            
        return module_instance

class StandardModuleWrapper:
    """
    标准模块包装器，为不符合StandardCourseUI接口的模块类创建完整的UI包装
    """
    
    def __init__(self, root, module_class, title, **kwargs):
        """初始化包装器"""
        self.root = root
        self.title = title
        self.root.title(title)
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题栏
        self.create_title_bar()
        
        # 创建内容区域
        self.content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 使用适配器创建模块实例
        self.module = ModuleAdapter.adapt(module_class, self.content_frame)
        
        # 创建底部按钮区域
        self.create_bottom_bar()
        
    def create_title_bar(self):
        """创建标题栏"""
        title_bar = tk.Frame(self.main_frame, bg="#3498db", height=50)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        
        # 添加标题
        title_label = tk.Label(
            title_bar, 
            text=self.title, 
            font=("SimHei", 16, "bold"),
            bg="#3498db", 
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 添加返回按钮
        back_button = tk.Button(
            title_bar, 
            text="返回", 
            font=("SimHei", 12),
            bg="#2c3e50",
            fg="white",
            command=self.root.destroy,
            padx=10,
            pady=3
        )
        back_button.pack(side=tk.RIGHT, padx=15, pady=8)
        
    def create_bottom_bar(self):
        """创建底部栏"""
        bottom_bar = tk.Frame(self.main_frame, bg="#ecf0f1", height=40)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 添加版权信息
        status_label = tk.Label(
            bottom_bar, 
            text="© 2025 数学可视化教学平台", 
            font=("SimHei", 10),
            bg="#ecf0f1", 
            fg="#7f8c8d"
        )
        status_label.pack(side=tk.RIGHT, padx=10, pady=10)
