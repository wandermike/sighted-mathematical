import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import warnings
from knowledge import KnowledgeLearningClass

# Suppress specific warnings if needed (e.g., from SymPy)
warnings.filterwarnings("ignore", category=UserWarning, module='sympy')

# Set default font for Matplotlib to support Chinese
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False # Ensure minus sign displays correctly

class TrigPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高等数学可视化工具 - 函数分析")
        self.root.geometry("1200x800")

        # 初始化变量 - 合并所有初始化到一处
        self.dragging = False
        self.drag_start = None
        self.animation_running = False
        self.current_anim = None
        
        # 初始化所有需要的属性
        self.user_function = None  # 存储用户函数
        self.taylor_function = None  # 存储泰勒近似曲线函数
        self.taylor_order = 3  # 初始泰勒级数阶数
        self.taylor_center_var = tk.StringVar(value="0.0") # 添加展开点变量
        self.taylor = []  # 存储泰勒曲线
        
        self.rects = []  # 存储矩形对象的列表
        self.line = None  # 用于存储连接两点的直线
        self.points = []  # 用于存储标记点
        self.division_points = []  # 存储分割点
        self.division_line = None  # 用于存储分割点连接线
        
        # 初始化x1和x2的值
        self.x1 = 0.0
        self.x2 = 0.0
        
        # 初始化防抖计时器
        self.rectangle_update_timer = None
        self.taylor_update_timer = None

        # 添加控制变量
        self.draw_rectangles = tk.BooleanVar(value=False)  # 控制是否绘制矩形
        self.draw_taylor = tk.BooleanVar(value=False)  # 控制是否绘制泰勒曲线
        self.draw_tangent = tk.BooleanVar(value=False)  # 控制是否绘制切线
        self.draw_division = tk.BooleanVar(value=False)  # 控制是否绘制分割点连接线

        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="高等数学可视化", font=("SimHei", 18, "bold"))
        title_label.pack(pady=5)

        # 创建上下分割的界面
        # 1. 上部分：控制区域
        self.control_area = ttk.Frame(main_frame)
        self.control_area.pack(fill=tk.X, pady=5)
        
        # 2. 下部分：图表和信息区域
        self.display_area = ttk.Frame(main_frame)
        self.display_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建控制区域
        self.create_control_area(self.control_area)

        # 创建显示区域
        self.create_display_area(self.display_area)
        
        # 绑定鼠标事件
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_scroll = self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # 绑定视图变化事件
        self.cid_xlim_change = self.ax.callbacks.connect('xlim_changed', self.on_xlim_change)
        
        # 初始绘制
        self.draw_user_function() # 初始绘制一次

        self.knowledge_learner = KnowledgeLearningClass()

    def create_control_area(self, parent):
        """创建上部操作区域，包括按钮行和动态控制面板"""
        # 1. 创建按钮行框架
        button_bar = ttk.Frame(parent)
        button_bar.pack(fill=tk.X, pady=5)

        # 2. 创建动态控制面板框架 (用于切换不同功能的控件)
        self.dynamic_control_panel = ttk.Frame(parent, padding=5)
        self.dynamic_control_panel.pack(fill=tk.X, expand=True)

        # 3. 定义按钮及其对应的功能标识符
        features = {
            "函数设置": "function",
            "矩形积分": "rectangles",
            "泰勒展开": "taylor",
            "分割线": "division",
            "切线": "tangent"
        }
        
        # 设置按钮样式
        button_style = {
            'font': ('SimHei', 11),
            'relief': 'raised',
            'bg': '#4A90E2',
            'fg': 'white',
            'padx': 10,
            'pady': 5,
            'cursor': 'hand2',
            'width': 10,
            'borderwidth': 2
        }

        # 4. 创建按钮并放置在按钮行框架中
        for text, feature_id in features.items():
            button = tk.Button(
                button_bar,
                text=text,
                command=lambda fid=feature_id: self.switch_control_view(fid),
                **button_style
            )
            button.pack(side=tk.LEFT, padx=5, pady=5)

        # 5. 初始化控制面板状态
        self.control_frames = {}  # 用于存储已创建的控制面板
        self.current_control_frame = None  # 当前显示的控制面板
        
        # 默认显示函数设置面板
        self.switch_control_view("function")

    def create_display_area(self, parent):
        """创建下部显示区域，包括图表和函数信息"""
        # 创建水平分割面板
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 1. 左侧：图表区域
        plot_frame = ttk.LabelFrame(paned, text="函数图像", padding=10)
        paned.add(plot_frame, weight=3)  # 图表区域占更多空间
        
        # 创建matplotlib图表
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_xlabel('x', fontproperties=FontProperties(family='SimHei', size=12))
        self.ax.set_ylabel('y', fontproperties=FontProperties(family='SimHei', size=12))
        self.ax.set_title('函数图像', fontproperties=FontProperties(family='SimHei', size=14, weight='bold'))
        
        # 创建画布并添加到图表框架
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加matplotlib工具栏
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        
        # 2. 右侧：函数信息区域
        info_frame = ttk.LabelFrame(paned, text="函数信息", padding=10)
        paned.add(info_frame, weight=1)  # 信息区域占较少空间
        
        # 创建函数信息文本框
        self.info_text = tk.Text(info_frame, wrap=tk.WORD, width=30, height=20, font=("SimHei", 10))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        # 初始化信息文本
        self.update_function_info("尚未绘制函数")

    def switch_control_view(self, feature_id):
        """切换控制面板视图"""
        # 如果当前有显示的控制面板，先隐藏它
        if self.current_control_frame:
            self.current_control_frame.pack_forget()
        
        # 如果请求的控制面板已经创建，则显示它
        if feature_id in self.control_frames:
            self.control_frames[feature_id].pack(fill=tk.X, expand=True, pady=5)
            self.current_control_frame = self.control_frames[feature_id]
        else:
            # 否则，创建新的控制面板
            new_frame = self._create_specific_control_frame(feature_id, self.dynamic_control_panel)
            if new_frame:
                self.control_frames[feature_id] = new_frame
                new_frame.pack(fill=tk.X, expand=True, pady=5)
                self.current_control_frame = new_frame

    def _create_specific_control_frame(self, feature_id, parent):
        """根据 feature_id 调用相应的创建函数"""
        if feature_id == "function":
            return self._create_function_controls(parent)
        elif feature_id == "rectangles":
            return self._create_rectangle_controls(parent)
        elif feature_id == "taylor":
            return self._create_taylor_controls(parent)
        elif feature_id == "division":
            return self._create_division_controls(parent)
        elif feature_id == "tangent":
            return self._create_tangent_controls(parent)
        else:
            return None # 对于未知的 feature_id 返回 None

    def _create_function_controls(self, parent):
        """创建函数设置面板"""
        frame = ttk.LabelFrame(parent, text="函数设置", padding=10)
        
        # 函数输入行
        function_frame = ttk.Frame(frame)
        function_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(function_frame, text="函数表达式:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)
        self.function_entry = ttk.Entry(function_frame, width=30, font=("SimHei", 10))
        self.function_entry.pack(side=tk.LEFT, padx=5)
        self.function_entry.insert(0, "sin(x)")  # 设置默认函数为sin(x)
        
        draw_button = ttk.Button(function_frame, text="绘制", command=self.draw_user_function)
        draw_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(function_frame, text="清除", command=self.clear_plot)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 坐标范围设置
        range_frame = ttk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(range_frame, text="x范围:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)
        self.xmin_entry = ttk.Entry(range_frame, width=10, font=("SimHei", 10))
        self.xmin_entry.pack(side=tk.LEFT, padx=5)
        self.xmin_entry.insert(0, "a=-10")
        
        ttk.Label(range_frame, text="到", font=("SimHei", 10)).pack(side=tk.LEFT)
        self.xmax_entry = ttk.Entry(range_frame, width=10, font=("SimHei", 10))
        self.xmax_entry.pack(side=tk.LEFT, padx=5)
        self.xmax_entry.insert(0, "b=10")
        
        update_range_button = ttk.Button(range_frame, text="更新范围", command=self.update_plot_range)
        update_range_button.pack(side=tk.LEFT, padx=5)
        
        return frame

    def _create_rectangle_controls(self, parent):
        """创建矩形积分控制面板"""
        frame = ttk.LabelFrame(parent, text="矩形积分控制", padding=10)

        # 矩形数量控制
        rect_control_frame = ttk.Frame(frame)
        rect_control_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rect_control_frame, text="矩形数:").pack(side=tk.LEFT)
        self.rectangles_slider = ttk.Scale(
            rect_control_frame, from_=1, to=100, orient=tk.HORIZONTAL,
            command=lambda x: self.debounced_update_rectangles(float(x))
        )
        self.rectangles_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.rectangles_slider.set(10)
        self.rectangles_label = ttk.Label(rect_control_frame, text="矩形数：10")
        self.rectangles_label.pack(side=tk.LEFT, padx=5)

        # 矩形范围输入
        range_frame = ttk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=5)
        ttk.Label(range_frame, text="积分范围:").pack(side=tk.LEFT)
        
        self.rect_min_entry = ttk.Entry(range_frame, width=8)
        self.rect_min_entry.pack(side=tk.LEFT, padx=5)
        self.rect_min_entry.insert(0, "-10")
        
        ttk.Label(range_frame, text="到").pack(side=tk.LEFT)
        
        self.rect_max_entry = ttk.Entry(range_frame, width=8)
        self.rect_max_entry.pack(side=tk.LEFT, padx=5)
        self.rect_max_entry.insert(0, "10")
        
        update_range_button = ttk.Button(
            range_frame, text="更新范围", 
            command=lambda: self.update_rectangles(self.rectangles_slider.get())
        )
        update_range_button.pack(side=tk.LEFT, padx=5)

        # 矩形显示开关
        self.rectangles_check = ttk.Checkbutton(
            frame, text="显示矩形", variable=self.draw_rectangles, command=self.toggle_rectangles
        )
        self.rectangles_check.pack(anchor=tk.W, pady=5)
        
        # 积分结果显示
        integral_frame = ttk.Frame(frame)
        integral_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(integral_frame, text="矩形面积:").pack(side=tk.LEFT, padx=5)
        self.area_text = tk.Text(integral_frame, height=1, width=15, font=("SimHei", 10))
        self.area_text.pack(side=tk.LEFT, padx=5)
        self.area_text.insert(tk.END, "未计算")
        self.area_text.config(state=tk.DISABLED)
        
        ttk.Label(integral_frame, text="定积分:").pack(side=tk.LEFT, padx=(15, 5))
        self.integral_text = tk.Text(integral_frame, height=1, width=15, font=("SimHei", 10))
        self.integral_text.pack(side=tk.LEFT, padx=5)
        self.integral_text.insert(tk.END, "未计算")
        self.integral_text.config(state=tk.DISABLED)
        
        calc_integral_btn = ttk.Button(
            integral_frame, 
            text="计算积分", 
            command=self.calculate_integral
        )
        calc_integral_btn.pack(side=tk.LEFT, padx=10)

        knowledge_learning_integral_frame = ttk.Frame(frame)
        knowledge_learning_integral_frame.pack(fill=tk.X, pady=5)

        knowledge_learning = ttk.Button(
            knowledge_learning_integral_frame,
            text="知识介绍", 
            command=self.knowledge_learner.knowledge_learning_1_function  # 去掉括号，传递方法引用
        )
        knowledge_learning.pack(side=tk.LEFT, padx=10)

        return frame

    def _create_taylor_controls(self, parent):
        """创建泰勒展开控制面板"""
        frame = ttk.LabelFrame(parent, text="泰勒展开控制", padding=10)
        
        # 展开点输入
        center_frame = ttk.Frame(frame)
        center_frame.pack(fill=tk.X, pady=5)
        ttk.Label(center_frame, text="展开点:").pack(side=tk.LEFT)
        self.taylor_center_entry = ttk.Entry(center_frame, width=15, textvariable=self.taylor_center_var)
        self.taylor_center_entry.pack(side=tk.LEFT, padx=5)
        self.taylor_center_entry.bind("<Return>", lambda event: self._update_taylor())
        
        # 阶数控制
        order_frame = ttk.Frame(frame)
        order_frame.pack(fill=tk.X, pady=5)
        ttk.Label(order_frame, text="展开阶数:").pack(side=tk.LEFT)
        
        # 修改滑块，添加值变化时的回调
        self.taylor_slider = ttk.Scale(
            order_frame, 
            from_=1, 
            to=10, 
            orient=tk.HORIZONTAL, 
            command=lambda x: self._on_taylor_slider_change(x)
        )
        self.taylor_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.taylor_slider.set(3)  # 默认3阶
        self.taylor_label = ttk.Label(order_frame, text="阶数：3")
        self.taylor_label.pack(side=tk.LEFT, padx=5)
        
        # 泰勒展开显示开关
        self.taylor_check = ttk.Checkbutton(
            frame, text="显示泰勒展开", variable=self.draw_taylor, command=self.toggle_taylor
        )
        self.taylor_check.pack(anchor=tk.W, pady=5)
        
        # 泰勒公式显示
        formula_frame = ttk.Frame(frame)
        formula_frame.pack(fill=tk.X, pady=5)
        ttk.Label(formula_frame, text="泰勒公式:").pack(side=tk.LEFT)
        
        # 使用Text控件显示公式
        self.taylor_formula_text = tk.Text(formula_frame, height=3, width=50, wrap=tk.WORD, font=("SimHei", 10))
        self.taylor_formula_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.taylor_formula_text.insert(tk.END, "点击\“显示泰勒展开\”查看公式")
        self.taylor_formula_text.config(state=tk.DISABLED)

        knowledge_learning_integral_frame = ttk.Frame(frame)
        knowledge_learning_integral_frame.pack(fill=tk.X, pady=5)

        knowledge_learning= ttk.Button(
            knowledge_learning_integral_frame,
            text="知识介绍", 
            command=self.knowledge_learner.knowledge_learning_2_function
        )
        knowledge_learning.pack(side=tk.LEFT, padx=10)
        
        return frame

    def _create_division_controls(self, parent):
        """创建分割线控制面板"""
        frame = ttk.LabelFrame(parent, text="分割线控制", padding=10)
        
        # 分割点数量控制
        division_control_frame = ttk.Frame(frame)
        division_control_frame.pack(fill=tk.X, pady=5)
        ttk.Label(division_control_frame, text="分割点数:").pack(side=tk.LEFT)
        self.division_slider = ttk.Scale(
            division_control_frame, from_=2, to=100, orient=tk.HORIZONTAL,
            command=lambda x: self.update_division(float(x))
        )
        self.division_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.division_slider.set(10)
        self.division_label = ttk.Label(division_control_frame, text="分割点数：10")
        self.division_label.pack(side=tk.LEFT, padx=5)

        # 分割范围输入
        range_frame = ttk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=5)
        ttk.Label(range_frame, text="范围:").pack(side=tk.LEFT)
        
        self.division_min_entry = ttk.Entry(range_frame, width=8)
        self.division_min_entry.pack(side=tk.LEFT, padx=5)
        self.division_min_entry.insert(0, "-10")
        
        ttk.Label(range_frame, text="到").pack(side=tk.LEFT)
        
        self.division_max_entry = ttk.Entry(range_frame, width=8)
        self.division_max_entry.pack(side=tk.LEFT, padx=5)
        self.division_max_entry.insert(0, "10")
        
        update_range_button = ttk.Button(
            range_frame, text="更新范围", 
            command=lambda: self.update_division(self.division_slider.get())
        )
        update_range_button.pack(side=tk.LEFT, padx=5)

        # 分割点连接线显示开关
        self.division_check = ttk.Checkbutton(
            frame, text="显示分割点连接线", variable=self.draw_division, command=self.toggle_division
        )
        self.division_check.pack(anchor=tk.W, pady=5)
        
        # 连接线长度显示
        length_frame = ttk.Frame(frame)
        length_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(length_frame, text="连接线长度:").pack(side=tk.LEFT, padx=5)
        self.length_text = tk.Text(length_frame, height=1, width=15, font=("SimHei", 10))
        self.length_text.pack(side=tk.LEFT, padx=5)
        self.length_text.insert(tk.END, "未计算")
        self.length_text.config(state=tk.DISABLED)

        knowledge_learning_integral_frame = ttk.Frame(frame)
        knowledge_learning_integral_frame.pack(fill=tk.X, pady=5)

        knowledge_learning= ttk.Button(
            knowledge_learning_integral_frame,
            text="知识介绍", 
            command=self.knowledge_learner.knowledge_learning_3_function
        )
        knowledge_learning.pack(side=tk.LEFT, padx=10)

        return frame

    def _create_tangent_controls(self, parent):
        """创建切线控制面板"""
        frame = ttk.LabelFrame(parent, text="切线控制", padding=10)
        
        # x1输入
        x1_frame = ttk.Frame(frame)
        x1_frame.pack(fill=tk.X, pady=5)
        ttk.Label(x1_frame, text="切点x坐标:").pack(side=tk.LEFT)
        self.x1_entry = ttk.Entry(x1_frame, width=15)
        self.x1_entry.pack(side=tk.LEFT, padx=5)
        self.x1_entry.insert(0, "x1=0")
        self.x1_entry.bind("<Return>", lambda event: self.update_x1())
        
        # 切线显示开关
        self.tangent_check = ttk.Checkbutton(
            frame, text="显示切线", variable=self.draw_tangent, command=self.toggle_tangent
        )
        self.tangent_check.pack(anchor=tk.W, pady=5)
        
        # 切线方程显示
        equation_frame = ttk.Frame(frame)
        equation_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(equation_frame, text="切线方程:").pack(side=tk.LEFT, padx=5)
        self.tangent_equation_text = tk.Text(equation_frame, height=1, width=30, font=("SimHei", 10))
        self.tangent_equation_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.tangent_equation_text.insert(tk.END, "未计算")
        self.tangent_equation_text.config(state=tk.DISABLED)

        knowledge_learning_integral_frame = ttk.Frame(frame)
        knowledge_learning_integral_frame.pack(fill=tk.X, pady=5)

        knowledge_learning= ttk.Button(knowledge_learning_integral_frame,text="知识介绍", command=self.knowledge_learner.knowledge_learning_4_function)
        knowledge_learning.pack(side=tk.LEFT, padx=10)

        return frame

    def update_function_info(self, info_text):
        """更新函数信息区域"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)

    def clear_plot(self):
        """清除绘图区中的所有绘图元素"""
        try:
            # 清除用户函数曲线
            if hasattr(self, 'func_line') and self.func_line:
                self.func_line.remove()
                self.func_line = None

            # 如果有泰勒曲线，清除它
            if hasattr(self, 'taylor_plot') and self.taylor_plot:
                self.taylor_plot.remove()
                self.taylor_plot = None

            # 如果有切线，清除它
            if hasattr(self, 'line') and self.line:
                self.line.remove()
                self.line = None
                
            # 清除矩形
            self.clear_rectangles()
            
            # 清除分割线
            self.clear_division()
            
            # 更新函数信息
            self.update_function_info("已清除所有图形")
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("清除错误", f"清除绘图时出错: {str(e)}")

    def draw_user_function(self):
        """绘制用户输入的函数"""
        try:
            # 解析函数表达式
            func_expr = self.function_entry.get() if hasattr(self, 'function_entry') else "sin(x)"
            
            # 创建函数
            x = sp.Symbol('x')
            expr = parse_expr(func_expr, transformations=(standard_transformations + (implicit_multiplication_application,)))
            
            # 将sympy表达式转换为可计算的Python函数
            func_lambda = sp.lambdify(x, expr, modules=['numpy'])
            self.user_function = func_lambda  # 保存函数引用，以便其他方法使用
            
            # 获取绘图范围
            xlim = self.ax.get_xlim()
            x_vals = np.linspace(xlim[0], xlim[1], 1000)  # 使用1000个点来绘制平滑曲线
            
            # 计算y值 - 使用try/except捕获可能的计算错误
            y_vals = []
            for x_val in x_vals:
                try:
                    y_vals.append(func_lambda(x_val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    y_vals.append(np.nan)  # 对于无法计算的点，使用NaN
            
            # 更新或创建函数曲线
            if hasattr(self, 'func_line') and self.func_line:
                self.func_line.set_data(x_vals, y_vals)
            else:
                self.func_line, = self.ax.plot(x_vals, y_vals, 'b-', linewidth=2)
            
            # 更新图表范围
            self.update_plot_limits()
            self.canvas.draw()
            
            # 更新函数信息
            func_info = f"函数: {func_expr}\n\n"
            func_info += f"定义域: 实数域 (可能有特殊点需要排除)\n\n"
            
            # 尝试计算一些函数特性
            try:
                derivative = sp.diff(expr, x)
                func_info += f"导函数: {derivative}\n\n"
            except:
                func_info += "导函数: 无法计算\n\n"
                
            try:
                critical_points = sp.solve(derivative, x)
                if critical_points:
                    func_info += f"临界点: {', '.join(str(p) for p in critical_points)}\n\n"
                else:
                    func_info += "临界点: 无\n\n"
            except:
                func_info += "临界点: 无法计算\n\n"
                
            self.update_function_info(func_info)
            
        except Exception as e:
            messagebox.showerror("函数错误", f"绘制函数时出错: {str(e)}")
            print(f"绘制函数时出错: {str(e)}")

    def update_plot_range(self):
        """更新绘图范围"""
        try:
            # 解析x范围输入
            a_input = self.xmin_entry.get()
            b_input = self.xmax_entry.get()
            
            # 提取a和b的值
            try:
                a = float(a_input.split('=')[1].strip())
                b = float(b_input.split('=')[1].strip())
            except (ValueError, IndexError):
                messagebox.showerror("输入错误", "请输入有效的范围值，例如: a=-10, b=10")
                return
            
            if a >= b:
                messagebox.showerror("范围错误", "左边界必须小于右边界")
                return
            
            # 设置新的x轴范围
            self.ax.set_xlim(a, b)
            
            # 如果已经有函数，重新绘制
            if hasattr(self, 'user_function') and self.user_function:
                self.draw_user_function()
            else:
                self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("范围更新错误", f"更新绘图范围时出错: {str(e)}")

    def update_plot_limits(self):
        """更新图表的y轴范围，以适应当前的函数"""
        try:
            if not hasattr(self, 'func_line') or self.func_line is None:
                return
            
            # 获取当前x轴范围
            xlim = self.ax.get_xlim()
            
            # 在当前x轴范围内计算y值
            x_vals = np.linspace(xlim[0], xlim[1], 1000)
            y_vals = []
            
            for x_val in x_vals:
                try:
                    y_vals.append(self.user_function(x_val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    y_vals.append(np.nan)
            
            # 过滤掉无效值
            valid_y = [y for y in y_vals if not (np.isnan(y) or np.isinf(y))]
            
            if valid_y:
                # 计算y轴范围
                y_min, y_max = min(valid_y), max(valid_y)
                y_range = y_max - y_min
                
                # 设置y轴范围，添加一些边距
                if y_range > 0:
                    self.ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
                else:
                    # 如果y值都相同，设置一个默认范围
                    self.ax.set_ylim(y_min - 1, y_min + 1)
        except Exception as e:
            print(f"更新图表范围时出错: {str(e)}")

    def on_press(self, event):
        """处理鼠标按下事件"""
        if event.inaxes != self.ax:
            return
        
        self.dragging = True
        self.drag_start = (event.xdata, event.ydata)

    def on_move(self, event):
        """处理鼠标移动事件"""
        if not self.dragging or event.inaxes != self.ax:
            return
        
        # 可以在这里添加拖动时的逻辑

    def on_release(self, event):
        """处理鼠标释放事件"""
        self.dragging = False
        
        if event.inaxes != self.ax:
            return
        
        # 可以在这里添加鼠标释放时的逻辑

    def on_scroll(self, event):
        """处理鼠标滚轮事件"""
        if event.inaxes != self.ax:
            return
        
        # 获取当前x轴和y轴范围
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        
        # 计算范围的中心点
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        # 计算新的范围
        zoom_factor = 0.9 if event.button == 'up' else 1.1
        
        new_x_min = x_center - (x_center - x_min) * zoom_factor
        new_x_max = x_center + (x_max - x_center) * zoom_factor
        new_y_min = y_center - (y_center - y_min) * zoom_factor
        new_y_max = y_center + (y_max - y_center) * zoom_factor
        
        # 设置新的范围
        self.ax.set_xlim(new_x_min, new_x_max)
        self.ax.set_ylim(new_y_min, new_y_max)
        
        # 重新绘制
        self.canvas.draw_idle()

    def on_xlim_change(self, ax):
        """处理x轴范围变化事件"""
        # 如果有用户函数，重新绘制
        if hasattr(self, 'user_function') and self.user_function:
            # 获取当前x轴范围
            xlim = self.ax.get_xlim()
            
            # 重新计算函数值
            x_vals = np.linspace(xlim[0], xlim[1], 1000)
            y_vals = []
            
            for x_val in x_vals:
                try:
                    y_vals.append(self.user_function(x_val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    y_vals.append(np.nan)
            
            # 更新函数曲线
            if hasattr(self, 'func_line') and self.func_line:
                self.func_line.set_data(x_vals, y_vals)
            
            # 更新其他可能的图形元素
            # 例如：更新矩形、泰勒曲线等
            
            # 重新绘制
            self.canvas.draw_idle()

    def toggle_rectangles(self):
        """切换是否显示矩形"""
        if self.draw_rectangles.get():
            self.update_rectangles(self.rectangles_slider.get())
        else:
            self.clear_rectangles()
            self.canvas.draw()

    def clear_rectangles(self):
        """清除所有矩形"""
        for rect in self.rects:
            rect.remove()
        self.rects = []

    def toggle_taylor(self):
        """切换是否显示泰勒展开"""
        if self.draw_taylor.get():
            self._update_taylor()
        else:
            if hasattr(self, 'taylor_plot') and self.taylor_plot:
                self.taylor_plot.remove()
                self.taylor_plot = None
                self.canvas.draw()

    def toggle_division(self):
        """切换是否显示分割线"""
        if self.draw_division.get():
            self.update_division(self.division_slider.get())
        else:
            self.clear_division()
            self.canvas.draw()

    def clear_division(self):
        """清除分割线"""
        for point in self.division_points:
            point.remove()
        self.division_points = []
        
        if self.division_line:
            self.division_line.remove()
            self.division_line = None

    def toggle_tangent(self):
        """切换是否显示切线"""
        if self.draw_tangent.get():
            self.update_x1()
        else:
            if self.line:
                self.line.remove()
                self.line = None
                self.canvas.draw()

    def update_x1(self):
        """更新x1值并绘制切线"""
        try:
            # 解析x1输入
            x1_input = self.x1_entry.get()
            
            # 提取x1的值
            try:
                x1 = float(x1_input.split('=')[1].strip())
            except (ValueError, IndexError):
                messagebox.showerror("输入错误", "请输入有效的x1值，例如: x1=0")
                return
            
            self.x1 = x1
            self.draw_tangent_line()
            
        except Exception as e:
            messagebox.showerror("切线错误", f"更新切线时出错: {str(e)}")

    def draw_tangent_line(self):
        """绘制切线"""
        if not hasattr(self, 'user_function') or self.user_function is None:
            messagebox.showinfo("提示", "请先输入并绘制函数")
            return
        
        try:
            # 计算函数在x1处的值和导数
            x1 = self.x1
            y1 = self.user_function(x1)
            
            # 使用数值方法计算导数
            h = 1e-6  # 小增量
            slope = (self.user_function(x1 + h) - self.user_function(x1 - h)) / (2 * h)
            
            # 获取当前x轴范围
            xlim = self.ax.get_xlim()
            width = xlim[1] - xlim[0]
            
            # 计算切线的两个端点
            x_left = x1 - width/4
            x_right = x1 + width/4
            y_left = y1 + slope * (x_left - x1)
            y_right = y1 + slope * (x_right - x1)
            
            # 清除旧的切线
            if self.line:
                self.line.remove()
            
            # 绘制新的切线
            self.line, = self.ax.plot([x_left, x_right], [y_left, y_right], 'r-', linewidth=2)
            
            # 更新切线方程显示
            if hasattr(self, 'tangent_equation_text'):
                self.tangent_equation_text.config(state=tk.NORMAL)
                self.tangent_equation_text.delete(1.0, tk.END)
                self.tangent_equation_text.insert(tk.END, f"y - {y1:.4f} = {slope:.4f}(x - {x1:.4f})")
                self.tangent_equation_text.config(state=tk.DISABLED)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("切线错误", f"绘制切线时出错: {str(e)}")
            if self.line:
                self.line.remove()
                self.line = None
                self.canvas.draw()

    def debounced_update_rectangles(self, value):
        """防抖更新矩形"""
        # 确保矩形数至少为1
        value = max(1, int(value))
        
        # 更新标签
        self.rectangles_label.config(text=f"矩形数：{value}")
        
        # 取消之前的计时器
        if self.rectangle_update_timer:
            self.root.after_cancel(self.rectangle_update_timer)
        
        # 设置新的计时器
        self.rectangle_update_timer = self.root.after(300, lambda: self.update_rectangles(value))

    def update_rectangles(self, num_rectangles=None):
        """更新矩形积分近似"""
        try:
            if not hasattr(self, 'user_function') or self.user_function is None:
                messagebox.showinfo("提示", "请先输入并绘制函数")
                return
            
            # 获取积分范围
            try:
                # 尝试从矩形范围输入框获取值
                a = float(self.rect_min_entry.get())
                b = float(self.rect_max_entry.get())
            except (ValueError, AttributeError):
                # 如果输入无效或输入框不存在，使用函数范围输入框的值
                try:
                    a = float(self.xmin_entry.get().split('=')[1].strip())
                    b = float(self.xmax_entry.get().split('=')[1].strip())
                except (ValueError, IndexError, AttributeError):
                    # 如果仍然无效，使用当前x轴范围
                    xlim = self.ax.get_xlim()
                    a, b = xlim[0], xlim[1]
                
                # 如果有矩形范围输入框，更新其值
                if hasattr(self, 'rect_min_entry'):
                    self.rect_min_entry.delete(0, tk.END)
                    self.rect_min_entry.insert(0, str(a))
                if hasattr(self, 'rect_max_entry'):
                    self.rect_max_entry.delete(0, tk.END)
                    self.rect_max_entry.insert(0, str(b))
            
            # 确保a < b
            if a >= b:
                messagebox.showerror("范围错误", "左边界必须小于右边界")
                return
            
            # 如果提供了矩形数量，更新滑块和标签
            if num_rectangles is not None:
                num_rectangles = int(num_rectangles)
                if hasattr(self, 'rectangles_slider'):
                    self.rectangles_slider.set(num_rectangles)
                if hasattr(self, 'rectangles_label'):
                    self.rectangles_label.config(text=f"每10单位矩形数：{num_rectangles}")
            else:
                # 否则使用滑块的当前值
                num_rectangles = int(self.rectangles_slider.get())
            
            # 清除现有的矩形
            self.clear_rectangles()
            
            # 如果不显示矩形，则直接返回
            if not self.draw_rectangles.get():
                return
            
            # 计算实际的矩形数量（基于区间长度）
            interval_length = abs(b - a)
            total_rectangles = int(num_rectangles * interval_length / 10)
            total_rectangles = max(1, total_rectangles)  # 确保至少有1个矩形
            
            # 计算矩形宽度
            width = (b - a) / total_rectangles
            
            # 计算每个矩形的高度（使用矩形中点的函数值）
            heights = []
            for i in range(total_rectangles):
                x = a + i * width
                x_mid = x + width/2  # 计算矩形的中点x坐标
                try:
                    height = self.user_function(x_mid)  # 使用中点计算高度
                    if np.isnan(height) or np.isinf(height):
                        height = 0
                    heights.append(height)
                except (ValueError, ZeroDivisionError, OverflowError):
                    heights.append(0)
            
            # 绘制矩形
            total_area = 0
            for i in range(total_rectangles):
                x = a + i * width
                height = heights[i]
                
                # 计算矩形面积
                area = width * height
                total_area += area
                
                # 绘制矩形
                if height >= 0:
                    rect = plt.Rectangle((x, 0), width, height, 
                                        facecolor='blue', alpha=0.3, edgecolor='blue')
                    # 在矩形顶部中点绘制一个小点
                    self.ax.plot(x + width/2, height, 'bo', markersize=3)
                else:
                    rect = plt.Rectangle((x, height), width, -height, 
                                        facecolor='red', alpha=0.3, edgecolor='red')
                    # 在矩形顶部中点绘制一个小点
                    self.ax.plot(x + width/2, height, 'ro', markersize=3)
                
                self.ax.add_patch(rect)
                self.rects.append(rect)
            
            # 更新矩形面积显示
            if hasattr(self, 'area_text'):
                self.area_text.config(state=tk.NORMAL)
                self.area_text.delete(1.0, tk.END)
                self.area_text.insert(tk.END, f"{total_area:.4f}")
                self.area_text.config(state=tk.DISABLED)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("矩形错误", f"更新矩形时出错: {str(e)}")
            print(f"更新矩形时出错: {str(e)}")
            self.clear_rectangles()

    def calculate_integral(self):
        """计算定积分"""
        try:
            if not hasattr(self, 'user_function') or self.user_function is None:
                messagebox.showinfo("提示", "请先输入并绘制函数")
                return
            
            # 获取积分区间 - 使用矩形积分的范围
            try:
                a = float(self.rect_min_entry.get())
                b = float(self.rect_max_entry.get())
            except (ValueError, AttributeError):
                messagebox.showerror("输入错误", "请输入有效的积分区间")
                return
            
            # 使用scipy.integrate计算积分
            from scipy import integrate
            integral_val, error = integrate.quad(self.user_function, a, b)
            
            # 更新积分结果显示
            if hasattr(self, 'integral_text'):
                self.integral_text.config(state=tk.NORMAL)
                self.integral_text.delete(1.0, tk.END)
                self.integral_text.insert(tk.END, f"{integral_val:.4f}")
                self.integral_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("积分错误", f"计算积分时出错: {str(e)}")
            print(f"计算积分时出错: {str(e)}")

    def update_division(self, num_divisions):
        """更新分割点和连接线"""
        # 确保分割点数至少为2
        num_divisions = max(2, int(num_divisions))
        
        try:
            if not hasattr(self, 'user_function') or self.user_function is None:
                messagebox.showinfo("提示", "请先输入并绘制函数")
                return
            
            # 更新分割点数量标签
            if hasattr(self, 'division_label'):
                self.division_label.config(text=f"分割点数：{num_divisions}")
            
            # 清除现有的分割点和连接线
            self.clear_division()
            
            # 如果不显示分割线，则直接返回
            if not self.draw_division.get():
                return
            
            # 获取当前x轴范围
            try:
                a = float(self.division_min_entry.get())
                b = float(self.division_max_entry.get())
            except (ValueError, AttributeError):
                # 如果输入无效或输入框不存在，使用当前x轴范围
                xlim = self.ax.get_xlim()
                a, b = xlim[0], xlim[1]
                # 如果有输入框，更新其值
                if hasattr(self, 'division_min_entry'):
                    self.division_min_entry.delete(0, tk.END)
                    self.division_min_entry.insert(0, str(a))
                if hasattr(self, 'division_max_entry'):
                    self.division_max_entry.delete(0, tk.END)
                    self.division_max_entry.insert(0, str(b))
            
            # 生成分割点
            x_vals = np.linspace(a, b, num_divisions)
            valid_points = []
            
            # 计算每个分割点的函数值
            for x_val in x_vals:
                try:
                    y_val = self.user_function(x_val)
                    if not (np.isnan(y_val) or np.isinf(y_val)):
                        valid_points.append((x_val, y_val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    continue
            
            # 如果有效点数不足，则无法绘制连接线
            if len(valid_points) < 2:
                messagebox.showinfo("提示", "有效点数不足，无法绘制连接线")
                return
            
            # 绘制分割点
            for x, y in valid_points:
                point, = self.ax.plot(x, y, 'go', markersize=5)
                self.division_points.append(point)
            
            # 绘制连接线
            x_vals = [p[0] for p in valid_points]
            y_vals = [p[1] for p in valid_points]
            self.division_line, = self.ax.plot(x_vals, y_vals, 'g-', linewidth=1, alpha=0.7)
            
            # 计算连接线长度
            length = 0
            for i in range(len(valid_points) - 1):
                x1, y1 = valid_points[i]
                x2, y2 = valid_points[i + 1]
                segment_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                length += segment_length
            
            # 更新长度显示
            if hasattr(self, 'length_text'):
                self.length_text.config(state=tk.NORMAL)
                self.length_text.delete(1.0, tk.END)
                self.length_text.insert(tk.END, f"{length:.4f}")
                self.length_text.config(state=tk.DISABLED)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("分割线错误", f"更新分割线时出错: {str(e)}")
            self.clear_division()

    def _update_taylor(self):
        """更新泰勒级数的计算和显示"""
        try:
            if not hasattr(self, 'user_function') or self.user_function is None:
                messagebox.showinfo("提示", "请先输入并绘制函数")
                return
            
            # 获取泰勒展开的阶数和中心点
            n_terms = int(self.taylor_slider.get())
            center = float(self.taylor_center_var.get())
            self.taylor_order = n_terms
            
            # 更新阶数标签
            if hasattr(self, 'taylor_label'):
                self.taylor_label.config(text=f"阶数：{n_terms}")
            
            # 使用sympy计算泰勒展开
            x = sp.Symbol('x')
            func_expr = self.function_entry.get()
            expr = parse_expr(func_expr, transformations=(standard_transformations + (implicit_multiplication_application,)))
            
            # 计算泰勒级数 - 确保即使是偶数阶也能正确展开
            taylor_series = sum([(sp.diff(expr, x, i).subs(x, center) / sp.factorial(i)) * (x - center)**i for i in range(n_terms + 1)])
            
            # 将泰勒级数转换为可计算的函数
            taylor_func = sp.lambdify(x, taylor_series, modules=['numpy'])
            
            # 绘制泰勒曲线
            xlim = self.ax.get_xlim()
            x_vals = np.linspace(xlim[0], xlim[1], 1000)
            
            # 计算y值，处理可能的错误
            y_vals = []
            for x_val in x_vals:
                try:
                    y_vals.append(taylor_func(x_val))
                except (ValueError, ZeroDivisionError, OverflowError):
                    y_vals.append(np.nan)
            
            # 更新或创建泰勒曲线
            if hasattr(self, 'taylor_plot') and self.taylor_plot:
                self.taylor_plot.set_data(x_vals, y_vals)
            else:
                self.taylor_plot, = self.ax.plot(x_vals, y_vals, 'g--', linewidth=2, label=f'泰勒级数 (n={n_terms})')
            
            # 更新图例
            self.ax.legend(loc='upper right', prop={'family':'SimHei', 'size':10})
            
            # 更新画布
            self.canvas.draw()
            
            # 更新泰勒公式显示
            if hasattr(self, 'taylor_formula_text'):
                # 将泰勒级数转换为字符串
                taylor_str = str(taylor_series)
                
                # 更新文本框
                self.taylor_formula_text.config(state=tk.NORMAL)
                self.taylor_formula_text.delete(1.0, tk.END)
                formula_display = f"f(x) ≈ {taylor_str}   (在 x={center} 处的 {n_terms} 阶泰勒展开)"
                self.taylor_formula_text.insert(tk.END, formula_display)
                self.taylor_formula_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("泰勒更新错误", f"更新泰勒展开时出错: {str(e)}")
            print(f"泰勒展开错误: {str(e)}")
            # 清除泰勒公式显示
            if hasattr(self, 'taylor_formula_text'):
                self.taylor_formula_text.config(state=tk.NORMAL)
                self.taylor_formula_text.delete(1.0, tk.END)
                self.taylor_formula_text.insert(tk.END, f"泰勒展开错误: {str(e)}")
                self.taylor_formula_text.config(state=tk.DISABLED)

    def _on_taylor_slider_change(self, value):
        """处理泰勒滑块值变化"""
        # 确保泰勒阶数至少为1
        n_terms = max(1, int(float(value)))
        
        # 更新阶数标签
        if hasattr(self, 'taylor_label'):
            self.taylor_label.config(text=f"阶数：{n_terms}")
        
        # 如果泰勒展开已启用，则更新泰勒展开
        if self.draw_taylor.get():
            self._update_taylor()

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = TrigPlotApp(root)
    root.mainloop()