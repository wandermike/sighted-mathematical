import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
import sys

# Pillow 兼容性补丁
try:
    # Pillow>=10 移除了直接在 Image 命名空间下的采样常量
    if not hasattr(Image, "LANCZOS") and hasattr(Image, "Resampling"):
        Image.LANCZOS = Image.Resampling.LANCZOS  # type: ignore
except Exception:
    # 安全忽略，保持向后兼容
    pass

# 统一重采样常量，供本模块内部使用
try:
    RESAMPLE = Image.LANCZOS  # type: ignore[attr-defined]
except AttributeError:
    RESAMPLE = Image.Resampling.LANCZOS  # type: ignore

# 预先导入高等数学可视化模块
try:
    from kehe import KeheApp  # 直接导入KeheApp，而不是EquationVisualizationApp
    print("DEBUG: 成功导入 KeheApp")
except ImportError as e:
    print(f"DEBUG: 无法导入 KeheApp: {e}")
    KeheApp = None

try:
    from weifen import DirectionFieldApp  
    print("DEBUG: 成功导入 DirectionFieldApp")
except ImportError as e:
    print(f"DEBUG: 无法导入 DirectionFieldApp: {e}")
    DirectionFieldApp = None

try:
    from haisen import HessianApp
    print("DEBUG: 成功导入 HessianApp")
except ImportError as e:
    print(f"DEBUG: 无法导入 HessianApp: {e}")
    HessianApp = None

try:
    from fang import EquationVisualizationApp as FangApp
    print("DEBUG: 成功导入 FangApp")
except ImportError as e:
    print(f"DEBUG: 无法导入 FangApp: {e}")
    FangApp = None

# 导入自定义主题和组件
from themes.futuristic_theme import COLORS, FONTS
from components.buttons import FuturisticButton
from components.cards import InteractiveCard
from effects.animations import ParticleSystem

# 导入各个功能模块
from gailvlunn import ProbabilityApp
from juzhenduibi import MatrixComparisonApp
from tezheng import EigenvalueApp
from zhuanzhi import MatrixAnimationApp
from jibianhuan import MatrixTransformationApp
from gaosixiaoyuan import GaussianEliminationApp
from guodujuzhen import MatrixTransitionApp
import jisuan
# jisuan已经导入
from ai import DataAnalyzerGUI  # 导入AI数据分析模块

try:
    from fenxi import AnalysisApp # Assuming fenxi.py has AnalysisApp
except ImportError:
    print("Warning: Could not import AnalysisApp from fenxi.py")
    AnalysisApp = None
try:
    from game import GamePuzzleApp as GameApp  # 正确导入类名并设置别名
except ImportError:
    print("Warning: Could not import GamePuzzleApp from game.py")
    GameApp = None
try:
    from mengka import MonteCarloApp # Assuming mengka.py has MonteCarloApp
except ImportError:
    print("Warning: Could not import MonteCarloApp from mengka.py")
    MonteCarloApp = None
try:
    from suiji import RandomVariableApp # From suiji.py
except ImportError:
    print("Warning: Could not import RandomVariableApp from suiji.py")
    RandomVariableApp = None
try:
    from suijiguocheng import StochasticProcessApp # Assuming suijiguocheng.py has StochasticProcessApp
except ImportError:
    print("Warning: Could not import StochasticProcessApp from suijiguocheng.py")
    StochasticProcessApp = None
try:
    from tuiduan import HypothesisTestingApp # Assuming tuiduan.py has HypothesisTestingApp
except ImportError:
    print("Warning: Could not import HypothesisTestingApp from tuiduan.py")
    HypothesisTestingApp = None
try:
    from zhixin import ConfidenceIntervalApp # From zhixin.py
except ImportError:
    print("Warning: Could not import ConfidenceIntervalApp from zhixin.py")
    ConfidenceIntervalApp = None
# --- End Imports ---

# --- Helper function to find resources ---
def resource_path(relative_path):
    # 兼容 PyInstaller 单文件打包的资源路径
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# --- 为调试添加一个简单的日志函数 ---
def log(message):
    print(f"DEBUG: {message}")

logo_image = None

def add_logo(window):
    global logo_image
    try:
        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((64, 64), RESAMPLE)
            logo_image = ImageTk.PhotoImage(img)
            logo_label = tk.Label(window, image=logo_image, bg=window.cget('bg'))
            logo_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
    except Exception as e:
        log(f"添加logo时出错: {e}")
        
def open_app_window(parent, app_class, title, geometry="1200x800"):
    """增强版助手函数，创建并管理应用窗口，带动画过渡效果。"""
    if not app_class:
        messagebox.showerror("错误", f"无法加载模块: {title}")
        return None

    # 获取父窗口
    root_window = parent.root

    # 先关闭当前窗口
    if hasattr(parent, 'close_current_window'):
        parent.close_current_window()

    # 创建新的Toplevel窗口
    window = tk.Toplevel(root_window)
    window.title(title)
    window.geometry(geometry)
    
    # 初始化透明度为0（用于淡入效果）
    window.attributes('-alpha', 0.0)
    
    # 设置主题样式
    window.config(bg=COLORS["bg_light"])
    
    # 创建内容框架
    content_frame = tk.Frame(window, bg=COLORS["bg_light"])
    
    # 实例化应用类
    app_instance = app_class(window)
    
    # 添加标题栏
    title_bar = tk.Frame(window, bg=COLORS["bg_medium"], height=40)
    title_bar.pack(fill=tk.X, side=tk.TOP)
    
    # 添加标题文本
    title_label = tk.Label(
        title_bar, 
        text=title, 
        font=FONTS["subtitle"], 
        bg=COLORS["bg_medium"], 
        fg=COLORS["text_primary"]
    )
    title_label.pack(side=tk.LEFT, padx=20, pady=8)
    
    # 添加返回按钮
    back_button = FuturisticButton(
        title_bar, 
        text="返回", 
        command=window.destroy, 
        width=80, 
        height=30,
        fg_color=COLORS["accent_primary"]
    )
    back_button.pack(side=tk.RIGHT, padx=15, pady=5)
    
    # 添加装饰线
    divider = tk.Frame(window, height=2, bg=COLORS["accent_secondary"])
    divider.pack(fill=tk.X, padx=0, pady=0)
    
    
    # 保存到父对象的引用
    if hasattr(parent, 'current_window'):
        parent.current_window = window
        log(f"已存储新窗口引用: {title}")
    
    # 设置窗口与父窗口关联
    try:
        window.transient(root_window)
    except tk.TclError:
        pass
    
    # 执行淡入动画
    def perform_fade_in(step=0):
        """使用非阻塞递归 after 实现淡入渐变"""
        steps = 10
        if not window.winfo_exists():
            return
        alpha = step / steps
        window.attributes('-alpha', alpha)
        if step < steps:
            window.after(20, lambda s=step+1: perform_fade_in(s))
    # 启动淡入动画
    window.after(100, perform_fade_in)
    
    # 递归绑定所有内容子组件的可点击性
    def make_all_widgets_clickable(widget, callback):
        """递归地使所有子部件可点击"""
        # 跳过特定类型的组件
        if isinstance(widget, (FuturisticButton, tk.Scrollbar, tk.Entry, tk.Text)):
            return
            
        # 如果是可点击组件，设置手型光标并绑定事件
        if isinstance(widget, (tk.Label, tk.Frame, tk.Canvas)):
            widget.bind("<Button-1>", lambda e: callback())
            widget.config(cursor="hand2")
            
        # 递归处理子组件
        for child in widget.winfo_children():
            make_all_widgets_clickable(child, callback)
    
    # 如果应用实例有点击方法，使所有组件可点击
    if hasattr(app_instance, 'on_click'):
        make_all_widgets_clickable(window, app_instance.on_click)
    
    return window

try:
    from shulie import SequenceModule
    print("DEBUG: 成功导入数列模块")
except ImportError as e:
    print(f"DEBUG: 无法导入数列模块: {e}")
    SequenceModule = None

# --- StandardCourseUI 类定义 ---
class StandardCourseUI:
    """数学课程标准界面基类，所有数学课程界面继承此类"""
    
    def __init__(self, root, title, button_data, course_type="standard"):
        """
        初始化标准课程界面
        
        参数:
            root: 根窗口
            title: 界面标题
            button_data: 按钮数据，格式为 [(名称, 回调函数), ...]
            course_type: 课程类型，可选值为 "standard"(标准), "complex"(复杂带滚动)
        """
        self.root = root
        self.current_window = None
        self.root.title(title)
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 采用与主菜单相同的深色背景
        self.bg_color = COLORS["bg_light"]
        self.accent_color = COLORS["accent_primary"]
        
        # 主框架 - 使用Grid布局
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置主框架网格
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # 标题区域
        self.main_frame.rowconfigure(1, weight=1)  # 内容区域
        self.main_frame.rowconfigure(2, weight=0)  # 底部区域
        
        # 标题容器
        self.title_container = tk.Frame(self.main_frame, bg=self.bg_color, height=80)
        self.title_container.grid(row=0, column=0, sticky="ew")
        self.title_container.grid_propagate(False)  # 防止内部组件影响容器高度
        
        # 标题标签 - 使用白色字体在深色背景上
        self.title_frame = tk.Frame(self.title_container, bg=self.bg_color)
        self.title_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.title_label = tk.Label(
            self.title_frame, 
            text=title,
            font=("SimHei", 24, "bold"),
            bg=self.bg_color,
            fg=COLORS["text_primary"],  # 白色文字
            padx=20,
            pady=10
        )
        self.title_label.pack()
        
        # 内容区域 - 使用Frame容器
        self.content_container = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # 配置内容区域网格
        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)
        
        # 创建内容区域 - 根据课程类型选择实现
        if course_type == "complex":
            # 复杂模式 - 带滚动条
            self.create_scrollable_content()
        else:
            # 标准模式 - 简单网格
            self.create_standard_content()
        
        # 使用按钮数据创建卡片式按钮
        self.create_card_buttons(button_data)
        
        # 底部容器
        self.bottom_container = tk.Frame(self.main_frame, bg=self.bg_color, height=60)
        self.bottom_container.grid(row=2, column=0, sticky="ew")
        self.bottom_container.grid_propagate(False)  # 防止内部组件影响容器高度
        
        # 返回主菜单按钮
        self.return_button = tk.Button(
            self.bottom_container, 
            text="返回主菜单", 
            font=("SimHei", 12),
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            command=self.root.destroy,
            padx=15,
            pady=8
        )
        self.return_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 添加底部版权信息
        copyright_label = tk.Label(
            self.main_frame, 
            text="© 2025 数学可视化教学平台", 
            font=("SimHei", 10),
            bg=self.bg_color,
            fg=COLORS["text_secondary"]
        )
        copyright_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
        # 添加logo
        add_logo(self.root)
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self.on_window_resize)
        
        # 初始化调整
        self.root.after(100, self.initial_adjustment)
    
    def create_standard_content(self):
        """创建标准内容区域 - 简单网格布局"""
        self.button_frame = tk.Frame(self.content_container, bg=self.bg_color)
        self.button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_scrollable_content(self):
        """创建可滚动内容区域 - 用于按钮较多的情况"""
        # 创建滚动容器 - 使用深色背景
        self.canvas = tk.Canvas(self.content_container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 在 grid 中留出左右 10px 边距视觉更美观
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 创建按钮框架 - 作为Canvas内容
        self.button_frame = tk.Frame(self.canvas, bg=self.bg_color)
        # 留出 (10,10) 起始偏移，避免首行贴边
        self.canvas_window = self.canvas.create_window((10, 10), window=self.button_frame, anchor="n")
        
        # 更新Canvas滚动区域
        def update_scrollregion(event):
            # 更新宽度并保持居中
            self.canvas.itemconfig(self.canvas_window, width=self.content_container.winfo_width()-20)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 绑定按钮框架大小变化事件
        self.button_frame.bind("<Configure>", update_scrollregion)
    
    def create_card_buttons(self, button_data):
        """创建卡片式按钮 - 与主界面风格一致"""
        # 计算按钮布局
        cols = min(3, len(button_data))  # 最多3列
        rows = (len(button_data) + cols - 1) // cols  # 向上取整计算行数
        
        # 配置按钮框架网格
        for i in range(cols):
            self.button_frame.columnconfigure(i, weight=1)
        for i in range(rows):
            self.button_frame.rowconfigure(i, weight=1)
        
        # 卡片尺寸
        card_width = 220
        card_height = 150
        card_padding = 15
        
        # 创建按钮列表
        self.buttons = []
        
        # 创建每个卡片
        for i, (text, command) in enumerate(button_data):
            row, col = divmod(i, cols)
            
            # 创建卡片框架
            card = tk.Frame(
                self.button_frame,
                width=card_width,
                height=card_height,
                bg=COLORS["bg_card"],  # 更亮底色
                highlightbackground=COLORS["accent_secondary"],
                highlightthickness=0,
                bd=0,
                relief="flat",
                cursor="hand2"
            )
            
            # Hover 边框
            def _on_enter_card(e, c=card):
                c.configure(highlightthickness=2)

            def _on_leave_card(e, c=card):
                c.configure(highlightthickness=0)

            card.bind("<Enter>", _on_enter_card)
            card.bind("<Leave>", _on_leave_card)
            
            # 在卡片框架中创建网格
            card.columnconfigure(0, weight=1)
            card.rowconfigure(0, weight=1)  # 标题区域
            
            # 添加标题文本
            title_label = tk.Label(
                card,
                text=text,
                font=("SimHei", 14),
                bg=COLORS["bg_card"],
                fg=COLORS["text_primary"],
                wraplength=card_width-20,
                cursor="hand2"  # 保持一致的手型光标
            )
            title_label.grid(row=0, column=0, pady=15)
            
            # 标题标签也绑定点击事件
            title_label.bind("<Button-1>", lambda e, cmd=command: cmd())
            
            # 保存按钮引用
            self.buttons.append(card)
            
            # 递归绑定所有子组件的点击事件
            self.bind_all_children(card, command)
            
            # 放置卡片到网格
            card.grid(row=row, column=col, padx=card_padding, pady=card_padding)
            card.grid_propagate(False)
    
    def bind_all_children(self, parent, command):
        """递归绑定所有子组件的点击事件"""
        for child in parent.winfo_children():
            if isinstance(child, (tk.Frame, tk.Label, tk.Canvas)) and not isinstance(child, FuturisticButton):
                child.config(cursor="hand2")  # 统一设置手型光标
                child.bind("<Button-1>", lambda e, cmd=command: cmd())
                
                # 递归绑定嵌套组件
                if isinstance(child, tk.Frame):
                    self.bind_all_children(child, command)
    
    def on_window_resize(self, event=None):
        """窗口大小变化时的响应"""
        if event is None or event.widget == self.root:
            # 如果使用滚动布局，更新Canvas窗口宽度
            if hasattr(self, 'canvas') and hasattr(self, 'canvas_window'):
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def initial_adjustment(self):
        """初始化调整"""
        # 如果有滚动区域，更新滚动区域大小
        if hasattr(self, 'canvas') and hasattr(self, 'button_frame'):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def close_current_window(self):
        """关闭当前打开的子窗口"""
        if self.current_window and self.current_window.winfo_exists():
            self.current_window.destroy()
        self.current_window = None

class LinearAlgebraApp(StandardCourseUI):
    def __init__(self, root):
        # 准备按钮数据
        button_data = [
            ("矩阵对比", lambda: self.handle_module_click(self.open_matrix_comparison, "矩阵对比")),
            ("特征值与特征向量", lambda: self.handle_module_click(self.open_eigenvalue, "特征值与特征向量")),
            ("矩阵旋转", lambda: self.handle_module_click(self.open_matrix_rotation, "矩阵旋转")),
            ("基变换与向量表示", lambda: self.handle_module_click(self.open_basis_transformation, "基变换与向量表示")),
            ("高斯消元法", lambda: self.handle_module_click(self.open_gaussian_elimination, "高斯消元法")),
            ("矩阵过渡", lambda: self.handle_module_click(self.open_matrix_transition, "矩阵过渡")),
            ("矩阵运算", lambda: self.handle_module_click(self.open_matrix_operations, "矩阵运算")),
            ("行列式", lambda: self.handle_module_click(self.open_determinant, "行列式"))
        ]
        
        # 调用父类初始化
        super().__init__(
            root=root,
            title="线性代数可视化工具",
            button_data=button_data
        )
        
        # 更新返回按钮命令
        self.return_button.config(command=self.return_to_main_menu)
    
    def handle_module_click(self, handler_func, module_name):
        """处理模块点击，增加错误处理"""
        try:
            handler_func()
        except Exception as e:
            messagebox.showerror("模块错误", f"无法加载 {module_name} 模块\n错误信息: {str(e)}")

    # 添加返回主菜单的方法
    def return_to_main_menu(self):
        self.root.destroy()  # 关闭当前窗口

    # 打开各个功能模块的方法
    def open_matrix_comparison(self):
        open_app_window(self, MatrixComparisonApp, "矩阵对比可视化")

    def open_eigenvalue(self):
        open_app_window(self, EigenvalueApp, "特征值与特征向量可视化")

    def open_matrix_rotation(self):
        open_app_window(self, MatrixAnimationApp, "矩阵旋转动画可视化")

    def open_basis_transformation(self):
        open_app_window(self, MatrixTransformationApp, "基变换与向量表示动画")

    def open_gaussian_elimination(self):
        open_app_window(self, GaussianEliminationApp, "高斯消元法可视化")

    def open_matrix_transition(self):
        open_app_window(self, MatrixTransitionApp, "矩阵过渡动画")

    def open_matrix_operations(self):
        open_app_window(self, jisuan.VectorOperationsApp, "矩阵运算可视化")

    def open_determinant(self):
        """打开行列式可视化"""
        try:
            # 在函数内部导入hanglieshi模块
            import hanglieshi
            open_app_window(self, hanglieshi.DeterminantApp, "行列式可视化")
        except ImportError as e:
            messagebox.showerror("模块错误", f"无法导入行列式可视化模块: {str(e)}\n请确保hanglieshi.py文件存在于正确位置。")
        except Exception as e:
            messagebox.showerror("错误", f"打开行列式可视化时出错: {str(e)}")

# --- 特别修复贝叶斯统计模块导入 ---
try:
    from beiye import BayesianApp  # 确保beiye.py中存在这个类
    log("成功导入 BayesianApp")
except ImportError as e:
    log(f"无法导入 BayesianApp: {e}")
    BayesianApp = None
except AttributeError as e:
    log(f"Beiye模块配置错误: {e}")
    BayesianApp = None

class ProbabilityTheoryApp(StandardCourseUI):
    def __init__(self, root):
        # 动态创建可用模块按钮数据
        button_data = []
        
        # 确保所有功能按钮都显示，即使模块不可用
        self.add_button(button_data, "概率分布", ProbabilityApp)
        self.add_button(button_data, "随机变量", RandomVariableApp)
        self.add_button(button_data, "随机过程", StochasticProcessApp)
        self.add_button(button_data, "贝叶斯统计", BayesianApp)
        self.add_button(button_data, "置信区间", ConfidenceIntervalApp)
        self.add_button(button_data, "假设检验", HypothesisTestingApp)
        self.add_button(button_data, "统计分析工具", AnalysisApp)
        self.add_button(button_data, "概率游戏与谜题", GameApp)
        self.add_button(button_data, "蒙特卡洛模拟", MonteCarloApp)
        
        # 调用父类初始化
        course_type = "complex" if len(button_data) > 6 else "standard"
        super().__init__(
            root=root,
            title="概率论与数理统计可视化",
            button_data=button_data,
            course_type=course_type  # 根据按钮数量选择布局模式
        )
        
        # 如果没有可用模块显示错误提示
        if not button_data:
            # 清除现有按钮区域
            for widget in self.button_frame.winfo_children():
                widget.destroy()
                
            error_label = tk.Label(
                self.button_frame,
                text="错误：未找到任何可用模块\n请检查：\n1. 所有.py文件是否齐全\n2. 类名是否正确",
                font=("SimHei", 14),
                fg="red",
                bg=self.bg_color
            )
            error_label.pack(pady=50)
    
    def add_button(self, button_data, title, app_class):
        """添加功能按钮到按钮数据列表"""
        button_data.append((title, self.create_handler_with_fallback(app_class, title)))
    
    def create_open_handler(self, app_class, title):
        """创建打开模块的处理函数"""
        return lambda: open_app_window(self, app_class, title)
        
    def create_handler_with_fallback(self, app_class, title):
        """创建带有失败处理的按钮处理函数"""
        def handler():
            if app_class is not None:
                open_app_window(self, app_class, title)
            else:
                messagebox.showerror("模块错误", f"无法加载 {title} 模块\n请确保相关文件存在且格式正确。")
        return handler

class MainApp:
    def __init__(self, root):
        self.root = root
        self.current_window = None
        self.root.title("数学可视化教学工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 配置基本样式
        self.root.config(bg=COLORS["bg_light"])
        
        # 创建主框架 - 使用Grid布局替代Canvas窗口
        self.main_frame = tk.Frame(root, bg=COLORS["bg_light"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置主框架的行列权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # 顶部导航栏
        self.main_frame.rowconfigure(1, weight=1)  # 内容区域
        self.main_frame.rowconfigure(2, weight=0)  # 底部状态栏
        
        # 创建粒子背景效果 - 作为装饰层
        self.canvas = tk.Canvas(self.main_frame, bg=COLORS["bg_light"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=3, sticky="news")
        
        # 启动粒子系统
        self.particles = ParticleSystem(self.canvas, num_particles=12)
        self.particles.update()
        
        # 顶部导航栏
        self.navbar = tk.Frame(self.main_frame, bg=COLORS["bg_medium"], height=60)
        self.navbar.grid(row=0, column=0, sticky="ew")
        
        # ---------- Logo & 标题 ----------
        # Logo (左侧)
        logo_left = None
        try:
            logo_path_left = resource_path("logo.ico")
            if os.path.exists(logo_path_left):
                img_left = Image.open(logo_path_left)
                img_left = img_left.resize((40, 40), RESAMPLE)
                self.left_logo_image = ImageTk.PhotoImage(img_left)
                logo_left = tk.Label(
                    self.navbar,
                    image=self.left_logo_image,
                    bg=COLORS["bg_medium"]
                )
                logo_left.pack(side=tk.LEFT, padx=15)
        except Exception as e:
            log(f"加载顶部 Logo 失败: {e}")

        # 标题（居中显示）
        self.title_label = tk.Label(
            self.navbar,
            text="数学可视化教学工具",
            font=FONTS["title"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        self.title_label.pack(side=tk.LEFT, pady=10, expand=True)

        # 右侧预留空白填充保持居中
        spacer = tk.Frame(self.navbar, bg=COLORS["bg_medium"], width=40, height=1)
        spacer.pack(side=tk.RIGHT, padx=15)
        
        # 内容区域 - 使用Frame替代Canvas窗口
        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["bg_light"])
        self.content_frame.grid(row=1, column=0, sticky="news", padx=20, pady=20)
        
        # 配置内容框架的行列权重
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # 主要功能卡片区域
        self.cards_frame = tk.Frame(self.content_frame, bg=COLORS["bg_light"])
        self.cards_frame.grid(row=0, column=0)
        
        # 配置卡片区域的行列权重
        for i in range(2):  # 2行
            self.cards_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for i in range(2):  # 2列
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # 创建功能卡片
        self.create_feature_cards()
        
        # 底部状态栏
        self.statusbar = tk.Frame(self.main_frame, bg=COLORS["bg_medium"], height=30)
        self.statusbar.grid(row=2, column=0, sticky="ew")
        
        status_label = tk.Label(
            self.statusbar, 
            text="© 2025 数学可视化教学平台", 
            font=FONTS["small"], 
            bg=COLORS["bg_medium"], 
            fg=COLORS["text_secondary"]
        )
        status_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def create_feature_cards(self):
        """创建主要功能卡片 - 实现响应式布局"""
        # 定义卡片数据
        cards_data = [
            {
                "title": "高等数学",
                "desc": "函数、微积分、微分方程等交互式可视化",
                "icon": "gaoshup.ico",  # 高等数学图标
                "color": COLORS["accent_primary"],
                "command": self.open_advanced_math
            },
            {
                "title": "线性代数",
                "desc": "矩阵运算、特征值分析等直观呈现",
                "icon": "xiandaip.ico",  # 线性代数图标
                "color": "#00B5FF",
                "command": self.open_linear_algebra
            },
            {
                "title": "概率统计",
                "desc": "概率分布、统计分析可视化与模拟",
                "icon": "gailvp.ico",  # 概率统计图标
                "color": "#7B68EE",
                "command": self.open_probability
            },
            {
                "title": "AI 数据分析",
                "desc": "基于人工智能的数据分析与预测",
                "icon": "AIP.ico",  # AI数据分析图标
                "color": "#00F5A0",
                "command": self.open_ai_analyzer
            }
        ]

        # 使用相对尺寸确保响应式布局
        base_width = self.content_frame.winfo_width() // 2 - 60 if self.content_frame.winfo_width() > 0 else 220
        base_height = int(base_width * 1.2)  # 保持黄金比例并确保为整数
        card_spacing = 30   # 均匀间距
        
        # 清除旧卡片
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        self.cards = []  # 保存卡片引用以避免垃圾回收
        
        # 创建卡片网格 - 使用Grid确保自适应
        # 检测窗口宽度以决定布局模式
        small_screen = self.root.winfo_width() < 800
        
        for i, card_data in enumerate(cards_data):
            # 根据窗口大小决定布局
            if small_screen:  # 小屏幕时单列排列
                row, col = i, 0
            else:  # 大屏幕时双列排列
                row, col = divmod(i, 2)
            
            # 使用响应式尺寸
            card_width = base_width
            card_height = base_height
            
            # 创建卡片容器框架 - 用于添加红色边框
            card_container = tk.Frame(
                self.cards_frame,
                bg=COLORS["bg_light"],
                highlightbackground=COLORS["accent_secondary"],  # 默认无边框，悬停时显示
                highlightthickness=0,
                cursor="hand2"
            )
            
            # 设置边距
            x_padding = card_spacing // 2
            y_padding = card_spacing // 2
            
            # 放置容器
            card_container.grid(
                row=row, 
                column=col, 
                padx=x_padding, 
                pady=y_padding, 
                sticky="nsew"  # 确保填充整个单元格
            )
            
            # 创建卡片
            card = InteractiveCard(
                parent=card_container,
                title=card_data["title"],
                description=card_data["desc"],
                icon_path=card_data["icon"],
                color=card_data["color"],
                command=card_data["command"],
                width=card_width,
                height=card_height,
                style="clickable"  # 修改为可点击样式
            )
            card.pack(fill=tk.BOTH, expand=True)
            
            # 确保容器本身也可点击
            card_container.bind("<Button-1>", lambda e, cmd=card_data["command"]: cmd())
            
            # 递归绑定容器内所有子组件的点击事件
            self.bind_all_children(card_container, card_data["command"])
            
            # 保存卡片引用
            self.cards.append((card_container, card))
        
        # 注册窗口大小变化事件
        def on_resize(event):
            # 如果窗口宽度变化超过阈值，重新创建卡片
            if (event.widget == self.root and 
                (self.root.winfo_width() < 800 and len(self.cards) > 0 and self.cards[0][0].grid_info()['column'] == 1 or
                 self.root.winfo_width() >= 800 and len(self.cards) > 0 and self.cards[1][0].grid_info()['column'] == 0)):
                self.root.after(100, self.create_feature_cards)
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", on_resize)

    def open_advanced_math(self):
        """打开高等数学选择器"""
        open_app_window(self, AdvancedMathSelector, "高等数学可视化工具", "800x600")

    def open_linear_algebra(self):
        open_app_window(self, LinearAlgebraApp, "线性代数可视化", "1000x700")

    def open_probability(self):
        open_app_window(self, ProbabilityTheoryApp, "概率论与数理统计可视化", "1000x700")

    def bind_all_children(self, parent, command):
        """递归绑定所有子组件的点击事件"""
        for child in parent.winfo_children():
            if isinstance(child, (tk.Frame, tk.Label, tk.Canvas)) and not isinstance(child, FuturisticButton):
                child.config(cursor="hand2")  # 统一设置手型光标
                child.bind("<Button-1>", lambda e, cmd=command: cmd())
                
                # 递归绑定嵌套组件
                if isinstance(child, tk.Frame):
                    self.bind_all_children(child, command)
                    
    def close_current_window(self): # Add this method
        """Closes the currently open sub-application window."""
        if self.current_window and self.current_window.winfo_exists():
            log(f"MainApp closing window: {self.current_window.title()}")
            self.current_window.destroy()
        self.current_window = None
    
    def open_ai_analyzer(self):
        """打开AI数据分析器"""
        analyzer_window = tk.Toplevel(self.root)
        analyzer_window.title("AI 数据分析")
        DataAnalyzerGUI(analyzer_window)
        self.current_window = analyzer_window

class AdvancedMathSelector(StandardCourseUI):
    def __init__(self, root):
        # 收集模块按钮数据
        button_data = []
        
        # 安全地添加按钮，不管模块是否存在
        # 函数可视化分析
        button_data.append(("函数图像分析", self.create_safe_handler('TrigPlotApp', "函数图像分析")))
        
        # 数列分析工具
        button_data.append(("数列分析工具", self.create_safe_handler('SequenceModule', "数列分析工具")))
        
        # 微分方程可视化
        button_data.append(("微分方程", self.create_safe_handler('DirectionFieldApp', "微分方程")))
        
        # 方程可视化工具
        button_data.append(("方程图像分析", self.create_safe_handler('FangApp', "方程图像分析")))
        
        # 科赫曲线可视化
        button_data.append(("科赫曲线", self.create_safe_handler('KeheApp', "科赫曲线")))
        
        # 海森矩阵分析
        button_data.append(("海森矩阵分析", self.create_safe_handler('HessianApp', "海森矩阵分析")))
        
        # 调用父类初始化 - 使用复杂模式支持滚动
        super().__init__(
            root=root,
            title="高等数学可视化工具集",
            button_data=button_data,
            course_type="complex"  # 使用带滚动条的布局
        )
        
        # 更新返回按钮命令
        self.return_button.config(command=self.return_to_main_menu)
    
    def create_safe_handler(self, module_name, title):
        """创建安全的模块处理函数，通过字符串引用模块"""
        def handler():
            try:
                # 尝试从全局变量中获取模块类
                module_class = globals().get(module_name)
                if module_class is not None:
                    open_app_window(self, module_class, title)
                else:
                    messagebox.showerror("模块错误", f"无法加载 {title} 模块\n请确保模块 {module_name} 已正确导入。")
            except Exception as e:
                messagebox.showerror("错误", f"启动 {title} 时出错: {str(e)}")
        return handler
    
    def return_to_main_menu(self):
        """返回主菜单"""
        self.root.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    log("启动主应用程序...")
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
