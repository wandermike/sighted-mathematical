import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from pandasai import SmartDataframe
from pandasai.llm.base import LLM
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from ttkthemes import ThemedTk
import threading
import os
import json
from datetime import datetime
import sys
import logging

try:
    import importlib.metadata
    importlib.metadata.metadata('pandasai')
except (ImportError, importlib.metadata.PackageNotFoundError):
    import sys
    import types
    if not hasattr(sys.modules, 'pandasai._version'):
        mod = types.ModuleType('pandasai._version')
        mod.__version__ = "1.0.0"
        sys.modules['pandasai._version'] = mod

# 全局禁用所有日志文件
logging.disable(logging.CRITICAL)

# 设置 pandasai 不生成日志文件
os.environ["PANDASAI_LOG_LEVEL"] = "CRITICAL"
os.environ["PANDASAI_SKIP_LOGGING_CONFIG"] = "true"

# 仅在开发环境启用控制台日志
if not getattr(sys, 'frozen', False):
    # 开发环境，只输出到控制台，不输出到文件
    handlers = [logging.StreamHandler()]
    logging.basicConfig(level=logging.ERROR, handlers=handlers, force=True)

class DeepSeekLLM(LLM):

    def __init__(self, api_key, model="deepseek-chat"):
        super().__init__()
        self.api_key = api_key
        self.model = model

    @property
    def type(self):
        return "deepseek"

    def call(self, prompt: str, context: dict = None, **kwargs):
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        if context:
            prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"
            
        data = {
            "model": self.model,
            "messages": [{"role": "system", "content": "You are a helpful assistant."},
                         {"role": "user", "content": prompt}],
            "temperature": 0.5
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"

class ModernButton(ttk.Button):
    """自定义按钮样式"""
    def __init__(self, master=None, **kwargs):
        self.tooltip_text = kwargs.pop('tooltip', None)
        self.icon = kwargs.pop('icon', None)
        
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        if self.tooltip_text:
            self.tooltip = None
            self.bind('<Enter>', self.show_tooltip)
            self.bind('<Leave>', self.hide_tooltip)
            
        if self.icon:
            self['compound'] = tk.LEFT
            self['image'] = self.icon

    def on_enter(self, e):
        self['style'] = 'Accent.TButton'

    def on_leave(self, e):
        self['style'] = 'TButton'
        
    def show_tooltip(self, event=None):
        self.on_enter(event)
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 25
        
        # 创建工具提示窗口
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.tooltip_text, 
                          background="#ffffe0", relief="solid", borderwidth=1,
                          font=("微软雅黑", 9), padding=5)
        label.pack()
        
    def hide_tooltip(self, event=None):
        self.on_leave(event)
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ProgressDialog:
    def __init__(self, parent, title="处理中"):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("300x120")
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)
        
        # 居中
        x = parent.winfo_x() + parent.winfo_width() // 2 - 150
        y = parent.winfo_y() + parent.winfo_height() // 2 - 60
        self.top.geometry(f"+{x}+{y}")
        
        # 样式
        style = ttk.Style()
        style.configure("TProgressbar", thickness=8)
        
        # 提示标签
        self.message_var = tk.StringVar(value="正在处理，请稍候...")
        self.message = ttk.Label(self.top, textvariable=self.message_var,
                                font=("微软雅黑", 10), padding=(10, 10))
        self.message.pack(fill=tk.X)
        
        # 进度条
        self.progress = ttk.Progressbar(self.top, mode="indeterminate", style="TProgressbar")
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        self.progress.start(10)
        
        # 取消按钮
        self.cancel_button = ttk.Button(self.top, text="取消", command=self.on_cancel)
        self.cancel_button.pack(pady=5)
        
        self.cancelled = False
        
    def update_message(self, message):
        self.message_var.set(message)
        self.top.update_idletasks()
        
    def on_cancel(self):
        self.cancelled = True
        self.top.destroy()
        
    def close(self):
        self.progress.stop()
        self.top.destroy()

class DataAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能数据分析助手")
        self.root.geometry("1200x800")
        
        # 设置字体支持
        font_files = []
        for font_name in ['msyh.ttc', 'simhei.ttf', 'simsun.ttc']:
            path = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts', font_name)
            if os.path.exists(path):
                font_files.append(path)
        
        # 尝试加载系统字体
        for font_file in font_files:
            if os.path.exists(font_file):
                # 设置 matplotlib 字体
                matplotlib.font_manager.fontManager.addfont(font_file)
                break
        
        # 设置 matplotlib 显示中文
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
        
        # 设置配置文件路径
        self.config_file = os.path.join(os.path.expanduser('~'), "analyzer_config.json")
        self.recent_files = []
        self.load_config()
        
        # 初始化变量
        self.api_key = self.config.get("api_key", "xxxxxxxxxxxxxxxxxxx")
        self.analyzer = None
        self.df = None
        self.df_preview = None  # 预览数据
        self.sdf = None
        self.current_file = None
        self.cancel_analysis = False
        self.analysis_thread = None
        
        # 创建并加载默认数据集
        self.create_default_dataset()
        
        # 设置主题和样式
        self.setup_styles()
        
        # 创建主框架
        self.create_widgets()
        
        # 初始化分析器
        self.initialize_analyzer()
        
        # Check if API key is still default
        if self.api_key == "xxxxxxxxxxxxxxxxxxx":
            messagebox.showinfo("API 设置", "请设置您的 DeepSeek API Key，目前仅支持 DeepSeek API")
            self.show_api_settings()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    self.recent_files = self.config.get("recent_files", [])
            else:
                self.config = {}
                self.recent_files = []
        except Exception:
            self.config = {}
            self.recent_files = []
            
    def save_config(self):
        """保存配置"""
        try:
            self.config["api_key"] = self.api_key
            self.config["recent_files"] = self.recent_files[:5]  # 只保留最近5个
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False)
        except Exception:
            pass
    
    def setup_styles(self):
        """设置样式，与其他模块保持一致"""
        self.style = ttk.Style()
        
        # 按钮样式 - 与其他模块保持一致，使用蓝色背景
        self.style.configure('TButton', padding=6, font=('SimHei', 10))
        self.style.configure('Accent.TButton', background='#4A90E2')
        
        # 标签样式
        self.style.configure('TLabel', font=('SimHei', 10))
        self.style.configure('Header.TLabel', font=('SimHei', 20, 'bold'))
        self.style.configure('Title.TLabel', font=('SimHei', 14, 'bold'))
        
        # 框架样式
        self.style.configure('TLabelframe', font=('SimHei', 10))
        self.style.configure('TLabelframe.Label', font=('SimHei', 10, 'bold'))
        
        # 输入框样式
        self.style.configure('TEntry', padding=5, font=('SimHei', 10))
        
        # 自定义框架样式 - 更改为浅蓝色背景，与其他模块一致
        self.style.configure('Custom.TFrame', background='#E6F3FF')
        self.style.configure('Header.TFrame', background='#E6F3FF')
        
        # 下拉框样式
        self.style.configure('TCombobox', padding=5, font=('SimHei', 10))
        self.root.option_add('*TCombobox*Listbox.font', ('SimHei', 10))
        
        # 文本框样式
        self.style.configure('TText', font=('SimHei', 10))
        
        # 设置Treeview样式 (数据表格)
        self.style.configure('Treeview', font=('SimHei', 9))
        self.style.configure('Treeview.Heading', font=('SimHei', 10, 'bold'), background='#E6F3FF')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建菜单
        self.create_menu()
        
        # 主容器
        self.main_container = ttk.Frame(self.root, style='Custom.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题栏
        header_frame = ttk.Frame(self.main_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X)
        
        # 标题
        header_label = ttk.Label(header_frame, 
                                text="智能数据分析助手", 
                                style='Header.TLabel',
                                foreground='#2C3E50')  # 设置文字颜色与其他模块一致
        header_label.pack(pady=10)
        
        # 内容区域容器
        content_container = ttk.Frame(self.main_container, style='Custom.TFrame')
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 文件操作区域
        self.create_file_frame(content_container)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(content_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 数据预览标签页
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="数据预览")
        
        # 数据可视化标签页
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="数据可视化")
        
        # 分析结果标签页
        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="分析结果")
        
        # 设置预览区域
        self.setup_preview_tab()
        
        # 设置可视化区域
        self.setup_viz_tab()
        
        # 设置结果区域
        self.setup_result_tab()
        
        # 底部控制区域
        self.create_control_frame(content_container)
        
        # 状态栏
        self.create_status_bar(self.main_container)
    
    def create_menu(self):
        """创建菜单"""
        # 创建自定义样式的菜单
        self.root.option_add('*Menu.font', ('微软雅黑', 10))
        self.root.option_add('*Menu.background', '#f0f0f0')
        self.root.option_add('*Menu.selectColor', '#e0e0e0')
        self.root.option_add('*Menu.activeBackground', '#d0d0d0')
        
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.load_file)
        
        # 最近文件子菜单
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self.update_recent_menu()
        file_menu.add_cascade(label="最近文件", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="保存分析结果", command=self.save_results)
        file_menu.add_command(label="保存可视化图表", command=self.save_visualization)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="API设置", command=self.show_api_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self.show_help)
        
        # 添加菜单到菜单栏
        menubar.add_cascade(label="文件", menu=file_menu)
        menubar.add_cascade(label="设置", menu=settings_menu)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def update_recent_menu(self):
        """更新最近文件菜单"""
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="<无最近文件>", state=tk.DISABLED)
        else:
            for file_path in self.recent_files:
                # 显示文件名而非完整路径
                file_name = os.path.basename(file_path)
                self.recent_menu.add_command(
                    label=file_name,
                    command=lambda f=file_path: self.open_recent_file(f)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="清除最近文件列表", command=self.clear_recent_files)
    
    def open_recent_file(self, file_path):
        """打开最近文件"""
        if os.path.exists(file_path):
            self.load_file_from_path(file_path)
        else:
            messagebox.showwarning("文件不存在", f"文件 {file_path} 不存在或已被移动。")
            # 从列表中移除
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.update_recent_menu()
    
    def clear_recent_files(self):
        """清除最近文件列表"""
        self.recent_files = []
        self.update_recent_menu()
    
    def create_file_frame(self, parent):
        """创建文件操作区域"""
        file_frame = ttk.LabelFrame(parent, text="数据文件")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 左侧按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 打开文件按钮
        open_button = ttk.Button(
            button_frame, 
            text="打开数据文件",
            command=self.load_file
        )
        open_button.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(
            button_frame, 
            text="刷新数据",
            command=self.refresh_data
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 重置为默认数据按钮
        default_button = ttk.Button(
            button_frame, 
            text="使用示例数据",
            command=self.load_default_data
        )
        default_button.pack(side=tk.LEFT, padx=5)
        
        # 右侧文件信息区域
        info_frame = ttk.Frame(file_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10, pady=10)
        
        ttk.Label(info_frame, text="当前文件：").pack(side=tk.LEFT)
        self.file_label = ttk.Label(info_frame, text="未选择文件" if self.current_file is None else os.path.basename(self.current_file))
        self.file_label.pack(side=tk.LEFT)
        
        # 文件信息标签
        self.file_info = ttk.Label(info_frame, text="")
        self.file_info.pack(side=tk.RIGHT)
        
        # 如果已经有默认数据，更新文件标签和信息
        if self.df is not None and self.current_file == "默认示例数据.xlsx":
            self.file_label.config(text=os.path.basename(self.current_file))
            self.file_info.config(text=f"行数: {len(self.df)}")
    
    def setup_preview_tab(self):
        """设置数据预览标签页"""
        preview_container = ttk.Frame(self.preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据信息区域
        info_frame = ttk.LabelFrame(preview_container, text="数据基本信息")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.data_info_text = scrolledtext.ScrolledText(
            info_frame,
            height=6,
            font=('微软雅黑', 10),  # 改为微软雅黑以更好地显示中文
            wrap=tk.WORD,
            background='#ffffff'
        )
        self.data_info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 数据表格预览区域
        table_frame = ttk.LabelFrame(preview_container, text="数据表格预览")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        self.preview_table = ttk.Treeview(table_frame)
        self.preview_table.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.preview_table.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_table.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(preview_container, orient="horizontal", command=self.preview_table.xview)
        scrollbar_x.pack(fill=tk.X)
        self.preview_table.configure(xscrollcommand=scrollbar_x.set)
    
    def setup_viz_tab(self):
        """设置数据可视化标签页"""
        viz_container = ttk.Frame(self.viz_frame)
        viz_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 可视化控制区域
        control_frame = ttk.LabelFrame(viz_container, text="可视化控制")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 图表类型选择
        ttk.Label(control_frame, text="图表类型:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.chart_type = ttk.Combobox(
            control_frame,
            values=["柱状图", "折线图", "饼图", "散点图", "箱线图", "热力图"],
            width=10,
            state='readonly'
        )
        self.chart_type.set("柱状图")
        self.chart_type.pack(side=tk.LEFT, padx=5, pady=5)
        
        # X轴选择
        ttk.Label(control_frame, text="X轴:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.x_axis = ttk.Combobox(
            control_frame,
            width=15,
            state='readonly'
        )
        self.x_axis.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Y轴选择
        ttk.Label(control_frame, text="Y轴:").pack(side=tk.LEFT, padx=5, pady=5)
        
        self.y_axis = ttk.Combobox(
            control_frame,
            width=15,
            state='readonly'
        )
        self.y_axis.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 绘图按钮
        plot_button = ModernButton(
            control_frame,
            text="生成图表",
            command=self.generate_plot,
            tooltip="根据选择的参数生成数据可视化图表"
        )
        plot_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 保存按钮
        save_button = ModernButton(
            control_frame,
            text="保存图表",
            command=self.save_visualization,
            tooltip="将当前图表保存为图片文件"
        )
        save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 图表区域
        self.chart_frame = ttk.LabelFrame(viz_container, text="图表")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建绘图区域
        self.figure, self.ax = plt.subplots(figsize=(10, 6), dpi=80)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chart_canvas.draw()
    
    def setup_result_tab(self):
        """设置分析结果标签页"""
        result_container = ttk.Frame(self.result_frame)
        result_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示区域
        self.result_text = scrolledtext.ScrolledText(
            result_container,
            font=('微软雅黑', 10),  # 改为微软雅黑以更好地显示中文
            wrap=tk.WORD,
            background='#ffffff'
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def create_control_frame(self, parent):
        """创建控制区域"""
        control_frame = ttk.LabelFrame(parent, text="分析控制", padding=10)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        # 分析类型选择
        type_frame = ttk.Frame(control_frame)
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(type_frame, text="分析类型:").pack(side=tk.LEFT, padx=5)
        
        self.analysis_type = ttk.Combobox(
            type_frame,
            values=["基础统计分析", "趋势分析", "相关性分析", "分组分析", "自定义分析"],
            width=20,
            state='readonly'
        )
        self.analysis_type.set("选择分析类型")
        self.analysis_type.pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.analysis_type.bind("<<ComboboxSelected>>", self.on_analysis_type_selected)

        # 自定义查询区域
        query_frame = ttk.Frame(control_frame)
        query_frame.pack(fill=tk.X, pady=5)

        ttk.Label(query_frame, text="自定义查询:").pack(side=tk.LEFT, padx=5)
        
        self.custom_query = ttk.Entry(query_frame, width=60)
        self.custom_query.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.custom_query.insert(0, "输入自定义分析问题")
        self.custom_query.bind("<FocusIn>", self.on_entry_click)
        self.custom_query.bind("<FocusOut>", self.on_entry_leave)
        self.custom_query.config(foreground='grey')

        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.analyze_button = ModernButton(
            button_frame,
            text="开始分析",
            command=self.perform_analysis,
            tooltip="开始执行数据分析"
        )
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ModernButton(
            button_frame,
            text="保存结果",
            command=self.save_results,
            tooltip="将分析结果保存到文件"
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # 高级分析选项区域
        self.advanced_frame = ttk.LabelFrame(control_frame, text="高级分析选项")
        
        # 根据分析类型显示不同的选项
        self.group_by_frame = ttk.Frame(self.advanced_frame)
        ttk.Label(self.group_by_frame, text="分组字段:").pack(side=tk.LEFT, padx=5)
        self.group_by_field = ttk.Combobox(self.group_by_frame, width=15, state='readonly')
        self.group_by_field.pack(side=tk.LEFT, padx=5)
        
        self.target_frame = ttk.Frame(self.advanced_frame)
        ttk.Label(self.target_frame, text="目标字段:").pack(side=tk.LEFT, padx=5)
        self.target_field = ttk.Combobox(self.target_frame, width=15, state='readonly')
        self.target_field.pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(
            parent,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(fill=tk.X)
    
    def on_entry_click(self, event):
        """输入框获得焦点时的处理"""
        if self.custom_query.get() == "输入自定义分析问题":
            self.custom_query.delete(0, tk.END)
            self.custom_query.config(foreground='black')
    
    def on_entry_leave(self, event):
        """输入框失去焦点时的处理"""
        if self.custom_query.get() == "":
            self.custom_query.insert(0, "输入自定义分析问题")
            self.custom_query.config(foreground='grey')
    
    def on_analysis_type_selected(self, event):
        """分析类型选择变化时的处理"""
        selected = self.analysis_type.get()
        
        # 隐藏之前的高级选项框架
        for widget in self.advanced_frame.winfo_children():
            widget.pack_forget()
            
        # 根据选择显示不同的选项
        if selected == "分组分析":
            self.group_by_frame.pack(fill=tk.X, pady=5)
            self.target_frame.pack(fill=tk.X, pady=5)
            self.advanced_frame.pack(fill=tk.X, pady=5)
        elif selected == "相关性分析":
            self.target_frame.pack(fill=tk.X, pady=5)
            self.advanced_frame.pack(fill=tk.X, pady=5)
        else:
            self.advanced_frame.pack_forget()
    
    def update_status(self, message):
        """更新状态栏信息"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def add_to_recent_files(self, file_path):
        """添加到最近文件列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > 5:
            self.recent_files = self.recent_files[:5]
        self.update_recent_menu()
    
    def load_file(self):
        """加载文件对话框"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_file_from_path(file_path)
    
    def load_file_from_path(self, file_path):
        """从路径加载文件"""
        try:
            self.update_status(f"正在加载文件 {os.path.basename(file_path)}...")
            
            # 使用进度对话框
            progress = ProgressDialog(self.root, "加载文件")
            
            def load_task():
                try:
                    if file_path.endswith(('.xlsx', '.xls')):
                        try:
                            self.df = pd.read_excel(file_path)
                        except IOError as e:
                            if "File is already open" in str(e):
                                self.root.after(0, lambda: self.show_file_locked_error(str(e), progress))
                                return
                            else:
                                raise
                    elif file_path.endswith('.csv'):
                        try:
                            # 尝试不同的编码方式打开CSV文件
                            try:
                                self.df = pd.read_csv(file_path, encoding='utf-8')
                            except UnicodeDecodeError:
                                try:
                                    self.df = pd.read_csv(file_path, encoding='gbk')
                                except UnicodeDecodeError:
                                    self.df = pd.read_csv(file_path, encoding='latin1')
                        except IOError as e:
                            if "File is already open" in str(e):
                                self.root.after(0, lambda: self.show_file_locked_error(str(e), progress))
                                return
                            else:
                                raise
                    else:
                        raise ValueError("不支持的文件格式")
                    
                    # 更新UI
                    self.root.after(0, lambda: self.finish_load(file_path, progress))
                except Exception:
                    self.root.after(0, lambda: self.show_load_error(str(e), progress))
            
            # 启动加载线程
            thread = threading.Thread(target=load_task)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.update_status("文件加载失败")
            messagebox.showerror("错误", f"加载文件失败：{str(e)}")
    
    def show_file_locked_error(self, error_message, progress):
        """显示文件被锁定的错误"""
        progress.close()
        self.update_status("文件被锁定")
        messagebox.showerror("文件被锁定", 
                            f"文件已被其他程序打开，无法访问。\n\n"
                            f"错误信息: {error_message}\n\n"
                            f"解决方法:\n"
                            f"1. 关闭可能正在使用此文件的其他程序\n"
                            f"2. 使用任务管理器结束相关进程\n"
                            f"3. 尝试加载其他文件或重启计算机")
    
    def finish_load(self, file_path, progress):
        """完成文件加载后的处理"""
        try:
            progress.close()
            
            self.sdf = SmartDataframe(self.df, config={"llm": self.analyzer})
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            
            # 更新文件信息
            file_size = os.path.getsize(file_path) / 1024  # KB
            file_info = f"大小: {file_size:.1f} KB | 行数: {len(self.df)}"
            self.file_info.config(text=file_info)
            
            # 更新数据预览
            self.update_data_preview()
            
            # 更新可视化选项
            self.update_visualization_options()
            
            # 添加到最近文件
            self.add_to_recent_files(file_path)
            
            self.update_status(f"文件 {os.path.basename(file_path)} 加载成功")
            messagebox.showinfo("成功", "文件加载成功！")
        except Exception as e:
            self.update_status("文件加载处理失败")
            messagebox.showerror("错误", f"处理文件时出错：{str(e)}")
    
    def show_load_error(self, error_message, progress):
        """显示加载错误"""
        progress.close()
        self.update_status("文件加载失败")
        messagebox.showerror("错误", f"加载文件失败：{error_message}")
    
    def update_data_preview(self):
        """更新数据预览"""
        if self.df is None:
            return
            
        # 更新数据信息文本
        try:
            info = f"数据基本信息：\n"
            info += f"行数：{len(self.df)}\n"
            info += f"列数：{len(self.df.columns)}\n"
            info += f"列名：{', '.join(str(col) for col in self.df.columns)}\n\n"
            
            # 添加数据类型信息
            info += "数据类型：\n"
            for col, dtype in self.df.dtypes.items():
                info += f"  {col}: {dtype}\n"
                
            # 添加缺失值信息
            missing = self.df.isnull().sum()
            if missing.sum() > 0:
                info += "\n缺失值信息：\n"
                for col, count in missing.items():
                    if count > 0:
                        percent = (count / len(self.df)) * 100
                        info += f"  {col}: {count} 个缺失值 ({percent:.1f}%)\n"
            
            self.data_info_text.delete(1.0, tk.END)
            self.data_info_text.insert(tk.END, info)
        except Exception as e:
            self.data_info_text.delete(1.0, tk.END)
            self.data_info_text.insert(tk.END, f"更新数据信息时出错: {str(e)}")
        
        # 更新数据表格
        self.update_data_table()
    
    def update_data_table(self):
        """更新数据表格"""
        # 清除现有数据
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
            
        # 清除现有列
        self.preview_table['columns'] = []
        
        if self.df is None:
            return
            
        # 设置列
        columns = list(self.df.columns)
        self.preview_table['columns'] = columns
        
        # 配置列标题
        self.preview_table.heading('#0', text='行号')
        self.preview_table.column('#0', width=60, stretch=False)
        
        # 配置树状表格的显示样式
        self.preview_table.tag_configure('odd', background='#f9f9f9')
        self.preview_table.tag_configure('even', background='#ffffff')
        
        for col in columns:
            self.preview_table.heading(col, text=col)
            # 根据数据类型设置列宽
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.preview_table.column(col, width=100)
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.preview_table.column(col, width=150)
            else:
                # 计算最大宽度
                max_len = max(len(str(self.df[col].iloc[0])) if len(self.df) > 0 else 0, len(col))
                self.preview_table.column(col, width=max(60, min(300, max_len * 10)))
        
        # 添加行数据，最多显示100行
        display_df = self.df.head(100)
        for i, row in enumerate(display_df.itertuples()):
            values = [row[j+1] for j in range(len(columns))]
            # 格式化值
            formatted_values = []
            for val in values:
                if pd.isna(val):
                    formatted_values.append('')
                elif isinstance(val, (float, np.float64)):
                    formatted_values.append(f"{val:.4g}")
                else:
                    formatted_values.append(str(val))
            
            # 添加行，使用奇偶行不同的背景色
            tag = 'odd' if i % 2 else 'even'
            self.preview_table.insert('', 'end', text=str(i), values=formatted_values, tags=(tag,))
    
    def update_visualization_options(self):
        """更新可视化选项"""
        if self.df is None:
            return
            
        # 获取列名
        columns = list(self.df.columns)
        
        # 更新X轴选项
        self.x_axis['values'] = columns
        if columns:
            self.x_axis.current(0)
            
        # 更新Y轴选项
        # 只包含数值型列
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        self.y_axis['values'] = numeric_cols
        if numeric_cols:
            self.y_axis.current(0)
            
        # 更新分组和目标字段选项
        self.group_by_field['values'] = columns
        self.target_field['values'] = numeric_cols
    
    def generate_plot(self):
        """生成可视化图表"""
        if self.df is None:
            messagebox.showwarning("警告", "请先加载数据文件！")
            return
            
        try:
            x_col = self.x_axis.get()
            y_col = self.y_axis.get()
            chart_type = self.chart_type.get()
            
            if not x_col or not y_col:
                messagebox.showwarning("警告", "请选择X轴和Y轴字段！")
                return
                
            # 清除当前图形
            self.ax.clear()
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 根据图表类型绘制
            if chart_type == "柱状图":
                # 限制数据点数量以提高性能
                if len(self.df) > 50:
                    # 对于大数据集，取前50个值
                    plot_df = self.df.head(50)
                    plt.figtext(0.5, 0.01, "注: 仅显示前50条数据", ha="center", fontsize=9, 
                              color="gray")
                else:
                    plot_df = self.df
                    
                plot_df.plot(kind='bar', x=x_col, y=y_col, ax=self.ax, legend=True, 
                           color='#5b9bd5')
                self.ax.set_title(f"{y_col} 按 {x_col} 分组")
                
                # 自动旋转X轴标签以避免重叠
                plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            
            elif chart_type == "折线图":
                self.df.plot(kind='line', x=x_col, y=y_col, ax=self.ax, marker='o', 
                           color='#5b9bd5', markersize=4, linewidth=2)
                self.ax.set_title(f"{y_col} 随 {x_col} 的变化趋势")
            
            elif chart_type == "饼图":
                # 对于饼图，我们需要聚合数据
                pie_data = self.df.groupby(x_col)[y_col].sum()
                
                # 限制饼图切片
                if len(pie_data) > 10:
                    # 保留前9个最大值，其他归为"其他"
                    top_n = pie_data.nlargest(9)
                    others = pd.Series({'其他': pie_data.sum() - top_n.sum()})
                    pie_data = pd.concat([top_n, others])
                
                colors = plt.cm.Paired(np.linspace(0, 1, len(pie_data)))
                pie_data.plot(kind='pie', ax=self.ax, autopct='%1.1f%%', 
                            colors=colors, shadow=False)
                self.ax.set_title(f"{y_col} 的分布 (按 {x_col})")
                self.ax.set_ylabel('')
            
            elif chart_type == "散点图":
                self.df.plot(kind='scatter', x=x_col, y=y_col, ax=self.ax, 
                           color='#5b9bd5', alpha=0.6)
                self.ax.set_title(f"{x_col} 与 {y_col} 的关系")
            
            elif chart_type == "箱线图":
                self.df.boxplot(column=y_col, by=x_col, ax=self.ax, 
                             patch_artist=True, 
                             boxprops=dict(facecolor='#5b9bd5', color='black'),
                             flierprops=dict(markerfacecolor='red', marker='o'))
                self.ax.set_title(f"{y_col} 的分布 (按 {x_col})")
                plt.suptitle('')  # 移除自动添加的标题
                
                # 自动旋转X轴标签以避免重叠
                plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            
            elif chart_type == "热力图":
                pivot_table = pd.pivot_table(self.df, values=y_col, index=x_col, aggfunc='mean')
                sns.heatmap(pivot_table, annot=True, cmap='YlGnBu', ax=self.ax,
                          fmt='.2g', linewidths=.5)
                self.ax.set_title(f"{y_col} 热力图 (按 {x_col})")
            
            # 应用主题样式
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # 设置标签
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)
            
            # 网格线设置
            self.ax.grid(True, linestyle='--', alpha=0.7)
            
            # 调整布局
            plt.tight_layout()
            
            # 重绘画布
            self.chart_canvas.draw()
            
            self.update_status(f"已生成 {chart_type}")
        
        except Exception as e:
            messagebox.showerror("错误", f"生成图表失败：{str(e)}")
            # 打印详细错误信息到控制台
            import traceback
            print(traceback.format_exc())
    
    def save_visualization(self):
        """保存可视化图表"""
        if not hasattr(self, 'figure') or self.figure is None:
            messagebox.showwarning("警告", "没有可保存的图表！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG 图片", "*.png"),
                ("JPG 图片", "*.jpg"),
                ("PDF 文件", "*.pdf"),
                ("SVG 图片", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", "图表已保存！")
            except Exception as e:
                messagebox.showerror("错误", f"保存图表失败：{str(e)}")
    
    def perform_analysis(self):
        """执行数据分析"""
        if self.df is None:
            messagebox.showwarning("警告", "请先加载数据文件！")
            return
            
        analysis_type = self.analysis_type.get()
        
        if analysis_type == "选择分析类型":
            messagebox.showwarning("警告", "请选择分析类型！")
            return
            
        # 如果是自定义分析，检查查询内容
        if analysis_type == "自定义分析":
            query = self.custom_query.get()
            if query == "输入自定义分析问题" or query.strip() == "":
                messagebox.showwarning("警告", "请输入自定义分析问题！")
                return
                
        # 数据预处理 - 确保数据类型正确
        try:
            # 处理数值列 - 确保数值列是数值类型
            numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
            # 预处理分组字段，确保类型合适
            if analysis_type == "分组分析" and hasattr(self, 'group_by_field') and self.group_by_field.get():
                self.group_by_field.get()
                target_field = self.target_field.get()
                
                # 确保目标字段是数值型
                if target_field and target_field not in numeric_cols:
                    self.df[target_field] = pd.to_numeric(self.df[target_field], errors='coerce')
        except Exception as e:
            self.update_status("数据预处理失败")
            messagebox.showerror("预处理错误", f"数据类型转换失败：{str(e)}")
            return
                
        # 显示进度对话框
        progress = ProgressDialog(self.root, "数据分析中")
        self.cancel_analysis = False
        
        # 在单独的线程中执行分析
        def analysis_task():
            try:
                # 根据分析类型构建查询
                if analysis_type == "基础统计分析":
                    query = "对数据进行基础统计分析，包括均值、中位数、最大值、最小值、标准差等，并解释结果含义。"
                elif analysis_type == "趋势分析":
                    query = "分析数据的变化趋势和模式，找出主要的增长或下降趋势，并解释可能的原因。"
                elif analysis_type == "相关性分析":
                    if hasattr(self, 'target_field') and self.target_field.get():
                        target = self.target_field.get()
                        query = f"分析各个因素与{target}的相关性，找出最具影响力的因素，并解释它们的关系。"
                    else:
                        query = "分析各个数值变量之间的相关性，找出强相关的变量对，并解释它们的关系。"
                elif analysis_type == "分组分析":
                    if hasattr(self, 'group_by_field') and self.group_by_field.get() and hasattr(self, 'target_field') and self.target_field.get():
                        group = self.group_by_field.get()
                        target = self.target_field.get()
                        # 使用纯文本分析而不是自动生成图表
                        query = f"请对数据按{group}分组，分析每组的{target}，包括均值、总和、计数等基本统计信息。比较不同组之间的差异，并解释可能的原因。仅提供文本分析，不要生成图表。"
                    else:
                        query = "选择合适的分组变量，对数据进行分组分析，比较不同组之间的差异。"
                else:  # 自定义分析
                    query = self.custom_query.get()
                    # 添加提示不要生成图表
                    if "分组" in query or "比较" in query:
                        query += " 请提供文本分析，避免生成图表。"
                
                # 更新进度信息
                self.root.after(0, lambda: progress.update_message(f"正在分析: {query[:50]}..."))
                
                # 执行分析
                try:
                    result = self.sdf.chat(query)
                except Exception as e:
                    error_message = str(e)
                    # 如果是类型错误，尝试使用另一种方式分析
                    if "Value type" in error_message and "must match with type plot" in error_message:
                        # 使用更简单的分析方法
                        fallback_query = query + " 请仅提供文本分析结果，不要尝试生成图表或可视化。"
                        result = self.sdf.chat(fallback_query)
                    else:
                        raise
                
                # 更新结果
                if not self.cancel_analysis:
                    self.root.after(0, lambda: self.update_result(result, progress))
                else:
                    self.root.after(0, lambda: progress.close())
            except Exception:
                if not self.cancel_analysis:
                    self.root.after(0, lambda: self.show_analysis_error(str(e), progress))
        
        # 启动分析线程
        self.analysis_thread = threading.Thread(target=analysis_task)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def update_result(self, result, progress):
        """更新分析结果"""
        progress.close()
        
        # 清空结果区域
        self.result_text.delete(1.0, tk.END)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result_text.insert(tk.END, f"=== 分析时间: {timestamp} ===\n\n")
        
        # 添加分析类型
        self.result_text.insert(tk.END, f"分析类型: {self.analysis_type.get()}\n\n")
        
        # 添加结果
        self.result_text.insert(tk.END, result)
        
        # 切换到结果标签页
        self.notebook.select(self.result_frame)
        
        self.update_status("分析完成")
    
    def show_analysis_error(self, error_message, progress):
        """显示分析错误"""
        progress.close()
        self.update_status("分析失败")
        messagebox.showerror("错误", f"分析过程出错：{error_message}")
    
    def save_results(self):
        """保存分析结果"""
        result_text = self.result_text.get(1.0, tk.END).strip()
        if not result_text:
            messagebox.showwarning("警告", "没有可保存的分析结果！")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Excel files", "*.xlsx"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.update_status("正在保存结果...")
                
                if file_path.endswith('.xlsx'):
                    # 保存为Excel
                    pd.DataFrame({'分析结果': [result_text]}).to_excel(file_path, index=False)
                elif file_path.endswith('.html'):
                    # 保存为HTML
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>数据分析结果</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                            h1 {{ color: #333366; }}
                            .timestamp {{ color: #666666; font-style: italic; }}
                            .content {{ white-space: pre-wrap; }}
                        </style>
                    </head>
                    <body>
                        <h1>数据分析结果</h1>
                        <p class="timestamp">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <div class="content">{result_text}</div>
                    </body>
                    </html>
                    """
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    # 默认保存为文本
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_text)
                
                self.update_status(f"结果已保存到 {os.path.basename(file_path)}")
                messagebox.showinfo("成功", "分析结果已保存！")
            except Exception as e:
                self.update_status("保存失败")
                messagebox.showerror("错误", f"保存结果失败：{str(e)}")
    
    def show_api_settings(self):
        """显示API设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("API设置")
        # 增加高度从200到250，确保按钮完全显示
        settings_window.geometry("400x250")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 居中
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 125  # 调整垂直位置
        settings_window.geometry(f"+{x}+{y}")
        
        ttk.Label(settings_window, text="DeepSeek API Key:", font=("微软雅黑", 10)).pack(pady=(20, 5))
        
        api_var = tk.StringVar(value=self.api_key)
        api_entry = ttk.Entry(settings_window, textvariable=api_var, width=40, show="*")
        api_entry.pack(pady=5)
        
        # 显示/隐藏密钥
        show_var = tk.BooleanVar(value=False)
        
        def toggle_show():
            if show_var.get():
                api_entry.config(show="")
            else:
                api_entry.config(show="*")
                
        show_check = ttk.Checkbutton(settings_window, text="显示密钥", variable=show_var, command=toggle_show)
        show_check.pack(pady=5)
        
        # 按钮
        button_frame = ttk.Frame(settings_window)
        # 增加下边距，确保按钮有足够空间
        button_frame.pack(pady=(30, 20))
        
        def save_api_key():
            self.api_key = api_var.get()
            self.initialize_analyzer()
            self.save_config()
            settings_window.destroy()
            messagebox.showinfo("成功", "API设置已保存！")
            
        ttk.Button(button_frame, text="保存", command=save_api_key).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        智能数据分析助手使用指南
        
        1. 文件操作
           - 点击"选择数据文件"按钮加载Excel或CSV文件
           - 通过"文件"菜单可以访问最近打开的文件
        
        2. 数据预览
           - "数据预览"标签页显示数据的基本信息和表格预览
        
        3. 数据可视化
           - 在"数据可视化"标签页中选择图表类型和轴
           - 点击"生成图表"创建可视化
           - 可以保存图表为多种格式
        
        4. 数据分析
           - 选择分析类型（基础统计、趋势分析等）
           - 对于特定分析类型，可以设置高级选项
           - 输入自定义分析问题进行更复杂的分析
           - 点击"开始分析"执行分析
        
        5. 结果处理
           - 在"分析结果"标签页查看分析结果
           - 点击"保存结果"将结果保存为文本、Excel或HTML
        
        6. 设置
           - 在"设置"菜单中可以配置API密钥
        
        如需更多帮助，请联系技术支持。
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        # 居中
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        help_window.geometry(f"+{x}+{y}")
        
        # 帮助内容
        ttk.Label(help_window, text="智能数据分析助手使用指南", 
                 font=("微软雅黑", 14, "bold")).pack(pady=10)
        
        help_text_widget = scrolledtext.ScrolledText(
            help_window, 
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("微软雅黑", 10)
        )
        help_text_widget.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
    
    def initialize_analyzer(self):
        """初始化分析器"""
        try:
            self.analyzer = DeepSeekLLM(self.api_key)
            self.update_status("分析器初始化成功")
        except Exception as e:
            self.update_status("分析器初始化失败")
            messagebox.showerror("错误", f"初始化分析器失败：{str(e)}")
    
    def on_close(self):
        """关闭窗口时的处理"""
        # 保存配置
        self.save_config()
        
        # 关闭窗口
        self.root.destroy()

    def refresh_data(self):
        """刷新当前数据"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_file_from_path(self.current_file)
        else:
            messagebox.showinfo("提示", "没有可刷新的文件")

    def create_default_dataset(self):
        """创建默认的示例数据集"""
        try:
            # 使用直接内置在代码中的固定数据集
            data = {
                '日期': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', 
                       '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                       '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                       '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20'],
                '产品': ['手机', '电脑', '平板', '耳机', '智能手表', 
                       '手机', '电脑', '平板', '耳机', '智能手表',
                       '手机', '电脑', '平板', '耳机', '智能手表',
                       '手机', '电脑', '平板', '耳机', '智能手表'],
                '地区': ['北京', '上海', '广州', '深圳', '成都', 
                       '杭州', '北京', '上海', '广州', '深圳',
                       '成都', '杭州', '北京', '上海', '广州', 
                       '深圳', '成都', '杭州', '北京', '上海'],
                '销售额': [5426.32, 8721.45, 3214.87, 890.21, 2341.65, 
                        6543.21, 7891.45, 2987.34, 768.90, 3245.67,
                        4987.23, 9876.54, 3467.89, 954.32, 2198.76,
                        6789.43, 8234.56, 3654.28, 1023.45, 3476.98],
                '数量': [5, 3, 4, 8, 2, 
                       6, 2, 3, 6, 3,
                       4, 4, 5, 7, 2,
                       7, 3, 4, 9, 4],
                '客户评分': [4.5, 4.2, 3.8, 4.7, 4.0, 
                         3.9, 4.5, 4.1, 4.8, 3.7,
                         4.2, 4.6, 3.9, 4.5, 4.1,
                         4.3, 4.0, 4.2, 4.9, 3.8],
                '促销活动': ['是', '否', '否', '是', '否', 
                         '是', '否', '是', '否', '否',
                         '是', '是', '否', '是', '否',
                         '是', '否', '是', '否', '是']
            }
            
            self.default_df = pd.DataFrame(data)
            
            # 添加单价列
            self.default_df['单价'] = (self.default_df['销售额'] / self.default_df['数量']).round(2)
            
            # 将日期列转换为日期时间类型
            self.default_df['日期'] = pd.to_datetime(self.default_df['日期'])
            
            # 添加月份和星期几
            self.default_df['月份'] = self.default_df['日期'].dt.month
            
            # 添加中文星期几
            weekday_map = {
                0: '星期一',
                1: '星期二',
                2: '星期三',
                3: '星期四',
                4: '星期五',
                5: '星期六',
                6: '星期日'
            }
            self.default_df['星期'] = self.default_df['日期'].dt.weekday.map(weekday_map)
            
            # 加载默认数据集
            self.df = self.default_df.copy()
            
            # 创建一个虚拟文件路径（这个路径实际不存在）
            self.current_file = "默认示例数据.xlsx"
            
            # 初始化Smart DataFrame
            if self.analyzer:
                self.sdf = SmartDataframe(self.df, config={"llm": self.analyzer})
                
        except Exception as e:
            print(f"创建默认数据集出错: {e}")

    def load_default_data(self):
        """加载默认示例数据"""
        try:
            # 加载之前创建的默认数据
            self.df = self.default_df.copy()
            self.current_file = "默认示例数据.xlsx"
            
            # 更新UI
            self.file_label.config(text=os.path.basename(self.current_file))
            self.file_info.config(text=f"行数: {len(self.df)}")
            
            # 初始化Smart DataFrame
            if self.analyzer:
                self.sdf = SmartDataframe(self.df, config={"llm": self.analyzer})
            
            # 更新数据预览
            self.update_data_preview()
            
            # 更新可视化选项
            self.update_visualization_options()
            
            self.update_status("已加载默认示例数据")
            messagebox.showinfo("成功", "已加载销售数据示例!")
        except Exception as e:
            self.update_status("加载默认数据失败")
            messagebox.showerror("错误", f"加载默认数据失败: {str(e)}")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    try:
        # 设置更好的DPI感知
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        root = ThemedTk(theme="arc")  # 使用 arc 主题，也可以尝试 "equilux", "breeze" 等
        
        # 设置图标 (如果有的话)
        try:
            root.iconbitmap("icon.ico")
        except:
            pass

        # 适当设置字体缩放
        font_scale = 1.0  # 默认缩放
        # 根据屏幕分辨率调整字体
        try:
            screen_width = root.winfo_screenwidth()
            if screen_width > 2560:  # 4K或更高分辨率
                pass
            elif screen_width > 1920:  # 2K分辨率
                pass
        except:
            pass

        DataAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        # 确保即使在GUI启动之前崩溃，也能显示错误信息
        import traceback
        error_msg = f"程序启动错误: {str(e)}\n\n{traceback.format_exc()}"
        try:
            # 尝试使用tkinter显示错误
            import tkinter.messagebox
            tkinter.messagebox.showerror("启动错误", error_msg)
        except:
            # 如果tkinter也失败，则使用控制台
            print(error_msg)

if __name__ == "__main__":
    main()