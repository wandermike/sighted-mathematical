import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font # 导入 font
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
import sympy as sp
from scipy import stats

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class RandomVariableApp:
    def __init__(self, master_frame):
        self.master = master_frame
        # master.title("随机变量与期望可视化工具")
        # self.master.geometry("1200x800")
        
        # --- Style configuration can stay if needed, but apply to widgets within master_frame ---
        # style = ttk.Style() ...

        # --- Create UI elements directly inside master_frame ---
        # Instead of creating a new main_frame inside self.master:
        # main_frame = ttk.Frame(self.master)
        # main_frame.pack(...)
        # Use self.master (the passed frame) directly as the parent:

        # Create title *within* the frame if desired, or rely on tab text
        title_label = ttk.Label(self.master, text="随机变量与期望可视化", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10)) # Adjust padding

        # Create Notebook *within* the frame
        self.notebook = ttk.Notebook(self.master) # Use self.master as parent
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5) # Adjust padding

        # Create tab pages (these are frames *within* the notebook)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="单变量与多变量分布")
        self.notebook.add(self.tab2, text="期望与方差")
        self.notebook.add(self.tab3, text="随机变量变换")

        # --- Initialize tabs (call setup methods) ---
        # These setup methods should now build UI inside self.tab1, self.tab2, etc.
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

        # --- Other initializations ---
        self._after_id = None
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Initial plot needs careful handling - ensure canvas is created first
        # Use after(0) or after(1) to schedule the plot after __init__ completes
        self.master.after(1, self.initial_plot)
    
    def initial_plot(self):
        """初始绘制当前选中的选项卡"""
        self.on_tab_change(None) # 手动触发一次
    
    def on_tab_change(self, event):
        """选项卡切换时的回调函数"""
        # 取消之前的防抖计时器
        if self._after_id:
            self.master.after_cancel(self._after_id)
            self._after_id = None
        
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        # 根据选项卡更新界面
        if tab_name == "单变量与多变量分布":
            self.plot_distribution()
        elif tab_name == "期望与方差":
            self.plot_expectation()
        elif tab_name == "随机变量变换":
            self.plot_transformation()
    
    # --- 防抖动更新函数 ---
    def _debounce(self, func, delay=300):
        """防抖动装饰器或辅助函数"""
        if self._after_id:
            self.master.after_cancel(self._after_id)
        self._after_id = self.master.after(delay, func)
    
    def schedule_plot_distribution(self, value=None):
        """安排绘制分布图（带防抖）"""
        # 更新对应的Entry（如果需要）
        # 注意：这里需要根据具体是哪个滑块来更新哪个Entry，
        # 为了简化，我们可以在plot_distribution内部读取滑块值
        # 或者在创建滑块时传递Entry对象给这个函数
        self._debounce(self.plot_distribution)
        # 同时更新Entry的值
        self.update_entries_from_vars(tab_index=0)
    
    def schedule_plot_expectation(self, value=None):
        """安排绘制期望图（带防抖）"""
        self._debounce(self.plot_expectation)
        # 同时更新Entry的值
        self.update_entries_from_vars(tab_index=1)
    
    def schedule_plot_transformation(self, value=None):
        """安排绘制变换图（带防抖）"""
        self._debounce(self.plot_transformation)
        # 同时更新Entry的值
        self.update_entries_from_vars(tab_index=2)
    
    def update_entries_from_vars(self, tab_index):
        """根据当前变量更新对应的输入框"""
        try:
            if tab_index == 0: # 分布选项卡
                dist_type = self.dist_type_var.get()
                if dist_type == "一维正态分布":
                    self.update_entry(self.mu_entry, self.mu_var.get())
                    self.update_entry(self.sigma_entry, self.sigma_var.get())
                elif dist_type == "二维正态分布":
                    self.update_entry(self.mu1_entry, self.mu1_var.get())
                    self.update_entry(self.mu2_entry, self.mu2_var.get())
                    self.update_entry(self.sigma1_entry, self.sigma1_var.get())
                    self.update_entry(self.sigma2_entry, self.sigma2_var.get())
                    self.update_entry(self.rho_entry, self.rho_var.get())
                elif dist_type == "联合分布":
                    joint_type = self.joint_type_var.get()
                    if joint_type == "二项分布与泊松分布":
                        self.update_entry(self.n_entry, self.n_var.get())
                        self.update_entry(self.p_entry, self.p_var.get())
                        self.update_entry(self.lambda_entry, self.lambda_var.get())
                    elif joint_type == "正态分布与均匀分布":
                        self.update_entry(self.normal_mu_entry, self.normal_mu_var.get())
                        self.update_entry(self.normal_sigma_entry, self.normal_sigma_var.get())
                        self.update_entry(self.a_entry, self.a_var.get())
                        self.update_entry(self.b_entry, self.b_var.get())
            elif tab_index == 1: # 期望选项卡
                dist_type = self.exp_dist_type_var.get()
                if dist_type == "一维正态分布":
                    self.update_entry(self.exp_mu_entry, self.exp_mu_var.get())
                    self.update_entry(self.exp_sigma_entry, self.exp_sigma_var.get())
                elif dist_type == "二维正态分布":
                    self.update_entry(self.exp_mu1_entry, self.exp_mu1_var.get())
                    self.update_entry(self.exp_mu2_entry, self.exp_mu2_var.get())
                    self.update_entry(self.exp_sigma1_entry, self.exp_sigma1_var.get())
                    self.update_entry(self.exp_sigma2_entry, self.exp_sigma2_var.get())
                    self.update_entry(self.exp_rho_entry, self.exp_rho_var.get())
            elif tab_index == 2: # 变换选项卡
                 dist_type = self.orig_dist_type_var.get()
                 if dist_type == "正态分布":
                     self.update_entry(self.orig_mu_entry, self.orig_mu_var.get())
                     self.update_entry(self.orig_sigma_entry, self.orig_sigma_var.get())
                 elif dist_type == "均匀分布":
                     self.update_entry(self.orig_a_entry, self.orig_a_var.get())
                     self.update_entry(self.orig_b_entry, self.orig_b_var.get())
                 elif dist_type == "指数分布":
                     self.update_entry(self.orig_lambda_entry, self.orig_lambda_var.get())
        except Exception as e:
            # print(f"Error updating entries: {e}") # 调试用
            pass # 忽略更新Entry时的错误（例如控件尚未创建）
    
    def setup_tab1(self):
        """设置单变量与多变量分布选项卡"""
        # 创建左侧控制面板和右侧绘图区域
        control_frame = ttk.LabelFrame(self.tab1, text="分布参数设置")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        plot_frame = ttk.Frame(self.tab1)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建绘图区域
        self.fig1 = Figure(figsize=(10, 7))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=plot_frame)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 创建分布类型选择下拉框
        ttk.Label(control_frame, text="选择分布类型:").pack(anchor=tk.W, pady=5)
        self.dist_type_var = tk.StringVar(value="一维正态分布")
        dist_combobox = ttk.Combobox(control_frame, textvariable=self.dist_type_var, 
                                     values=["一维正态分布", "二维正态分布", "联合分布"])
        dist_combobox.pack(anchor=tk.W, pady=5)
        dist_combobox.bind("<<ComboboxSelected>>", self.on_distribution_change) # 切换类型时也重绘
        
        # 创建参数框架
        self.param_frame1 = ttk.LabelFrame(control_frame, text="分布参数")
        self.param_frame1.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 初始化参数（一维正态分布）
        self.create_1d_normal_params()
        
        # 创建按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.plot_button1 = ttk.Button(button_frame, text="绘制分布图", command=self.plot_distribution)
        self.plot_button1.pack(side=tk.LEFT, padx=5)
        
        self.clear_button1 = ttk.Button(button_frame, text="清除图像", command=self.clear_plot1)
        self.clear_button1.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            button_frame, 
            text="理论知识", 
            command=self.show_theory1
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    
    def setup_tab2(self):
        """设置期望与方差选项卡"""
        # 创建左侧控制面板和右侧绘图区域
        control_frame = ttk.LabelFrame(self.tab2, text="分布参数设置")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        plot_frame = ttk.Frame(self.tab2)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建绘图区域
        self.fig2 = Figure(figsize=(10, 7))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=plot_frame)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 创建分布类型选择下拉框
        ttk.Label(control_frame, text="选择分布类型:").pack(anchor=tk.W, pady=5)
        self.exp_dist_type_var = tk.StringVar(value="一维正态分布")
        exp_dist_combobox = ttk.Combobox(control_frame, textvariable=self.exp_dist_type_var, 
                                       values=["一维正态分布", "二维正态分布"])
        exp_dist_combobox.pack(anchor=tk.W, pady=5)
        # 注意：这里绑定的是 on_expectation_dist_change，它内部会调用 plot_expectation
        exp_dist_combobox.bind("<<ComboboxSelected>>", self.on_expectation_dist_change)
        
        # 创建参数框架
        self.param_frame2 = ttk.LabelFrame(control_frame, text="分布参数")
        self.param_frame2.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 初始化参数（一维正态分布）
        self.create_1d_normal_expectation_params()
        
        # 创建结果显示框架
        self.result_frame2 = ttk.LabelFrame(control_frame, text="计算结果")
        self.result_frame2.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text2 = scrolledtext.ScrolledText(self.result_frame2, height=8, width=30)
        self.result_text2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.plot_button2 = ttk.Button(button_frame, text="计算期望与方差", command=self.plot_expectation)
        self.plot_button2.pack(side=tk.LEFT, padx=5)
        
        self.clear_button2 = ttk.Button(button_frame, text="清除图像", command=self.clear_plot2)
        self.clear_button2.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            button_frame, 
            text="理论知识", 
            command=self.show_theory2
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    
    def setup_tab3(self):
        """设置随机变量变换选项卡"""
        # 创建左侧控制面板和右侧绘图区域
        control_frame = ttk.LabelFrame(self.tab3, text="分布参数设置")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        plot_frame = ttk.Frame(self.tab3)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建绘图区域
        self.fig3 = Figure(figsize=(10, 7))
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=plot_frame)
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 创建原始分布参数框架
        self.orig_param_frame = ttk.LabelFrame(control_frame, text="原始分布参数")
        self.orig_param_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Store the label and combobox as instance attributes
        self.orig_dist_type_label = ttk.Label(self.orig_param_frame, text="原始分布类型:")
        self.orig_dist_type_label.pack(anchor=tk.W, pady=5)

        self.orig_dist_type_var = tk.StringVar(value="正态分布")
        self.orig_dist_combobox = ttk.Combobox(self.orig_param_frame, textvariable=self.orig_dist_type_var,
                                              values=["正态分布", "均匀分布", "指数分布"])
        self.orig_dist_combobox.pack(anchor=tk.W, pady=5)
        # 注意：这里绑定的是 on_orig_distribution_change，它内部会调用 plot_transformation
        self.orig_dist_combobox.bind("<<ComboboxSelected>>", self.on_orig_distribution_change)

        # 初始化原始分布参数（正态分布）
        self.create_orig_normal_params() # 这个函数内部会创建滑块
        
        # 创建变换函数框架
        transform_frame = ttk.LabelFrame(control_frame, text="变换函数")
        transform_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(transform_frame, text="输入变换函数 Y = g(X):").pack(anchor=tk.W, pady=5)
        self.transform_var = tk.StringVar(value="x**2")
        transform_entry = ttk.Entry(transform_frame, textvariable=self.transform_var, width=30)
        transform_entry.pack(anchor=tk.W, pady=5)
        # 变换函数输入变化时也触发更新
        transform_entry.bind("<KeyRelease>", lambda e: self.schedule_plot_transformation())
        
        ttk.Label(transform_frame, text="提示: 使用x表示随机变量X").pack(anchor=tk.W, pady=2)
        ttk.Label(transform_frame, text="例如: x**2, exp(x), sin(x)").pack(anchor=tk.W, pady=2)
        
        # 创建结果显示框架
        self.result_frame3 = ttk.LabelFrame(control_frame, text="计算结果")
        self.result_frame3.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text3 = scrolledtext.ScrolledText(self.result_frame3, height=8, width=30)
        self.result_text3.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.plot_button3 = ttk.Button(button_frame, text="计算变换", command=self.plot_transformation)
        self.plot_button3.pack(side=tk.LEFT, padx=5)
        
        self.clear_button3 = ttk.Button(button_frame, text="清除图像", command=self.clear_plot3)
        self.clear_button3.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            button_frame, 
            text="理论知识", 
            command=self.show_theory3
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    
    # ===== 选项卡1: 单变量与多变量分布 =====
    
    def create_1d_normal_params(self):
        """创建一维正态分布参数控件（带实时更新）"""
        # 清除之前的控件
        for widget in self.param_frame1.winfo_children():
            widget.destroy()
        
        # 均值参数
        ttk.Label(self.param_frame1, text="均值 (μ):").pack(anchor=tk.W, pady=2)
        self.mu_var = tk.DoubleVar(value=0)
        # 修改 command 指向防抖函数
        mu_scale = ttk.Scale(self.param_frame1, from_=-5, to=5, variable=self.mu_var,
                           orient=tk.HORIZONTAL,
                           command=self.schedule_plot_distribution) # 使用防抖
        mu_scale.pack(fill=tk.X)
        self.mu_entry = ttk.Entry(self.param_frame1, width=10)
        self.mu_entry.pack(anchor=tk.W)
        self.mu_entry.insert(0, "0")
        
        # 标准差参数
        ttk.Label(self.param_frame1, text="标准差 (σ):").pack(anchor=tk.W, pady=2)
        self.sigma_var = tk.DoubleVar(value=1)
        # 修改 command 指向防抖函数
        sigma_scale = ttk.Scale(self.param_frame1, from_=0.1, to=3, variable=self.sigma_var,
                          orient=tk.HORIZONTAL,
                          command=self.schedule_plot_distribution) # 使用防抖
        sigma_scale.pack(fill=tk.X)
        self.sigma_entry = ttk.Entry(self.param_frame1, width=10)
        self.sigma_entry.pack(anchor=tk.W)
        self.sigma_entry.insert(0, "1")
        
        # 绑定输入框变化事件，也使用防抖
        self.mu_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.mu_entry, self.mu_var, self.schedule_plot_distribution))
        self.sigma_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.sigma_entry, self.sigma_var, self.schedule_plot_distribution))
    
    def create_2d_normal_params(self):
        """创建二维正态分布参数控件"""
        # 清除之前的控件
        for widget in self.param_frame1.winfo_children():
            widget.destroy()
        
        # X均值参数
        ttk.Label(self.param_frame1, text="X均值 (μ₁):").pack(anchor=tk.W, pady=2)
        self.mu1_var = tk.DoubleVar(value=0)
        mu1_scale = ttk.Scale(self.param_frame1, from_=-5, to=5, variable=self.mu1_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_distribution) # 使用防抖
        mu1_scale.pack(fill=tk.X)
        self.mu1_entry = ttk.Entry(self.param_frame1, width=10)
        self.mu1_entry.pack(anchor=tk.W)
        self.mu1_entry.insert(0, "0")
        
        # Y均值参数
        ttk.Label(self.param_frame1, text="Y均值 (μ₂):").pack(anchor=tk.W, pady=2)
        self.mu2_var = tk.DoubleVar(value=0)
        mu2_scale = ttk.Scale(self.param_frame1, from_=-5, to=5, variable=self.mu2_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_distribution) # 使用防抖
        mu2_scale.pack(fill=tk.X)
        self.mu2_entry = ttk.Entry(self.param_frame1, width=10)
        self.mu2_entry.pack(anchor=tk.W)
        self.mu2_entry.insert(0, "0")
        
        # X标准差参数
        ttk.Label(self.param_frame1, text="X标准差 (σ₁):").pack(anchor=tk.W, pady=2)
        self.sigma1_var = tk.DoubleVar(value=1)
        sigma1_scale = ttk.Scale(self.param_frame1, from_=0.1, to=3, variable=self.sigma1_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_distribution) # 使用防抖
        sigma1_scale.pack(fill=tk.X)
        self.sigma1_entry = ttk.Entry(self.param_frame1, width=10)
        self.sigma1_entry.pack(anchor=tk.W)
        self.sigma1_entry.insert(0, "1")
        
        # Y标准差参数
        ttk.Label(self.param_frame1, text="Y标准差 (σ₂):").pack(anchor=tk.W, pady=2)
        self.sigma2_var = tk.DoubleVar(value=1)
        sigma2_scale = ttk.Scale(self.param_frame1, from_=0.1, to=3, variable=self.sigma2_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_distribution) # 使用防抖
        sigma2_scale.pack(fill=tk.X)
        self.sigma2_entry = ttk.Entry(self.param_frame1, width=10)
        self.sigma2_entry.pack(anchor=tk.W)
        self.sigma2_entry.insert(0, "1")
        
        # 相关系数参数
        ttk.Label(self.param_frame1, text="相关系数 (ρ):").pack(anchor=tk.W, pady=2)
        self.rho_var = tk.DoubleVar(value=0)
        rho_scale = ttk.Scale(self.param_frame1, from_=-0.99, to=0.99, variable=self.rho_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_distribution) # 使用防抖
        rho_scale.pack(fill=tk.X)
        self.rho_entry = ttk.Entry(self.param_frame1, width=10)
        self.rho_entry.pack(anchor=tk.W)
        self.rho_entry.insert(0, "0")
        
        # 移除 <Motion> 绑定，因为 command 会处理更新
        # mu1_scale.bind("<Motion>", lambda e: self.update_entry(self.mu1_entry, self.mu1_var.get()))
        # ... 其他 <Motion> 绑定也移除 ...
        
        # 绑定输入框变化事件，也使用防抖
        self.mu1_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.mu1_entry, self.mu1_var, self.schedule_plot_distribution))
        self.mu2_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.mu2_entry, self.mu2_var, self.schedule_plot_distribution))
        self.sigma1_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.sigma1_entry, self.sigma1_var, self.schedule_plot_distribution))
        self.sigma2_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.sigma2_entry, self.sigma2_var, self.schedule_plot_distribution))
        self.rho_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.rho_entry, self.rho_var, self.schedule_plot_distribution))
    
    def create_joint_dist_params(self):
        """创建联合分布参数控件"""
        # 清除之前的控件
        for widget in self.param_frame1.winfo_children():
            widget.destroy()
        
        # 联合分布类型
        ttk.Label(self.param_frame1, text="联合分布类型:").pack(anchor=tk.W, pady=2)
        self.joint_type_var = tk.StringVar(value="二项分布与泊松分布")
        joint_combobox = ttk.Combobox(self.param_frame1, textvariable=self.joint_type_var, 
                                     values=["二项分布与泊松分布", "正态分布与均匀分布"])
        joint_combobox.pack(anchor=tk.W, pady=5)
        
        # 二项分布参数
        self.binom_frame = ttk.LabelFrame(self.param_frame1, text="二项分布参数")
        self.binom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.binom_frame, text="试验次数 (n):").pack(anchor=tk.W, pady=2)
        self.n_var = tk.IntVar(value=10)
        n_scale = ttk.Scale(self.binom_frame, from_=1, to=30, variable=self.n_var,
                          orient=tk.HORIZONTAL,
                          command=self.schedule_plot_distribution) # 使用防抖
        n_scale.pack(fill=tk.X)
        self.n_entry = ttk.Entry(self.binom_frame, width=10)
        self.n_entry.pack(anchor=tk.W)
        self.n_entry.insert(0, "10")
        
        ttk.Label(self.binom_frame, text="成功概率 (p):").pack(anchor=tk.W, pady=2)
        self.p_var = tk.DoubleVar(value=0.5)
        p_scale = ttk.Scale(self.binom_frame, from_=0.01, to=0.99, variable=self.p_var,
                          orient=tk.HORIZONTAL,
                          command=self.schedule_plot_distribution) # 使用防抖
        p_scale.pack(fill=tk.X)
        self.p_entry = ttk.Entry(self.binom_frame, width=10)
        self.p_entry.pack(anchor=tk.W)
        self.p_entry.insert(0, "0.5")
        
        # 泊松分布参数
        self.poisson_frame = ttk.LabelFrame(self.param_frame1, text="泊松分布参数")
        self.poisson_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.poisson_frame, text="均值 (λ):").pack(anchor=tk.W, pady=2)
        self.lambda_var = tk.DoubleVar(value=5)
        lambda_scale = ttk.Scale(self.poisson_frame, from_=0.1, to=20, variable=self.lambda_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_distribution) # 使用防抖
        lambda_scale.pack(fill=tk.X)
        self.lambda_entry = ttk.Entry(self.poisson_frame, width=10)
        self.lambda_entry.pack(anchor=tk.W)
        self.lambda_entry.insert(0, "5")
        
        # 移除 <Motion> 绑定
        # n_scale.bind("<Motion>", lambda e: self.update_entry(self.n_entry, self.n_var.get()))
        # ... 其他 <Motion> 绑定也移除 ...
        
        # 绑定输入框变化事件，也使用防抖
        self.n_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.n_entry, self.n_var, self.schedule_plot_distribution))
        self.p_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.p_entry, self.p_var, self.schedule_plot_distribution))
        self.lambda_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.lambda_entry, self.lambda_var, self.schedule_plot_distribution))
        
        # 绑定联合分布类型变化事件
        joint_combobox.bind("<<ComboboxSelected>>", self.on_joint_distribution_change) # 切换类型时也重绘
        
        # 初始化时根据默认类型显示/隐藏
        self.on_joint_distribution_change(None)
    
    def on_joint_distribution_change(self, event):
        """联合分布类型变化时的回调函数"""
        joint_type = self.joint_type_var.get()
        
        if joint_type == "二项分布与泊松分布":
            # 显示二项分布和泊松分布参数
            self.binom_frame.pack(fill=tk.X, pady=5)
            self.poisson_frame.pack(fill=tk.X, pady=5)
            
            # 如果存在正态分布和均匀分布参数框架，则隐藏
            if hasattr(self, 'normal_frame'):
                self.normal_frame.pack_forget()
            if hasattr(self, 'uniform_frame'):
                self.uniform_frame.pack_forget()
        
        elif joint_type == "正态分布与均匀分布":
            # 隐藏二项分布和泊松分布参数
            self.binom_frame.pack_forget()
            self.poisson_frame.pack_forget()
            
            # 创建正态分布参数框架（如果不存在）
            if not hasattr(self, 'normal_frame'):
                self.normal_frame = ttk.LabelFrame(self.param_frame1, text="正态分布参数")
                
                ttk.Label(self.normal_frame, text="均值 (μ):").pack(anchor=tk.W, pady=2)
                self.normal_mu_var = tk.DoubleVar(value=0)
                normal_mu_scale = ttk.Scale(self.normal_frame, from_=-5, to=5, variable=self.normal_mu_var,
                                          orient=tk.HORIZONTAL,
                                          command=self.schedule_plot_distribution) # 使用防抖
                normal_mu_scale.pack(fill=tk.X)
                self.normal_mu_entry = ttk.Entry(self.normal_frame, width=10)
                self.normal_mu_entry.pack(anchor=tk.W)
                self.normal_mu_entry.insert(0, "0")
                
                ttk.Label(self.normal_frame, text="标准差 (σ):").pack(anchor=tk.W, pady=2)
                self.normal_sigma_var = tk.DoubleVar(value=1)
                normal_sigma_scale = ttk.Scale(self.normal_frame, from_=0.1, to=3, variable=self.normal_sigma_var,
                                             orient=tk.HORIZONTAL,
                                             command=self.schedule_plot_distribution) # 使用防抖
                normal_sigma_scale.pack(fill=tk.X)
                self.normal_sigma_entry = ttk.Entry(self.normal_frame, width=10)
                self.normal_sigma_entry.pack(anchor=tk.W)
                self.normal_sigma_entry.insert(0, "1")
                
                # 绑定输入框变化事件
                self.normal_mu_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.normal_mu_entry, self.normal_mu_var, self.schedule_plot_distribution))
                self.normal_sigma_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.normal_sigma_entry, self.normal_sigma_var, self.schedule_plot_distribution))
            
            # 创建均匀分布参数框架（如果不存在）
            if not hasattr(self, 'uniform_frame'):
                self.uniform_frame = ttk.LabelFrame(self.param_frame1, text="均匀分布参数")
                
                ttk.Label(self.uniform_frame, text="下限 (a):").pack(anchor=tk.W, pady=2)
                self.a_var = tk.DoubleVar(value=-2)
                a_scale = ttk.Scale(self.uniform_frame, from_=-5, to=0, variable=self.a_var,
                                  orient=tk.HORIZONTAL,
                                  command=self.schedule_plot_distribution) # 使用防抖
                a_scale.pack(fill=tk.X)
                self.a_entry = ttk.Entry(self.uniform_frame, width=10)
                self.a_entry.pack(anchor=tk.W)
                self.a_entry.insert(0, "-2")
                
                ttk.Label(self.uniform_frame, text="上限 (b):").pack(anchor=tk.W, pady=2)
                self.b_var = tk.DoubleVar(value=2)
                b_scale = ttk.Scale(self.uniform_frame, from_=0, to=5, variable=self.b_var,
                                  orient=tk.HORIZONTAL,
                                  command=self.schedule_plot_distribution) # 使用防抖
                b_scale.pack(fill=tk.X)
                self.b_entry = ttk.Entry(self.uniform_frame, width=10)
                self.b_entry.pack(anchor=tk.W)
                self.b_entry.insert(0, "2")
                
                # 绑定输入框变化事件
                self.a_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.a_entry, self.a_var, self.schedule_plot_distribution))
                self.b_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.b_entry, self.b_var, self.schedule_plot_distribution))
            
            # 显示正态分布和均匀分布参数
            self.normal_frame.pack(fill=tk.X, pady=5)
            self.uniform_frame.pack(fill=tk.X, pady=5)
    
    def on_distribution_change(self, event):
        """分布类型变化时的回调函数"""
        dist_type = self.dist_type_var.get()
        
        if dist_type == "一维正态分布":
            self.create_1d_normal_params()
        elif dist_type == "二维正态分布":
            self.create_2d_normal_params()
        elif dist_type == "联合分布":
            self.create_joint_dist_params()
    
        # 切换主分布类型后，立即重绘
        self.schedule_plot_distribution()
    
    def update_entry(self, entry, value):
        """更新输入框的值"""
        # 检查 entry 是否有效
        if entry and entry.winfo_exists():
            current_value = entry.get()
            new_value_str = f"{value:.2f}" if isinstance(value, float) else str(int(value))
            # 只有当值确实改变时才更新，避免光标跳动
            if current_value != new_value_str:
                entry.delete(0, tk.END)
                entry.insert(0, new_value_str)
    
    def update_var_from_entry(self, entry, var):
        """从输入框更新变量的值"""
        if entry and entry.winfo_exists() and var:
            try:
                value_str = entry.get()
                if isinstance(var, tk.IntVar):
                    value = int(float(value_str)) # 先转float再转int，兼容小数输入
                else: # DoubleVar
                    value = float(value_str)

                # 检查值是否在合理范围内（可选，但推荐）
                # 例如，标准差不能为负
                # if var == self.sigma_var and value <= 0: return
                # ... 其他检查 ...

                current_var_value = var.get()
                # 只有当值确实改变时才更新变量
                if abs(current_var_value - value) > 1e-6: # 比较浮点数
                    var.set(value)
                    return True # 表示值已更新
            except ValueError:
                # 输入无效时可以给出提示或恢复原值
                # print("Invalid input")
                pass
        return False # 表示值未更新
    
    def schedule_update_from_entry(self, entry, var, plot_scheduler):
        """带防抖地从输入框更新变量并安排绘图"""
        if self.update_var_from_entry(entry, var):
            # 如果变量成功更新，则安排绘图
            plot_scheduler()
    
    def plot_distribution(self):
        """绘制分布图"""
        # 检查 Canvas 是否有效
        if not self.canvas1 or not self.canvas1.get_tk_widget().winfo_exists():
            return

        dist_type = self.dist_type_var.get()

        # 清除之前的图像
        self.fig1.clear()

        try: # 添加try-except块捕获绘图错误
            if dist_type == "一维正态分布":
                # 确保参数控件已创建
                if hasattr(self, 'mu_var') and hasattr(self, 'sigma_var'):
                    self.plot_1d_normal()
                else:
                    self.create_1d_normal_params() # 如果未创建则创建
                    self.plot_1d_normal()
            elif dist_type == "二维正态分布":
                if hasattr(self, 'mu1_var'): # 检查一个代表性参数
                    self.plot_2d_normal()
                else:
                    self.create_2d_normal_params()
                    self.plot_2d_normal()
            elif dist_type == "联合分布":
                if hasattr(self, 'joint_type_var'):
                     self.plot_joint_distribution() # 这个函数内部会判断具体类型
                else:
                    self.create_joint_dist_params()
                    self.plot_joint_distribution()

            self.canvas1.draw()
        except ValueError as e:
            messagebox.showerror("参数错误", f"输入参数无效: {e}")
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制分布图时出错: {e}")
            print(f"Plotting error (distribution): {e}") # 调试信息
    
    def plot_1d_normal(self):
        """绘制一维正态分布"""
        mu = self.mu_var.get()
        sigma = self.sigma_var.get()
        
        if sigma <= 0:
            messagebox.showerror("参数错误", "标准差必须大于0")
            return
        
        # 创建子图
        ax = self.fig1.add_subplot(111)
        
        # 生成数据
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y = stats.norm.pdf(x, mu, sigma)
        
        # 绘制正态分布曲线
        ax.plot(x, y, 'b-', linewidth=2)
        ax.fill_between(x, y, color='lightblue', alpha=0.5)
        
        # 设置标题和标签
        ax.set_title(f"一维正态分布 (μ={mu:.2f}, σ={sigma:.2f})", fontsize=14)
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("概率密度", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 设置坐标轴范围
        ax.set_xlim(mu - 4*sigma, mu + 4*sigma)
        y_max = stats.norm.pdf(mu, mu, sigma) * 1.1
        ax.set_ylim(0, y_max)
    
    def plot_2d_normal(self):
        """绘制二维正态分布"""
        mu1 = self.mu1_var.get()
        mu2 = self.mu2_var.get()
        sigma1 = self.sigma1_var.get()
        sigma2 = self.sigma2_var.get()
        rho = self.rho_var.get()
        
        if sigma1 <= 0 or sigma2 <= 0:
            messagebox.showerror("参数错误", "标准差必须大于0")
            return
        
        if rho <= -1 or rho >= 1:
            messagebox.showerror("参数错误", "相关系数必须在-1到1之间")
            return
        
        # 创建子图
        ax1 = self.fig1.add_subplot(121, projection='3d')
        ax2 = self.fig1.add_subplot(122)
        
        # 生成网格数据
        x = np.linspace(mu1 - 3*sigma1, mu1 + 3*sigma1, 100)
        y = np.linspace(mu2 - 3*sigma2, mu2 + 3*sigma2, 100)
        X, Y = np.meshgrid(x, y)
        
        # 计算二维正态分布的概率密度
        Z = self.bivariate_normal(X, Y, mu1, mu2, sigma1, sigma2, rho)
        
        # 绘制3D表面图
        surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        
        # 设置3D图的标题和标签
        ax1.set_title("二维正态分布 (3D视图)", fontsize=10)
        ax1.set_xlabel("X", fontsize=8)
        ax1.set_ylabel("Y", fontsize=8)
        ax1.set_zlabel("概率密度", fontsize=8)
        
        # 绘制等高线图
        contour = ax2.contourf(X, Y, Z, 20, cmap='viridis', alpha=0.8)
        ax2.contour(X, Y, Z, 20, colors='k', linewidths=0.5, alpha=0.5)
        self.fig1.colorbar(contour, ax=ax2, shrink=0.8, label='概率密度')
        
        # 绘制均值点
        ax2.plot(mu1, mu2, 'ro', markersize=8)
        
        # 绘制协方差椭圆
        self.plot_cov_ellipse(ax2, [mu1, mu2], [[sigma1**2, rho*sigma1*sigma2], 
                                              [rho*sigma1*sigma2, sigma2**2]])
        
        # 设置等高线图的标题和标签
        ax2.set_title("二维正态分布 (等高线图)", fontsize=10)
        ax2.set_xlabel("X", fontsize=8)
        ax2.set_ylabel("Y", fontsize=8)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 设置坐标轴范围
        ax2.set_xlim(mu1 - 3*sigma1, mu1 + 3*sigma1)
        ax2.set_ylim(mu2 - 3*sigma2, mu2 + 3*sigma2)
        
        # 调整子图布局
        self.fig1.tight_layout()
    
    def plot_joint_distribution(self):
        """绘制联合分布"""
        joint_type = self.joint_type_var.get()
        
        # 创建子图
        ax1 = self.fig1.add_subplot(221)  # 第一个分布
        ax2 = self.fig1.add_subplot(222)  # 第二个分布
        ax3 = self.fig1.add_subplot(212)  # 联合分布
        
        if joint_type == "二项分布与泊松分布":
            # 获取参数
            n = self.n_var.get()
            p = self.p_var.get()
            lambd = self.lambda_var.get()
            
            # 检查参数有效性
            if p <= 0 or p >= 1:
                messagebox.showerror("参数错误", "二项分布的成功概率必须在0到1之间")
                return
            
            if lambd <= 0:
                messagebox.showerror("参数错误", "泊松分布的均值必须大于0")
                return
            
            # 生成二项分布数据
            x_binom = np.arange(0, n+1)
            y_binom = stats.binom.pmf(x_binom, n, p)
            
            # 生成泊松分布数据
            x_poisson = np.arange(0, int(lambd*3)+1)
            y_poisson = stats.poisson.pmf(x_poisson, lambd)
            
            # 绘制二项分布
            ax1.bar(x_binom, y_binom, color='skyblue', edgecolor='blue', alpha=0.7)
            ax1.set_title(f"二项分布 (n={n}, p={p:.2f})", fontsize=10)
            ax1.set_xlabel("成功次数", fontsize=8)
            ax1.set_ylabel("概率", fontsize=8)
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # 绘制泊松分布
            ax2.bar(x_poisson, y_poisson, color='lightgreen', edgecolor='green', alpha=0.7)
            ax2.set_title(f"泊松分布 (λ={lambd:.2f})", fontsize=10)
            ax2.set_xlabel("事件发生次数", fontsize=8)
            ax2.set_ylabel("概率", fontsize=8)
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            # 创建联合分布的热图数据
            X, Y = np.meshgrid(x_binom, x_poisson)
            Z = np.outer(y_poisson, y_binom)  # 假设X和Y独立
            
            # 绘制联合分布热图
            im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                          extent=[x_binom.min()-0.5, x_binom.max()+0.5, 
                                 x_poisson.min()-0.5, x_poisson.max()+0.5])
            self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率')
            
            ax3.set_title("联合分布 (假设独立)", fontsize=12)
            ax3.set_xlabel("二项分布 (X)", fontsize=10)
            ax3.set_ylabel("泊松分布 (Y)", fontsize=10)
            
        elif joint_type == "正态分布与均匀分布":
            # 获取参数
            mu = self.normal_mu_var.get()
            sigma = self.normal_sigma_var.get()
            a = self.a_var.get()
            b = self.b_var.get()
            
            # 检查参数有效性
            if sigma <= 0:
                messagebox.showerror("参数错误", "正态分布的标准差必须大于0")
                return
            
            if a >= b:
                messagebox.showerror("参数错误", "均匀分布的下限必须小于上限")
                return
            
            # 生成正态分布数据
            x_normal = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
            y_normal = stats.norm.pdf(x_normal, mu, sigma)
            
            # 生成均匀分布数据
            x_uniform = np.linspace(a-0.5, b+0.5, 1000)
            y_uniform = np.zeros_like(x_uniform)
            mask = (x_uniform >= a) & (x_uniform <= b)
            y_uniform[mask] = 1.0 / (b - a)
            
            # 绘制正态分布
            ax1.plot(x_normal, y_normal, 'b-', linewidth=2)
            ax1.fill_between(x_normal, y_normal, color='lightblue', alpha=0.5)
            ax1.set_title(f"正态分布 (μ={mu:.2f}, σ={sigma:.2f})", fontsize=10)
            ax1.set_xlabel("x", fontsize=8)
            ax1.set_ylabel("概率密度", fontsize=8)
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # 绘制均匀分布
            ax2.plot(x_uniform, y_uniform, 'g-', linewidth=2)
            ax2.fill_between(x_uniform, y_uniform, color='lightgreen', alpha=0.5)
            ax2.set_title(f"均匀分布 (a={a:.2f}, b={b:.2f})", fontsize=10)
            ax2.set_xlabel("x", fontsize=8)
            ax2.set_ylabel("概率密度", fontsize=8)
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            # 创建联合分布的热图数据
            x_grid = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
            y_grid = np.linspace(a-0.5, b+0.5, 100)
            X, Y = np.meshgrid(x_grid, y_grid)
            
            # 计算联合概率密度（假设独立）
            Z = np.zeros_like(X)
            for i in range(Z.shape[0]):
                for j in range(Z.shape[1]):
                    x_val = X[i, j]
                    y_val = Y[i, j]
                    
                    # 计算正态分布的概率密度
                    normal_pdf = stats.norm.pdf(x_val, mu, sigma)
                    
                    # 计算均匀分布的概率密度
                    uniform_pdf = 0
                    if a <= y_val <= b:
                        uniform_pdf = 1.0 / (b - a)
                    
                    # 联合概率密度（假设独立）
                    Z[i, j] = normal_pdf * uniform_pdf
            
            # 绘制联合分布热图
            im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                          extent=[x_grid.min(), x_grid.max(), y_grid.min(), y_grid.max()])
            self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率密度')
            
            ax3.set_title("联合分布 (假设独立)", fontsize=12)
            ax3.set_xlabel("正态分布 (X)", fontsize=10)
            ax3.set_ylabel("均匀分布 (Y)", fontsize=10)
        
        # 调整子图布局
        self.fig1.tight_layout()
    
    def clear_plot1(self):
        """清除分布图"""
        if self.canvas1 and self.canvas1.get_tk_widget().winfo_exists():
            self.fig1.clear()
            self.canvas1.draw()

    def show_theory1(self):
        """显示单变量与多变量分布理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 单变量与多变量分布知识点内容
            sections = {
                "一维正态分布": """
基本概念：
一维正态分布即通常所说的正态分布，也叫高斯分布。若随机变量X服从一个位置参数为μ、尺度参数为σ的正态分布，记为X∼N(μ,σ^2)。其中μ为均值，决定了分布的中心位置；σ^2为方差，决定了分布的离散程度。

性质：
1.对称性：概率密度函数关于x=μ对称，P(X≤μ)=P(X≥μ)=0.5。
2.线性变换不变性：若X∼N(μ,σ^2)，则aX+b也服从正态分布，即aX+b∼N(aμ+b,a^2*σ^2)（a不等于0）。

应用：
广泛应用于自然科学、社会科学、工程技术等领域。如测量误差、人的身高体重、产品质量指标等众多随机现象都近似服从一维正态分布，可用于分析和预测这些随机变量的取值情况。
""",
                "二维正态分布": """
基本概念：
二维正态分布是描述两个随机变量X和Y联合分布的一种概率分布。设随机向量(X,Y)服从二维正态分布，记为(X,Y)∼N(μ1​,μ2​,σ1^2​,σ2^2​,ρ)，其中μ1​和μ2​分别是X和Y的均值，σ1^2​和σ2^2​分别是X和Y的方差，ρ是X和Y的相关系数。

性质：
1.边缘分布：二维正态分布的边缘分布仍是正态分布，即X∼N(μ1​,σ1^2​)，Y∼N(μ2​,σ2^2​)
2.独立性与相关性：当且仅当ρ=0时，X和Y相互独立。

应用：
常用于分析两个相关的随机变量的联合分布情况，例如在气象学中，可用于研究气温和气压这两个相关气象要素的联合分布；在经济学中，可用于分析两种相关商品的价格波动关系等。
""",
                "联合分布": """
基本概念：
联合分布是指多个随机变量的概率分布，它描述了这些随机变量同时取值的概率情况。对于离散型随机变量，联合分布用联合概率质量函数表示；对于连续型随机变量，联合分布用联合概率密度函数表示。以两个随机变量X和Y为例，联合分布函数F(x,y)=P(X≤x,Y≤y)。

性质：
  1.非负性：F(x,y)≥0。
  2.单调性：关于x和y分别单调不减。
  3.极限性质：limx→+∞,y→+∞ ​F(x,y)=1，limx→−∞,y→−∞ ​F(x,y)=0。

计算方法:
1.对于离散型随机变量，P(X=xi​,Y=yj​)=pij​，∑i​∑j​pij​=1，通过联合概率质量函数计算相关概率。
2.对于连续型随机变量，通过对联合概率密度函数f(x,y)进行积分来计算概率。

应用：
联合分布是研究多个随机变量之间关系的基础，可用于计算各种与多个随机变量有关的概率，以及推导随机变量的其他性质，如边缘分布、条件分布等。在实际应用中，如在可靠性分析中，考虑多个部件的失效概率的联合分布来评估系统的可靠性；在通信系统中，分析多个信号的联合分布来进行信号处理和检测等。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "单变量与多变量分布理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window1()

    def create_theory_window1(self):
        """备选方案：直接创建单变量与多变量分布理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("单变量与多变量分布理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="单变量与多变量分布理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="一维正态分布")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="二维正态分布")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="联合分布")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)
    
    # ===== 选项卡2: 期望与方差 =====
    
    def create_1d_normal_expectation_params(self):
        """创建一维正态分布期望参数控件"""
        # 清除之前的控件
        for widget in self.param_frame2.winfo_children():
            widget.destroy()
        
        # 均值参数
        ttk.Label(self.param_frame2, text="均值 (μ):").pack(anchor=tk.W, pady=2)
        self.exp_mu_var = tk.DoubleVar(value=0)
        exp_mu_scale = ttk.Scale(self.param_frame2, from_=-5, to=5, variable=self.exp_mu_var,
                           orient=tk.HORIZONTAL,
                           command=self.schedule_plot_expectation) # 使用防抖
        exp_mu_scale.pack(fill=tk.X)
        self.exp_mu_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_mu_entry.pack(anchor=tk.W)
        self.exp_mu_entry.insert(0, "0")
        
        # 标准差参数
        ttk.Label(self.param_frame2, text="标准差 (σ):").pack(anchor=tk.W, pady=2)
        self.exp_sigma_var = tk.DoubleVar(value=1)
        exp_sigma_scale = ttk.Scale(self.param_frame2, from_=0.1, to=3, variable=self.exp_sigma_var,
                              orient=tk.HORIZONTAL,
                              command=self.schedule_plot_expectation) # 使用防抖
        exp_sigma_scale.pack(fill=tk.X)
        self.exp_sigma_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_sigma_entry.pack(anchor=tk.W)
        self.exp_sigma_entry.insert(0, "1")
        
        # 绑定输入框变化事件
        self.exp_mu_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_mu_entry, self.exp_mu_var, self.schedule_plot_expectation))
        self.exp_sigma_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_sigma_entry, self.exp_sigma_var, self.schedule_plot_expectation))
    
    def create_2d_normal_expectation_params(self):
        """创建二维正态分布期望参数控件"""
        # 清除之前的控件
        for widget in self.param_frame2.winfo_children():
            widget.destroy()
        
        # X均值参数
        ttk.Label(self.param_frame2, text="X均值 (μ₁):").pack(anchor=tk.W, pady=2)
        self.exp_mu1_var = tk.DoubleVar(value=0)
        exp_mu1_scale = ttk.Scale(self.param_frame2, from_=-5, to=5, variable=self.exp_mu1_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_expectation) # 使用防抖
        exp_mu1_scale.pack(fill=tk.X)
        self.exp_mu1_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_mu1_entry.pack(anchor=tk.W)
        self.exp_mu1_entry.insert(0, "0")
        
        # Y均值参数
        ttk.Label(self.param_frame2, text="Y均值 (μ₂):").pack(anchor=tk.W, pady=2)
        self.exp_mu2_var = tk.DoubleVar(value=0)
        exp_mu2_scale = ttk.Scale(self.param_frame2, from_=-5, to=5, variable=self.exp_mu2_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_expectation) # 使用防抖
        exp_mu2_scale.pack(fill=tk.X)
        self.exp_mu2_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_mu2_entry.pack(anchor=tk.W)
        self.exp_mu2_entry.insert(0, "0")
        
        # X标准差参数
        ttk.Label(self.param_frame2, text="X标准差 (σ₁):").pack(anchor=tk.W, pady=2)
        self.exp_sigma1_var = tk.DoubleVar(value=1)
        exp_sigma1_scale = ttk.Scale(self.param_frame2, from_=0.1, to=3, variable=self.exp_sigma1_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_expectation) # 使用防抖
        exp_sigma1_scale.pack(fill=tk.X)
        self.exp_sigma1_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_sigma1_entry.pack(anchor=tk.W)
        self.exp_sigma1_entry.insert(0, "1")
        
        # Y标准差参数
        ttk.Label(self.param_frame2, text="Y标准差 (σ₂):").pack(anchor=tk.W, pady=2)
        self.exp_sigma2_var = tk.DoubleVar(value=1)
        exp_sigma2_scale = ttk.Scale(self.param_frame2, from_=0.1, to=3, variable=self.exp_sigma2_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_expectation) # 使用防抖
        exp_sigma2_scale.pack(fill=tk.X)
        self.exp_sigma2_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_sigma2_entry.pack(anchor=tk.W)
        self.exp_sigma2_entry.insert(0, "1")
        
        # 相关系数参数
        ttk.Label(self.param_frame2, text="相关系数 (ρ):").pack(anchor=tk.W, pady=2)
        self.exp_rho_var = tk.DoubleVar(value=0)
        exp_rho_scale = ttk.Scale(self.param_frame2, from_=-0.99, to=0.99, variable=self.exp_rho_var,
                            orient=tk.HORIZONTAL,
                            command=self.schedule_plot_expectation) # 使用防抖
        exp_rho_scale.pack(fill=tk.X)
        self.exp_rho_entry = ttk.Entry(self.param_frame2, width=10)
        self.exp_rho_entry.pack(anchor=tk.W)
        self.exp_rho_entry.insert(0, "0")
        
        # 绑定输入框变化事件
        self.exp_mu1_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_mu1_entry, self.exp_mu1_var, self.schedule_plot_expectation))
        self.exp_mu2_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_mu2_entry, self.exp_mu2_var, self.schedule_plot_expectation))
        self.exp_sigma1_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_sigma1_entry, self.exp_sigma1_var, self.schedule_plot_expectation))
        self.exp_sigma2_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_sigma2_entry, self.exp_sigma2_var, self.schedule_plot_expectation))
        self.exp_rho_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.exp_rho_entry, self.exp_rho_var, self.schedule_plot_expectation))
    
    def on_expectation_dist_change(self, event):
        """期望与方差选项卡中分布类型变化时的回调函数"""
        dist_type = self.exp_dist_type_var.get()
        
        if dist_type == "一维正态分布":
            self.create_1d_normal_expectation_params()
        elif dist_type == "二维正态分布":
            self.create_2d_normal_expectation_params()
        
        # 切换类型后立即重绘
        self.schedule_plot_expectation()
    
    def plot_expectation(self):
        """绘制期望与方差图"""
        # 检查 Canvas 是否有效
        if not self.canvas2 or not self.canvas2.get_tk_widget().winfo_exists():
            return

        dist_type = self.exp_dist_type_var.get()

        # 清除之前的图像和文本
        self.fig2.clear()
        if self.result_text2 and self.result_text2.winfo_exists():
            self.result_text2.delete(1.0, tk.END)

        try: # 添加try-except块
            if dist_type == "一维正态分布":
                if hasattr(self, 'exp_mu_var'):
                    self.plot_1d_normal_expectation()
                else:
                    self.create_1d_normal_expectation_params()
                    self.plot_1d_normal_expectation()
            elif dist_type == "二维正态分布":
                 if hasattr(self, 'exp_mu1_var'):
                    self.plot_2d_normal_expectation()
                 else:
                    self.create_2d_normal_expectation_params()
                    self.plot_2d_normal_expectation()

            self.canvas2.draw()
        except ValueError as e:
            messagebox.showerror("参数错误", f"输入参数无效: {e}")
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制期望图时出错: {e}")
            print(f"Plotting error (expectation): {e}") # 调试信息
    
    def clear_plot2(self):
        """清除期望与方差图"""
        if self.canvas2 and self.canvas2.get_tk_widget().winfo_exists():
            self.fig2.clear()
            if self.result_text2 and self.result_text2.winfo_exists():
                self.result_text2.delete(1.0, tk.END)
            self.canvas2.draw()

    def show_theory2(self):
        """显示期望与方差理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 期望与方差知识点内容
            sections = {
                "期望": """
基本定义：
期望是随机变量的加权平均，用于描述随机变量的平均取值情况，记为E(X)。对于离散型随机变量X，若其取值为xi​，对应的概率为pi​，则期望E(X)=∑i​xi​pi​；对于连续型随机变量X，其概率密度函数为f(x)，则期望E(X)为​xf(x)关于x从−∞到+∞的积分。

性质：
  1.若C为常数，则E(C)=C。
  2.对于常数a和随机变量X，有E(aX)=aE(X)。
  3.对于两个随机变量X和Y，有E(X+Y)=E(X)+E(Y)。此性质可推广到多个随机变量的情况。
  4.若X和Y相互独立，则E(XY)=E(X)E(Y)
  
意义：
期望反映了随机变量的集中趋势，是随机变量取值的 “中心” 位置。例如，在多次重复试验中，随机变量的取值会围绕着期望波动，它是对随机变量长期平均行为的一种刻画。
""",
                "方差": """
基本定义：
方差用于衡量随机变量与其期望的偏离程度，记为D(X)或Var(X)。其定义式为D(X)=E[(X−E(X))^2]。对于离散型随机变量X，方差D(X)=∑ipi*​(xi​−E(X))^2​；对于连续型随机变量X，方差D(X)为​f(x)*(x−E(X))^2关于x从−∞到+∞的积分。

性质：
  1.若C为常数，则D(C)=0。
  2.对于常数a和随机变量X，有D(aX)=D(X)*a^2。
  3.D(X)=E(X^2)−[E(X)]^2，这是计算方差的常用公式之一。
  4.若X和Y相互独立，则D(X+Y)=D(X)+D(Y)。

意义：
方差越大，说明随机变量的取值越分散，偏离期望的程度越大；方差越小，随机变量的取值越集中在期望附近，稳定性越高。例如，在比较不同投资项目的风险时，方差可以作为衡量投资回报波动程度的指标，方差大的项目风险相对较高。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "期望与方差理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window2()

    def create_theory_window2(self):
        """备选方案：直接创建期望与方差理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("期望与方差理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="期望与方差理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="期望")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="方差")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)        
    
    # ===== 选项卡3: 随机变量变换 =====
    
    def create_orig_normal_params(self):
        """创建原始正态分布参数控件"""
        # 清除之前的参数控件 (保留类型标签和下拉框)
        for widget in self.orig_param_frame.winfo_children():
            if widget != self.orig_dist_type_label and widget != self.orig_dist_combobox:
                widget.destroy()

        # 均值参数
        ttk.Label(self.orig_param_frame, text="均值 (μ):").pack(anchor=tk.W, pady=2)
        self.orig_mu_var = tk.DoubleVar(value=0)
        mu_scale = ttk.Scale(self.orig_param_frame, from_=-5, to=5, variable=self.orig_mu_var,
                           orient=tk.HORIZONTAL,
                           command=self.schedule_plot_transformation) # 使用防抖
        mu_scale.pack(fill=tk.X)
        self.orig_mu_entry = ttk.Entry(self.orig_param_frame, width=10)
        self.orig_mu_entry.pack(anchor=tk.W)
        self.orig_mu_entry.insert(0, "0")

        # 标准差参数
        ttk.Label(self.orig_param_frame, text="标准差 (σ):").pack(anchor=tk.W, pady=2)
        self.orig_sigma_var = tk.DoubleVar(value=1)
        sigma_scale = ttk.Scale(self.orig_param_frame, from_=0.1, to=3, variable=self.orig_sigma_var,
                              orient=tk.HORIZONTAL,
                              command=self.schedule_plot_transformation) # 使用防抖
        sigma_scale.pack(fill=tk.X)
        self.orig_sigma_entry = ttk.Entry(self.orig_param_frame, width=10)
        self.orig_sigma_entry.pack(anchor=tk.W)
        self.orig_sigma_entry.insert(0, "1")

        # 绑定输入框变化事件
        self.orig_mu_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.orig_mu_entry, self.orig_mu_var, self.schedule_plot_transformation))
        self.orig_sigma_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.orig_sigma_entry, self.orig_sigma_var, self.schedule_plot_transformation))

    def create_orig_uniform_params(self):
        """创建原始均匀分布参数控件"""
        # 清除之前的参数控件 (保留类型标签和下拉框)
        for widget in self.orig_param_frame.winfo_children():
             if widget != self.orig_dist_type_label and widget != self.orig_dist_combobox:
                widget.destroy()

        # 下限参数
        ttk.Label(self.orig_param_frame, text="下限 (a):").pack(anchor=tk.W, pady=2)
        self.orig_a_var = tk.DoubleVar(value=-2)
        a_scale = ttk.Scale(self.orig_param_frame, from_=-5, to=5, variable=self.orig_a_var, # Adjusted range slightly
                          orient=tk.HORIZONTAL,
                          command=self.schedule_plot_transformation) # 使用防抖
        a_scale.pack(fill=tk.X)
        self.orig_a_entry = ttk.Entry(self.orig_param_frame, width=10)
        self.orig_a_entry.pack(anchor=tk.W)
        self.orig_a_entry.insert(0, "-2")

        # 上限参数
        ttk.Label(self.orig_param_frame, text="上限 (b):").pack(anchor=tk.W, pady=2)
        self.orig_b_var = tk.DoubleVar(value=2)
        b_scale = ttk.Scale(self.orig_param_frame, from_=-5, to=5, variable=self.orig_b_var, # Adjusted range slightly
                          orient=tk.HORIZONTAL,
                          command=self.schedule_plot_transformation) # 使用防抖
        b_scale.pack(fill=tk.X)
        self.orig_b_entry = ttk.Entry(self.orig_param_frame, width=10)
        self.orig_b_entry.pack(anchor=tk.W)
        self.orig_b_entry.insert(0, "2")

        # 绑定输入框变化事件
        self.orig_a_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.orig_a_entry, self.orig_a_var, self.schedule_plot_transformation))
        self.orig_b_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.orig_b_entry, self.orig_b_var, self.schedule_plot_transformation))

    def create_orig_exponential_params(self):
        """创建原始指数分布参数控件"""
        # 清除之前的参数控件 (保留类型标签和下拉框)
        for widget in self.orig_param_frame.winfo_children():
             if widget != self.orig_dist_type_label and widget != self.orig_dist_combobox:
                widget.destroy()

        # 率参数
        ttk.Label(self.orig_param_frame, text="率参数 (λ):").pack(anchor=tk.W, pady=2)
        self.orig_lambda_var = tk.DoubleVar(value=1) # Ensure this attribute is created
        lambda_scale = ttk.Scale(self.orig_param_frame, from_=0.1, to=5, variable=self.orig_lambda_var,
                               orient=tk.HORIZONTAL,
                               command=self.schedule_plot_transformation) # 使用防抖
        lambda_scale.pack(fill=tk.X)
        self.orig_lambda_entry = ttk.Entry(self.orig_param_frame, width=10)
        self.orig_lambda_entry.pack(anchor=tk.W)
        self.orig_lambda_entry.insert(0, "1")

        # 绑定输入框变化事件
        self.orig_lambda_entry.bind("<KeyRelease>", lambda e: self.schedule_update_from_entry(self.orig_lambda_entry, self.orig_lambda_var, self.schedule_plot_transformation))

    def on_orig_distribution_change(self, event):
        """原始分布类型变化时的回调函数"""
        dist_type = self.orig_dist_type_var.get()

        if dist_type == "正态分布":
            self.create_orig_normal_params()
        elif dist_type == "均匀分布":
            self.create_orig_uniform_params()
        elif dist_type == "指数分布":
            self.create_orig_exponential_params()

        # 切换类型后，立即重绘
        self.schedule_plot_transformation() # Use the debounced version

    def plot_transformation(self):
        """绘制随机变量变换"""
        # 检查 Canvas 是否有效
        if not self.canvas3 or not self.canvas3.get_tk_widget().winfo_exists():
            return

        # 获取原始分布类型和变换函数
        dist_type = self.orig_dist_type_var.get()
        transform_func_str = self.transform_var.get()

        # 清除之前的图像和结果
        self.fig3.clear()
        if self.result_text3 and self.result_text3.winfo_exists():
            self.result_text3.delete(1.0, tk.END)

        try:
            # 解析变换函数
            x_sym = sp.Symbol('x')
            # 使用更安全的解析方式
            from sympy.parsing.sympy_parser import (parse_expr,
                                                    standard_transformations,
                                                    implicit_multiplication_application)
            transformations = (standard_transformations +
                               (implicit_multiplication_application,))
            transform_expr = parse_expr(transform_func_str,
                                        local_dict={'x': x_sym, 'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 'tan':sp.tan, 'log':sp.log}, # 添加常用函数
                                        transformations=transformations)

            # 检查解析结果是否依赖于 x
            if not transform_expr.has(x_sym):
                 # 如果不依赖x，尝试直接评估为常数
                 try:
                     const_val = float(transform_expr.evalf())
                     transform_expr = sp.Number(const_val) # 替换为 sympy Number
                 except (TypeError, ValueError):
                      raise ValueError(f"变换函数 '{transform_func_str}' 无效或不依赖于 x")

            transform_func = sp.lambdify(x_sym, transform_expr, modules=['numpy', {'exp': np.exp, 'sin': np.sin, 'cos': np.cos, 'tan':np.tan, 'log':np.log}]) # 传递 numpy 函数

            # 创建子图
            ax1 = self.fig3.add_subplot(221)  # 原始分布
            ax2 = self.fig3.add_subplot(222)  # 变换函数
            ax3 = self.fig3.add_subplot(212)  # 变换后的分布

            # 根据选择的分布类型调用相应的绘图函数
            if dist_type == "正态分布":
                self.plot_normal_transformation(ax1, ax2, ax3, transform_func, transform_expr)
            elif dist_type == "均匀分布":
                self.plot_uniform_transformation(ax1, ax2, ax3, transform_func, transform_expr)
            elif dist_type == "指数分布":
                self.plot_exponential_transformation(ax1, ax2, ax3, transform_func, transform_expr)
            else:
                messagebox.showerror("错误", f"未知的分布类型: {dist_type}")
                return

            # 调整布局并绘制
            self.fig3.tight_layout(pad=3.0)
            self.canvas3.draw_idle()

        except (SyntaxError, TypeError, ValueError, AttributeError) as e:
            messagebox.showerror("输入错误", f"无法解析变换函数或参数错误: {e}\n请确保函数语法正确，例如 '2*x + 1', 'exp(x)', 'sin(x)'。")
            # 清理可能存在的绘图
            self.fig3.clear()
            self.canvas3.draw_idle()
            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.insert(tk.END, f"错误: {e}")
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制过程中发生错误: {e}")
            # 清理可能存在的绘图
            self.fig3.clear()
            self.canvas3.draw_idle()
            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.insert(tk.END, f"错误: {e}")
    
    def clear_plot3(self):
        """清除随机变量变换图"""
        if self.canvas3 and self.canvas3.get_tk_widget().winfo_exists():
            self.fig3.clear()
            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.delete(1.0, tk.END)
            self.canvas3.draw()
    
    # 移除旧的 debounced_update 和 update_from_entry_and_plot
    # def debounced_update(self, event): ...
    # def update_from_entry_and_plot(self): ...
    
    def bivariate_normal(self, X, Y, mu1, mu2, sigma1, sigma2, rho):
        """计算二维正态分布的概率密度函数"""
        Z = np.zeros_like(X)
        
        # 计算二维正态分布的概率密度
        Z = (1 / (2 * np.pi * sigma1 * sigma2 * np.sqrt(1 - rho**2)) *
             np.exp(-1 / (2 * (1 - rho**2)) * (
                 ((X - mu1) / sigma1)**2 - 
                 2 * rho * ((X - mu1) / sigma1) * ((Y - mu2) / sigma2) +
                 ((Y - mu2) / sigma2)**2
             )))
        
        return Z
    
    def plot_cov_ellipse(self, ax, pos, cov, n_std=1.0, **kwargs):
        """
        绘制协方差椭圆
        
        参数:
        - ax: matplotlib轴对象
        - pos: 椭圆中心位置 [x, y]
        - cov: 协方差矩阵 [[cov00, cov01], [cov10, cov11]]
        - n_std: 椭圆表示的标准差数量
        """
        # 计算特征值和特征向量
        eigenvals, eigenvecs = np.linalg.eigh(cov)
        
        # 椭圆的角度（弧度）
        angle = np.degrees(np.arctan2(eigenvecs[1, 0], eigenvecs[0, 0]))
        
        # 椭圆的宽度和高度
        width, height = 2 * n_std * np.sqrt(eigenvals)
        
        # 创建椭圆
        ellipse = Ellipse(xy=pos, width=width, height=height, angle=angle, **kwargs)
        
        # 添加到轴对象
        ax.add_patch(ellipse)
        
        return ellipse
    
    def plot_joint_distribution(self):
        """绘制联合分布"""
        joint_type = self.joint_type_var.get()
        
        if joint_type == "二项分布与泊松分布":
            self.plot_binom_poisson_joint()
        elif joint_type == "正态分布与均匀分布":
            self.plot_normal_uniform_joint()
    
    def plot_binom_poisson_joint(self):
        """绘制二项分布与泊松分布的联合分布"""
        n = self.n_var.get()
        p = self.p_var.get()
        lambd = self.lambda_var.get()
        
        if n <= 0 or p <= 0 or p >= 1 or lambd <= 0:
            messagebox.showerror("参数错误", "参数必须满足: n > 0, 0 < p < 1, λ > 0")
            return
        
        # 创建子图
        ax1 = self.fig1.add_subplot(221)  # 二项分布
        ax2 = self.fig1.add_subplot(222)  # 泊松分布
        ax3 = self.fig1.add_subplot(212)  # 联合分布
        
        # 生成二项分布数据
        x_binom = np.arange(0, n+1)
        y_binom = stats.binom.pmf(x_binom, n, p)
        
        # 生成泊松分布数据
        x_poisson = np.arange(0, int(lambd*3)+1)
        y_poisson = stats.poisson.pmf(x_poisson, lambd)
        
        # 绘制二项分布
        ax1.bar(x_binom, y_binom, color='lightblue', edgecolor='blue', alpha=0.7)
        ax1.set_title(f"二项分布 (n={n}, p={p:.2f})", fontsize=10)
        ax1.set_xlabel("成功次数", fontsize=8)
        ax1.set_ylabel("概率", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制泊松分布
        ax2.bar(x_poisson, y_poisson, color='lightgreen', edgecolor='green', alpha=0.7)
        ax2.set_title(f"泊松分布 (λ={lambd:.2f})", fontsize=10)
        ax2.set_xlabel("事件发生次数", fontsize=8)
        ax2.set_ylabel("概率", fontsize=8)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 创建联合分布的热图数据
        X, Y = np.meshgrid(x_binom, x_poisson)
        Z = np.zeros_like(X, dtype=float)
        
        # 计算联合概率（假设独立）
        for i in range(len(x_poisson)):
            for j in range(len(x_binom)):
                Z[i, j] = y_poisson[i] * y_binom[j]
        
        # 绘制联合分布热图
        im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                      extent=[-0.5, n+0.5, -0.5, int(lambd*3)+0.5])
        self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率')
        
        ax3.set_title("联合分布 (假设独立)", fontsize=12)
        ax3.set_xlabel("二项分布 (X)", fontsize=10)
        ax3.set_ylabel("泊松分布 (Y)", fontsize=10)
        
        # 调整子图布局
        self.fig1.tight_layout()
    
    def plot_normal_uniform_joint(self):
        """绘制正态分布与均匀分布的联合分布"""
        mu = self.normal_mu_var.get()
        sigma = self.normal_sigma_var.get()
        a = self.a_var.get()
        b = self.b_var.get()
        
        if sigma <= 0 or a >= b:
            messagebox.showerror("参数错误", "参数必须满足: σ > 0, a < b")
            return
        
        # 创建子图
        ax1 = self.fig1.add_subplot(221)  # 正态分布
        ax2 = self.fig1.add_subplot(222)  # 均匀分布
        ax3 = self.fig1.add_subplot(212)  # 联合分布
        
        # 生成正态分布数据
        x_normal = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y_normal = stats.norm.pdf(x_normal, mu, sigma)
        
        # 生成均匀分布数据
        x_uniform = np.linspace(a-0.5, b+0.5, 1000)
        y_uniform = np.zeros_like(x_uniform)
        mask = (x_uniform >= a) & (x_uniform <= b)
        y_uniform[mask] = 1.0 / (b - a)
        
        # 绘制正态分布
        ax1.plot(x_normal, y_normal, 'b-', linewidth=2)
        ax1.fill_between(x_normal, y_normal, color='lightblue', alpha=0.5)
        ax1.set_title(f"正态分布 (μ={mu:.2f}, σ={sigma:.2f})", fontsize=10)
        ax1.set_xlabel("x", fontsize=8)
        ax1.set_ylabel("概率密度", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制均匀分布
        ax2.plot(x_uniform, y_uniform, 'g-', linewidth=2)
        ax2.fill_between(x_uniform, y_uniform, color='lightgreen', alpha=0.5)
        ax2.set_title(f"均匀分布 (a={a:.2f}, b={b:.2f})", fontsize=10)
        ax2.set_xlabel("x", fontsize=8)
        ax2.set_ylabel("概率密度", fontsize=8)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 创建联合分布的热图数据
        x_grid = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
        y_grid = np.linspace(a-0.5, b+0.5, 100)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # 计算联合概率密度（假设独立）
        Z = np.zeros_like(X)
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                x_val = X[i, j]
                y_val = Y[i, j]
                
                # 计算正态分布的概率密度
                normal_pdf = stats.norm.pdf(x_val, mu, sigma)
                
                # 计算均匀分布的概率密度
                uniform_pdf = 0
                if a <= y_val <= b:
                    uniform_pdf = 1.0 / (b - a)
                
                # 联合概率密度（假设独立）
                Z[i, j] = normal_pdf * uniform_pdf
        
        # 绘制联合分布热图
        im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                      extent=[x_grid.min(), x_grid.max(), y_grid.min(), y_grid.max()])
        self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率密度')
        
        ax3.set_title("联合分布 (假设独立)", fontsize=12)
        ax3.set_xlabel("正态分布 (X)", fontsize=10)
        ax3.set_ylabel("均匀分布 (Y)", fontsize=10)
    
        # 调整子图布局
        self.fig1.tight_layout()
    
    def plot_1d_normal_expectation(self):
        """绘制一维正态分布的期望与方差"""
        mu = self.exp_mu_var.get()
        sigma = self.exp_sigma_var.get()
        
        if sigma <= 0:
            messagebox.showerror("参数错误", "标准差必须大于0")
            return
        
        # 创建子图
        ax = self.fig2.add_subplot(111)
        
        # 生成数据
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y = stats.norm.pdf(x, mu, sigma)
        
        # 绘制正态分布曲线
        ax.plot(x, y, 'b-', linewidth=2, label='概率密度函数')
        ax.fill_between(x, y, color='lightblue', alpha=0.3)
        
        # 标记期望位置
        ax.axvline(x=mu, color='r', linestyle='--', linewidth=2, label='期望 (μ)')
        ax.plot(mu, stats.norm.pdf(mu, mu, sigma), 'ro', markersize=8)
        
        # 标记标准差范围
        ax.axvline(x=mu-sigma, color='g', linestyle=':', linewidth=1.5, label='μ±σ')
        ax.axvline(x=mu+sigma, color='g', linestyle=':', linewidth=1.5)
        
        # 填充标准差范围
        x_fill = np.linspace(mu-sigma, mu+sigma, 100)
        y_fill = stats.norm.pdf(x_fill, mu, sigma)
        ax.fill_between(x_fill, y_fill, color='lightgreen', alpha=0.3)
        
        # 标记2倍标准差范围
        ax.axvline(x=mu-2*sigma, color='orange', linestyle=':', linewidth=1, label='μ±2σ')
        ax.axvline(x=mu+2*sigma, color='orange', linestyle=':', linewidth=1)
        
        # 设置标题和标签
        ax.set_title(f"一维正态分布的期望与方差", fontsize=14)
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("概率密度", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper right')
        
        # 设置坐标轴范围
        ax.set_xlim(mu - 4*sigma, mu + 4*sigma)
        y_max = stats.norm.pdf(mu, mu, sigma) * 1.1
        ax.set_ylim(0, y_max)
        
        # 计算并显示统计量
        variance = sigma**2
        
        # 计算在不同标准差范围内的概率
        prob_1sigma = stats.norm.cdf(mu + sigma, mu, sigma) - stats.norm.cdf(mu - sigma, mu, sigma)
        prob_2sigma = stats.norm.cdf(mu + 2*sigma, mu, sigma) - stats.norm.cdf(mu - 2*sigma, mu, sigma)
        prob_3sigma = stats.norm.cdf(mu + 3*sigma, mu, sigma) - stats.norm.cdf(mu - 3*sigma, mu, sigma)
        result_text = f"期望 (μ): {mu:.4f}\n"
        result_text += f"方差 (σ²): {variance:.4f}\n"
        result_text += f"标准差 (σ): {sigma:.4f}\n\n"
        result_text += f"概率分布特性:\n"
        result_text += f"P(μ-σ < X < μ+σ): {prob_1sigma:.4f} (约68.27%)\n"
        result_text += f"P(μ-2σ < X < μ+2σ): {prob_2sigma:.4f} (约95.45%)\n"
        result_text += f"P(μ-3σ < X < μ+3σ): {prob_3sigma:.4f} (约99.73%)\n"
        
        self.result_text2.insert(tk.END, result_text)
    
    def plot_2d_normal_expectation(self):
        """绘制二维正态分布的期望与方差"""
        mu1 = self.exp_mu1_var.get()
        mu2 = self.exp_mu2_var.get()
        sigma1 = self.exp_sigma1_var.get()
        sigma2 = self.exp_sigma2_var.get()
        rho = self.exp_rho_var.get()
        
        if sigma1 <= 0 or sigma2 <= 0:
            messagebox.showerror("参数错误", "标准差必须大于0")
            return
        
        if rho <= -1 or rho >= 1:
            messagebox.showerror("参数错误", "相关系数必须在-1到1之间")
            return
        
        # 创建子图
        ax = self.fig2.add_subplot(111)
        
        # 生成网格数据
        x = np.linspace(mu1 - 3*sigma1, mu1 + 3*sigma1, 100)
        y = np.linspace(mu2 - 3*sigma2, mu2 + 3*sigma2, 100)
        X, Y = np.meshgrid(x, y)
        
        # 计算二维正态分布的概率密度
        Z = self.bivariate_normal(X, Y, mu1, mu2, sigma1, sigma2, rho)
        
        # 绘制等高线图
        contour = ax.contourf(X, Y, Z, 20, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, Z, 20, colors='k', linewidths=0.5, alpha=0.5)
        self.fig2.colorbar(contour, ax=ax, shrink=0.8, label='概率密度')
        
        # 标记期望位置
        ax.plot(mu1, mu2, 'ro', markersize=10, label='期望 (μ₁,μ₂)')
        
        # 绘制协方差椭圆
        cov_matrix = np.array([[sigma1**2, rho*sigma1*sigma2], 
                               [rho*sigma1*sigma2, sigma2**2]])
        
        # 绘制1σ, 2σ, 3σ椭圆
        self.plot_cov_ellipse(ax, [mu1, mu2], cov_matrix, n_std=1.0, 
                             label='1σ椭圆', edgecolor='green', facecolor='lightgreen', alpha=0.3)
        self.plot_cov_ellipse(ax, [mu1, mu2], cov_matrix, n_std=2.0, 
                             label='2σ椭圆', edgecolor='orange', facecolor='none', linestyle='--')
        self.plot_cov_ellipse(ax, [mu1, mu2], cov_matrix, n_std=3.0, 
                             label='3σ椭圆', edgecolor='red', facecolor='none', linestyle=':')
        
        # 设置标题和标签
        ax.set_title(f"二维正态分布的期望与协方差", fontsize=14)
        ax.set_xlabel("X", fontsize=12)
        ax.set_ylabel("Y", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper right')
        
        # 设置坐标轴范围
        ax.set_xlim(mu1 - 3*sigma1, mu1 + 3*sigma1)
        ax.set_ylim(mu2 - 3*sigma2, mu2 + 3*sigma2)
        
        # 计算并显示统计量
        variance1 = sigma1**2
        variance2 = sigma2**2
        covariance = rho * sigma1 * sigma2
        
        # 更新结果文本
        result_text = f"X期望 (μ₁): {mu1:.4f}\n"
        result_text += f"Y期望 (μ₂): {mu2:.4f}\n\n"
        result_text += f"X方差 (σ₁²): {variance1:.4f}\n"
        result_text += f"Y方差 (σ₂²): {variance2:.4f}\n"
        result_text += f"协方差: {covariance:.4f}\n"
        result_text += f"相关系数 (ρ): {rho:.4f}\n\n"
        
        # 计算协方差矩阵的行列式和特征值
        det_cov = np.linalg.det(cov_matrix)
        eigenvalues, _ = np.linalg.eig(cov_matrix)
        
        result_text += f"协方差矩阵:\n"
        result_text += f"[{sigma1**2:.4f}, {covariance:.4f}]\n"
        result_text += f"[{covariance:.4f}, {sigma2**2:.4f}]\n\n"
        result_text += f"协方差矩阵行列式: {det_cov:.4f}\n"
        result_text += f"特征值: λ₁={eigenvalues[0]:.4f}, λ₂={eigenvalues[1]:.4f}\n"
        
        self.result_text2.insert(tk.END, result_text)
    
    def plot_normal_transformation(self, ax1, ax2, ax3, transform_func, transform_expr):
        """绘制正态分布的随机变量变换"""
        mu = self.orig_mu_var.get()
        sigma = self.orig_sigma_var.get()
        
        if sigma <= 0:
            messagebox.showerror("参数错误", "标准差必须大于0")
            return
        
        # 生成原始分布数据
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        pdf_x = stats.norm.pdf(x, mu, sigma)
        
        # 绘制原始分布
        ax1.plot(x, pdf_x, 'b-', linewidth=2)
        ax1.fill_between(x, pdf_x, color='lightblue', alpha=0.5)
        ax1.set_title(f"原始正态分布 (μ={mu:.2f}, σ={sigma:.2f})", fontsize=10)
        ax1.set_xlabel("x", fontsize=8)
        ax1.set_ylabel("概率密度", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制变换函数
        x_func = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        try:
            # 处理可能的定义域问题，例如 log(x) for x <= 0
            with np.errstate(divide='ignore', invalid='ignore'):
                y_func = transform_func(x_func)
            # 过滤掉 NaN 或 Inf 值，避免绘图错误
            valid_indices = np.isfinite(y_func)
            x_func_valid = x_func[valid_indices]
            y_func_valid = y_func[valid_indices]

            if len(x_func_valid) > 0:
                ax2.plot(x_func_valid, y_func_valid, 'g-', linewidth=2)
            else:
                 ax2.text(0.5, 0.5, '变换函数在此区间无定义', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)

            ax2.set_title(f"变换函数 Y = g(X) = ${sp.latex(transform_expr)}$", fontsize=10) # Use LaTeX rendering
            ax2.set_xlabel("x", fontsize=8)
            ax2.set_ylabel("y = g(x)", fontsize=8)
            ax2.grid(True, linestyle='--', alpha=0.7)

            # 标记期望位置
            ax2.axvline(x=mu, color='r', linestyle='--', linewidth=1)
            try:
                y_mu = transform_func(mu)
                if np.isfinite(y_mu):
                    ax2.plot(mu, y_mu, 'ro', markersize=6)
            except Exception:
                pass # Ignore if transformation fails at mu

            # 生成蒙特卡洛样本来估计变换后的分布
            np.random.seed(42)  # 设置随机种子以便结果可重现
            samples_x = np.random.normal(mu, sigma, 10000)
            with np.errstate(divide='ignore', invalid='ignore'):
                samples_y = transform_func(samples_x)
            samples_y = samples_y[np.isfinite(samples_y)] # Filter out non-finite results

            if len(samples_y) == 0:
                 ax3.text(0.5, 0.5, '无有效变换样本', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
                 result_text = "无法生成变换后的样本。\n请检查变换函数和分布参数。"
                 if self.result_text3 and self.result_text3.winfo_exists():
                     self.result_text3.insert(tk.END, result_text)
                 return

            # 绘制变换后的分布直方图
            ax3.hist(samples_y, bins=50, density=True, alpha=0.7, color='lightgreen')

            # 使用核密度估计绘制平滑曲线
            try:
                if len(np.unique(samples_y)) > 1: # KDE needs more than 1 unique point
                    kde = stats.gaussian_kde(samples_y)
                    y_min, y_max = np.min(samples_y), np.max(samples_y)
                    # Add a small margin for plotting range
                    margin = (y_max - y_min) * 0.1 if y_max > y_min else 1
                    y_range = np.linspace(y_min - margin, y_max + margin, 1000)
                    ax3.plot(y_range, kde(y_range), 'g-', linewidth=2)
            except Exception as kde_e:
                print(f"KDE failed: {kde_e}") # Log KDE error
                pass  # 如果核密度估计失败，就只显示直方图

            ax3.set_title(f"变换后的分布 Y = ${sp.latex(transform_expr)}$", fontsize=12) # Use LaTeX rendering
            ax3.set_xlabel("y", fontsize=10)
            ax3.set_ylabel("概率密度", fontsize=10)
            ax3.grid(True, linestyle='--', alpha=0.7)

            # 计算变换后的期望和方差
            E_Y = np.mean(samples_y)
            Var_Y = np.var(samples_y)

            # 标记变换后的期望
            ax3.axvline(x=E_Y, color='r', linestyle='--', linewidth=2, label=f'E[Y] ≈ {E_Y:.4f}')
            ax3.legend()

            # 更新结果文本
            result_text = f"原始分布: 正态分布 (μ={mu:.4f}, σ={sigma:.4f})\n"
            result_text += f"变换函数: Y = g(X) = {transform_expr}\n\n"
            result_text += f"原始分布的期望: E[X] = {mu:.4f}\n"
            result_text += f"原始分布的方差: Var[X] = {sigma**2:.4f}\n\n"
            result_text += f"变换后的期望 (蒙特卡洛估计): E[Y] ≈ {E_Y:.4f}\n"
            result_text += f"变换后的方差 (蒙特卡洛估计): Var[Y] ≈ {Var_Y:.4f}\n"

            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.insert(tk.END, result_text)

        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制正态变换时出错: {e}")
            self.fig3.clear() # Clear figure on error
            self.canvas3.draw_idle()


    def plot_uniform_transformation(self, ax1, ax2, ax3, transform_func, transform_expr):
        """绘制均匀分布的随机变量变换"""
        a = self.orig_a_var.get()
        b = self.orig_b_var.get()

        if a >= b:
            messagebox.showerror("参数错误", "下限 a 必须小于上限 b")
            return

        # 生成原始分布数据
        x = np.linspace(a - (b-a)*0.1, b + (b-a)*0.1, 1000) # Add margin
        pdf_x = np.zeros_like(x)
        mask = (x >= a) & (x <= b)
        pdf_x[mask] = 1.0 / (b - a) if b > a else 0

        # 绘制原始分布
        ax1.plot(x, pdf_x, 'b-', linewidth=2)
        ax1.fill_between(x[mask], pdf_x[mask], color='lightblue', alpha=0.5) # Fill only where defined
        ax1.set_title(f"原始均匀分布 (a={a:.2f}, b={b:.2f})", fontsize=10)
        ax1.set_xlabel("x", fontsize=8)
        ax1.set_ylabel("概率密度", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_ylim(bottom=0) # Ensure y-axis starts at 0

        # 绘制变换函数
        x_func = np.linspace(a, b, 1000) # Focus on the interval [a, b]
        try:
            # Handle potential domain issues
            with np.errstate(divide='ignore', invalid='ignore'):
                y_func = transform_func(x_func)
            valid_indices = np.isfinite(y_func)
            x_func_valid = x_func[valid_indices]
            y_func_valid = y_func[valid_indices]

            if len(x_func_valid) > 0:
                ax2.plot(x_func_valid, y_func_valid, 'g-', linewidth=2)
            else:
                ax2.text(0.5, 0.5, '变换函数在 [a, b] 无定义', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)

            ax2.set_title(f"变换函数 Y = g(X) = ${sp.latex(transform_expr)}$", fontsize=10) # Use LaTeX
            ax2.set_xlabel("x", fontsize=8)
            ax2.set_ylabel("y = g(x)", fontsize=8)
            ax2.grid(True, linestyle='--', alpha=0.7)

            # 标记期望位置
            mu = (a + b) / 2  # 均匀分布的期望
            ax2.axvline(x=mu, color='r', linestyle='--', linewidth=1)
            try:
                y_mu = transform_func(mu)
                if np.isfinite(y_mu):
                    ax2.plot(mu, y_mu, 'ro', markersize=6)
            except Exception:
                pass # Ignore if transformation fails at mu

            # 生成蒙特卡洛样本来估计变换后的分布
            np.random.seed(42)  # 设置随机种子以便结果可重现
            samples_x = np.random.uniform(a, b, 10000)
            with np.errstate(divide='ignore', invalid='ignore'):
                samples_y = transform_func(samples_x)
            samples_y = samples_y[np.isfinite(samples_y)] # Filter out non-finite results

            if len(samples_y) == 0:
                 ax3.text(0.5, 0.5, '无有效变换样本', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
                 result_text = "无法生成变换后的样本。\n请检查变换函数和分布参数。"
                 if self.result_text3 and self.result_text3.winfo_exists():
                     self.result_text3.insert(tk.END, result_text)
                 return

            # 绘制变换后的分布直方图
            ax3.hist(samples_y, bins=50, density=True, alpha=0.7, color='lightgreen')

            # 使用核密度估计绘制平滑曲线
            try:
                if len(np.unique(samples_y)) > 1: # KDE needs more than 1 unique point
                    kde = stats.gaussian_kde(samples_y)
                    y_min, y_max = np.min(samples_y), np.max(samples_y)
                    margin = (y_max - y_min) * 0.1 if y_max > y_min else 1
                    y_range = np.linspace(y_min - margin, y_max + margin, 1000)
                    ax3.plot(y_range, kde(y_range), 'g-', linewidth=2)
            except Exception as kde_e:
                print(f"KDE failed: {kde_e}")
                pass  # 如果核密度估计失败，就只显示直方图

            ax3.set_title(f"变换后的分布 Y = ${sp.latex(transform_expr)}$", fontsize=12) # Use LaTeX
            ax3.set_xlabel("y", fontsize=10)
            ax3.set_ylabel("概率密度", fontsize=10)
            ax3.grid(True, linestyle='--', alpha=0.7)

            # 计算变换后的期望和方差
            E_Y = np.mean(samples_y)
            Var_Y = np.var(samples_y)

            # 标记变换后的期望
            ax3.axvline(x=E_Y, color='r', linestyle='--', linewidth=2, label=f'E[Y] ≈ {E_Y:.4f}')
            ax3.legend()

            # 更新结果文本
            result_text = f"原始分布: 均匀分布 (a={a:.4f}, b={b:.4f})\n"
            result_text += f"变换函数: Y = g(X) = {transform_expr}\n\n"
            result_text += f"原始分布的期望: E[X] = {mu:.4f}\n"
            result_text += f"原始分布的方差: Var[X] = {(b-a)**2/12:.4f}\n\n"
            result_text += f"变换后的期望 (蒙特卡洛估计): E[Y] ≈ {E_Y:.4f}\n"
            result_text += f"变换后的方差 (蒙特卡洛估计): Var[Y] ≈ {Var_Y:.4f}\n"

            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.insert(tk.END, result_text)

        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制均匀变换时出错: {e}")
            self.fig3.clear() # Clear figure on error
            self.canvas3.draw_idle()


    def plot_exponential_transformation(self, ax1, ax2, ax3, transform_func, transform_expr):
        """绘制指数分布的随机变量变换"""
        lambd = self.orig_lambda_var.get()

        if lambd <= 0:
            messagebox.showerror("参数错误", "率参数 λ 必须大于0")
            return

        # 生成原始分布数据
        # Determine a reasonable upper bound for x based on lambda
        # e.g., where CDF is close to 1 (e.g., 0.999) -> 1 - exp(-lambda*x) = 0.999 -> x = -ln(0.001)/lambda
        x_max = -np.log(0.001) / lambd if lambd > 0 else 10 # Default if lambda is somehow 0
        x = np.linspace(0, x_max, 1000)
        pdf_x = lambd * np.exp(-lambd * x)

        # 绘制原始分布
        ax1.plot(x, pdf_x, 'b-', linewidth=2)
        ax1.fill_between(x, pdf_x, color='lightblue', alpha=0.5)
        ax1.set_title(f"原始指数分布 (λ={lambd:.2f})", fontsize=10)
        ax1.set_xlabel("x", fontsize=8)
        ax1.set_ylabel("概率密度", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_ylim(bottom=0) # Ensure y-axis starts at 0

        # 绘制变换函数
        x_func = np.linspace(1e-9, x_max, 1000) # Start slightly > 0 for functions like log(x)
        try:
            # Handle potential domain issues
            with np.errstate(divide='ignore', invalid='ignore'):
                y_func = transform_func(x_func)
            valid_indices = np.isfinite(y_func)
            x_func_valid = x_func[valid_indices]
            y_func_valid = y_func[valid_indices]

            if len(x_func_valid) > 0:
                ax2.plot(x_func_valid, y_func_valid, 'g-', linewidth=2)
            else:
                ax2.text(0.5, 0.5, '变换函数在 x > 0 无定义', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)

            ax2.set_title(f"变换函数 Y = g(X) = ${sp.latex(transform_expr)}$", fontsize=10) # Use LaTeX
            ax2.set_xlabel("x", fontsize=8)
            ax2.set_ylabel("y = g(x)", fontsize=8)
            ax2.grid(True, linestyle='--', alpha=0.7)

            # 标记期望位置
            mu = 1 / lambd  # 指数分布的期望
            ax2.axvline(x=mu, color='r', linestyle='--', linewidth=1)
            try:
                y_mu = transform_func(mu)
                if np.isfinite(y_mu):
                    ax2.plot(mu, y_mu, 'ro', markersize=6)
            except Exception:
                pass # Ignore if transformation fails at mu

            # 生成蒙特卡洛样本来估计变换后的分布
            np.random.seed(42)  # 设置随机种子以便结果可重现
            samples_x = np.random.exponential(scale=1/lambd, size=10000)
            with np.errstate(divide='ignore', invalid='ignore'):
                samples_y = transform_func(samples_x)
            samples_y = samples_y[np.isfinite(samples_y)] # Filter out non-finite results

            if len(samples_y) == 0:
                 ax3.text(0.5, 0.5, '无有效变换样本', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
                 result_text = "无法生成变换后的样本。\n请检查变换函数和分布参数。"
                 if self.result_text3 and self.result_text3.winfo_exists():
                     self.result_text3.insert(tk.END, result_text)
                 return

            # 绘制变换后的分布直方图
            ax3.hist(samples_y, bins=50, density=True, alpha=0.7, color='lightgreen')

            # 使用核密度估计绘制平滑曲线
            try:
                if len(np.unique(samples_y)) > 1: # KDE needs more than 1 unique point
                    kde = stats.gaussian_kde(samples_y)
                    y_min, y_max = np.min(samples_y), np.max(samples_y)
                    margin = (y_max - y_min) * 0.1 if y_max > y_min else 1
                    y_range = np.linspace(y_min - margin, y_max + margin, 1000)
                    ax3.plot(y_range, kde(y_range), 'g-', linewidth=2)
            except Exception as kde_e:
                print(f"KDE failed: {kde_e}")
                pass  # 如果核密度估计失败，就只显示直方图

            ax3.set_title(f"变换后的分布 Y = ${sp.latex(transform_expr)}$", fontsize=12) # Use LaTeX
            ax3.set_xlabel("y", fontsize=10)
            ax3.set_ylabel("概率密度", fontsize=10)
            ax3.grid(True, linestyle='--', alpha=0.7)

            # 计算变换后的期望和方差
            E_Y = np.mean(samples_y)
            Var_Y = np.var(samples_y)

            # 标记变换后的期望
            ax3.axvline(x=E_Y, color='r', linestyle='--', linewidth=2, label=f'E[Y] ≈ {E_Y:.4f}')
            ax3.legend()

            # 更新结果文本
            result_text = f"原始分布: 指数分布 (λ={lambd:.4f})\n"
            result_text += f"变换函数: Y = g(X) = {transform_expr}\n\n"
            result_text += f"原始分布的期望: E[X] = {mu:.4f}\n"
            result_text += f"原始分布的方差: Var[X] = {1/(lambd**2):.4f}\n\n"
            result_text += f"变换后的期望 (蒙特卡洛估计): E[Y] ≈ {E_Y:.4f}\n"
            result_text += f"变换后的方差 (蒙特卡洛估计): Var[Y] ≈ {Var_Y:.4f}\n"

            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.insert(tk.END, result_text)

        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制指数变换时出错: {e}")
            self.fig3.clear() # Clear figure on error
            self.canvas3.draw_idle()
    
    def get_linear_coeffs(self, expr, x):
        """从线性表达式中提取系数 a 和 b (ax + b)"""
        poly = sp.Poly(expr, x)
        if poly.degree() == 1:
            return poly.all_coeffs()  # 返回 [a, b]
        elif poly.degree() == 0:
            return [0, poly.all_coeffs()[0]]  # 返回 [0, b]
        else:
            raise ValueError("表达式不是线性的")
    
    def plot_cov_ellipse(self, ax, pos, cov, n_std=1.0, **kwargs):
        """
        绘制协方差椭圆
        
        参数:
        - ax: matplotlib轴对象
        - pos: 椭圆中心位置 [x, y]
        - cov: 协方差矩阵 [[cov00, cov01], [cov10, cov11]]
        - n_std: 椭圆表示的标准差数量
        """
        # 计算特征值和特征向量
        eigenvals, eigenvecs = np.linalg.eigh(cov)
        
        # 椭圆的角度（弧度）
        angle = np.degrees(np.arctan2(eigenvecs[1, 0], eigenvecs[0, 0]))
        
        # 椭圆的宽度和高度
        width, height = 2 * n_std * np.sqrt(eigenvals)
        
        # 创建椭圆
        ellipse = Ellipse(xy=pos, width=width, height=height, angle=angle, **kwargs)
        
        # 添加到轴对象
        ax.add_patch(ellipse)
        
        return ellipse
    
    def plot_joint_distribution(self):
        """绘制联合分布"""
        joint_type = self.joint_type_var.get()
        
        if joint_type == "二项分布与泊松分布":
            self.plot_binom_poisson_joint()
        elif joint_type == "正态分布与均匀分布":
            self.plot_normal_uniform_joint()
    
    def plot_binom_poisson_joint(self):
        """绘制二项分布与泊松分布的联合分布"""
        n = self.n_var.get()
        p = self.p_var.get()
        lambd = self.lambda_var.get()
        
        if n <= 0 or p <= 0 or p >= 1 or lambd <= 0:
            messagebox.showerror("参数错误", "参数必须满足: n > 0, 0 < p < 1, λ > 0")
            return
        
        # 创建子图
        ax1 = self.fig1.add_subplot(221)  # 二项分布
        ax2 = self.fig1.add_subplot(222)  # 泊松分布
        ax3 = self.fig1.add_subplot(212)  # 联合分布
        
        # 生成二项分布数据
        x_binom = np.arange(0, n+1)
        y_binom = stats.binom.pmf(x_binom, n, p)
        
        # 生成泊松分布数据
        x_poisson = np.arange(0, int(lambd*3)+1)
        y_poisson = stats.poisson.pmf(x_poisson, lambd)
        
        # 绘制二项分布
        ax1.bar(x_binom, y_binom, color='lightblue', edgecolor='blue', alpha=0.7)
        ax1.set_title(f"二项分布 (n={n}, p={p:.2f})", fontsize=10)
        ax1.set_xlabel("成功次数", fontsize=8)
        ax1.set_ylabel("概率", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制泊松分布
        ax2.bar(x_poisson, y_poisson, color='lightgreen', edgecolor='green', alpha=0.7)
        ax2.set_title(f"泊松分布 (λ={lambd:.2f})", fontsize=10)
        ax2.set_xlabel("事件发生次数", fontsize=8)
        ax2.set_ylabel("概率", fontsize=8)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 创建联合分布的热图数据
        X, Y = np.meshgrid(x_binom, x_poisson)
        Z = np.zeros_like(X, dtype=float)
        
        # 计算联合概率（假设独立）
        for i in range(len(x_poisson)):
            for j in range(len(x_binom)):
                Z[i, j] = y_poisson[i] * y_binom[j]
        
        # 绘制联合分布热图
        im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                      extent=[-0.5, n+0.5, -0.5, int(lambd*3)+0.5])
        self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率')
        
        ax3.set_title("联合分布 (假设独立)", fontsize=12)
        ax3.set_xlabel("二项分布 (X)", fontsize=10)
        ax3.set_ylabel("泊松分布 (Y)", fontsize=10)
        
        # 调整子图布局
        self.fig1.tight_layout()
    
    def plot_normal_uniform_joint(self):
        """绘制正态分布与均匀分布的联合分布"""
        mu = self.normal_mu_var.get()
        sigma = self.normal_sigma_var.get()
        a = self.a_var.get()
        b = self.b_var.get()
        
        if sigma <= 0 or a >= b:
            messagebox.showerror("参数错误", "参数必须满足: σ > 0, a < b")
            return
        
        # 创建子图
        ax1 = self.fig1.add_subplot(221)  # 正态分布
        ax2 = self.fig1.add_subplot(222)  # 均匀分布
        ax3 = self.fig1.add_subplot(212)  # 联合分布
        
        # 生成正态分布数据
        x_normal = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y_normal = stats.norm.pdf(x_normal, mu, sigma)
        
        # 生成均匀分布数据
        x_uniform = np.linspace(a-0.5, b+0.5, 1000)
        y_uniform = np.zeros_like(x_uniform)
        mask = (x_uniform >= a) & (x_uniform <= b)
        y_uniform[mask] = 1.0 / (b - a)
        
        # 绘制正态分布
        ax1.plot(x_normal, y_normal, 'b-', linewidth=2)
        ax1.fill_between(x_normal, y_normal, color='lightblue', alpha=0.5)
        ax1.set_title(f"正态分布 (μ={mu:.2f}, σ={sigma:.2f})", fontsize=10)
        ax1.set_xlabel("x", fontsize=8)
        ax1.set_ylabel("概率密度", fontsize=8)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制均匀分布
        ax2.plot(x_uniform, y_uniform, 'g-', linewidth=2)
        ax2.fill_between(x_uniform, y_uniform, color='lightgreen', alpha=0.5)
        ax2.set_title(f"均匀分布 (a={a:.2f}, b={b:.2f})", fontsize=10)
        ax2.set_xlabel("x", fontsize=8)
        ax2.set_ylabel("概率密度", fontsize=8)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 创建联合分布的热图数据
        x_grid = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
        y_grid = np.linspace(a-0.5, b+0.5, 100)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # 计算联合概率密度（假设独立）
        Z = np.zeros_like(X)
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                x_val = X[i, j]
                y_val = Y[i, j]
                
                # 计算正态分布的概率密度
                normal_pdf = stats.norm.pdf(x_val, mu, sigma)
                
                # 计算均匀分布的概率密度
                uniform_pdf = 0
                if a <= y_val <= b:
                    uniform_pdf = 1.0 / (b - a)
                
                # 联合概率密度（假设独立）
                Z[i, j] = normal_pdf * uniform_pdf
        
        # 绘制联合分布热图
        im = ax3.imshow(Z, cmap='viridis', aspect='auto', origin='lower',
                      extent=[x_grid.min(), x_grid.max(), y_grid.min(), y_grid.max()])
        self.fig1.colorbar(im, ax=ax3, shrink=0.8, label='联合概率密度')
        
        ax3.set_title("联合分布 (假设独立)", fontsize=12)
        ax3.set_xlabel("正态分布 (X)", fontsize=10)
        ax3.set_ylabel("均匀分布 (Y)", fontsize=10)
    
        # 调整子图布局
        self.fig1.tight_layout()
    
    def clear_plot1(self):
        """清除分布图"""
        if self.canvas1 and self.canvas1.get_tk_widget().winfo_exists():
            self.fig1.clear()
            self.canvas1.draw()
    
    def clear_plot2(self):
        """清除期望与方差图"""
        if self.canvas2 and self.canvas2.get_tk_widget().winfo_exists():
            self.fig2.clear()
            if self.result_text2 and self.result_text2.winfo_exists():
                self.result_text2.delete(1.0, tk.END)
            self.canvas2.draw()
    
    def clear_plot3(self):
        """清除随机变量变换图"""
        if self.canvas3 and self.canvas3.get_tk_widget().winfo_exists():
            self.fig3.clear()
            if self.result_text3 and self.result_text3.winfo_exists():
                self.result_text3.delete(1.0, tk.END)
            self.canvas3.draw()

    def show_theory3(self):
        """显示随机变量变换理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 随机变量变换知识点内容
            sections = {
                "正态分布": """
线性变换：
若X∼N(μ,σ^2)，设Y=aX+b（a不等于0），则Y也服从正态分布，且Y∼N(aμ+b,a^2*σ^2)。这是因为正态分布在线性变换下保持其分布类型不变，只是均值和方差发生了相应的变化。

多个正态分布随机变量的线性组合：
若X1​∼N(μ1​,σ1^2​)，X2​∼N(μ2​,σ2^2​)，且X1​与X2​相互独立，设Y=aX1​+bX2​，则Y服从正态分布N(aμ1​+bμ2​,a^2*σ1^2​+b^2*σ2^2​)。此性质可推广到多个相互独立的正态分布随机变量的线性组合情况。
""",
                "均匀分布": """
线性变换：
设X在区间[a,b]上服从均匀分布，即X∼U(a,b)，其概率密度函数为fX​(x)=1/(b−a)​,a≤x≤b。若Y=cX+d（c不等于0），则Y在区间[ca+d,cb+d]上服从均匀分布，概率密度函数为fY(y)=1/(c(b−a))​,ca+d≤y≤cb+d。

更一般的变换：
对于更复杂的变换Y=g(X)，需要先求出X关于Y的反函数X=h(Y)，然后根据X的概率密度函数fX​(x)和反函数的导数h′(y)来确定Y的概率密度函数f​Y(y)=fX​(h(y))∣h′(y)∣。
""",
                "指数分布": """
线性变换：
设X服从参数为λ的指数分布，即X∼Exp(λ)，概率密度函数为fX​(x)=λexp(−λx),x≥0。若Y=aX（a>0），则Y的概率密度函数为fY​(y)=(λ/a)*​exp(−λ​y/a),y≥0，即Y∼Exp(λ/a​)。

其他变换：
对于一般的变换Y=g(X)，同样可通过求反函数X=h(Y)，利用fY​(y)=fX​(h(y))∣h′(y)∣来确定Y的概率密度函数。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "随机变量变换理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window3()

    def create_theory_window3(self):
        """备选方案：直接创建随机变量变换理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("随机变量变换理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="随机变量变换理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="正态分布")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="均匀分布")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="指数分布")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)
    
    def debounced_update(self, event):
        """防抖动更新，避免输入过程中频繁刷新"""
        widget = event.widget
        
        # 检查输入是否为有效数字
        try:
            float(widget.get())
            # 如果是有效数字，500毫秒后更新图表
            self.master.after(500, self.update_from_entry_and_plot)
        except ValueError:
            pass  # 如果不是有效数字，不更新
    
    def update_from_entry_and_plot(self):
        """从输入框更新变量并重绘图表"""
        # 更新所有输入框对应的变量
        try:
            # 尝试更新tab1的变量
            if hasattr(self, 'mu_entry') and hasattr(self, 'mu_var'):
                self.update_var_from_entry(self.mu_entry, self.mu_var)
            if hasattr(self, 'sigma_entry') and hasattr(self, 'sigma_var'):
                self.update_var_from_entry(self.sigma_entry, self.sigma_var)
            
            # 尝试更新tab2的变量
            if hasattr(self, 'exp_mu_entry') and hasattr(self, 'exp_mu_var'):
                self.update_var_from_entry(self.exp_mu_entry, self.exp_mu_var)
            if hasattr(self, 'exp_sigma_entry') and hasattr(self, 'exp_sigma_var'):
                self.update_var_from_entry(self.exp_sigma_entry, self.exp_sigma_var)
            
            # 根据当前选项卡重绘图表
            tab_id = self.notebook.select()
            tab_name = self.notebook.tab(tab_id, "text")
            
            if tab_name == "单变量与多变量分布":
                self.plot_distribution()
            elif tab_name == "期望与方差":
                self.plot_expectation()
            elif tab_name == "随机变量变换":
                self.plot_transformation()
        except:
            pass  # 忽略任何错误
    
    def on_expectation_dist_change(self, event):
        """期望分布类型变化时的回调函数"""
        dist_type = self.exp_dist_type_var.get()
        
        if dist_type == "一维正态分布":
            self.create_1d_normal_expectation_params()
        elif dist_type == "二维正态分布":
            self.create_2d_normal_expectation_params()
        
        # 重新绘制图表
        self.plot_expectation()