import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import random
import time
from typing import Callable, Optional

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class MonteCarloApp:
    def __init__(self, master):
        self.master = master
        master.title("蒙特卡洛模拟工具")
        self.master.geometry("1200x800") # Increased size for two plots

        # --- Simulation State ---
        self.simulation_running = False
        self.simulation_task = None
        self.total_points = 0
        self.points_inside = 0 # For Pi calculation AND Integral Hit-or-Miss
        # self.sum_f_values = 0.0 # No longer needed for hit-or-miss integral
        self.points_x_inside = []
        self.points_y_inside = []
        self.points_x_outside = []
        self.points_y_outside = []
        # self.integral_points_x = [] # No longer needed for hit-or-miss
        # self.integral_points_y = [] # No longer needed for hit-or-miss
        self.integral_func: Optional[Callable[[float], float]] = None
        self.integral_a: float = 0.0
        self.integral_b: float = 1.0
        self.integral_min_y: float = 0.0 # Min y for bounding box
        self.integral_max_y: float = 1.0 # Max y for bounding box
        self.iteration_history = []
        self.estimate_history = [] # Store Pi or Integral estimates

        # --- Main Layout ---
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Reduced padding slightly

        title_label = ttk.Label(main_frame, text="蒙特卡洛模拟", font=("Arial", 18, "bold"))
        title_label.pack(pady=5)

        # Left Control Panel
        self.control_frame = ttk.LabelFrame(main_frame, text="模拟设置")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Right Area (Plot + Results)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Plot Area - Now contains two subplots
        plot_frame = ttk.Frame(right_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.fig = Figure(figsize=(10, 6)) # Adjusted figure size
        self.ax1 = self.fig.add_subplot(121) # Main simulation plot
        self.ax2 = self.fig.add_subplot(122) # Convergence plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig.tight_layout(pad=3.0) # Add padding between subplots

        # Results Area
        result_frame = ttk.LabelFrame(right_frame, text="模拟结果")
        result_frame.pack(fill=tk.X, pady=5)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=5, width=80, wrap=tk.WORD) # Slightly smaller height
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # Status Bar (Optional but helpful)
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(5, 0))

        # --- Control Panel Widgets ---
        # 1. Simulation Type
        ttk.Label(self.control_frame, text="选择模拟类型:").pack(anchor=tk.W, pady=(10, 2))
        self.sim_type_var = tk.StringVar(value="计算 π 值")
        sim_combobox = ttk.Combobox(self.control_frame, textvariable=self.sim_type_var,
                                    values=["计算 π 值", "估算积分"], width=30, state="readonly")
        sim_combobox.pack(anchor=tk.W, pady=2, fill=tk.X)
        sim_combobox.bind("<<ComboboxSelected>>", self.on_sim_type_change)

        # 2. Simulation Parameters Frame (Dynamic)
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.X, pady=10)

        # 3. Simulation Controls
        control_buttons_frame = ttk.Frame(self.control_frame)
        control_buttons_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(control_buttons_frame, text="开始模拟", command=self.run_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_buttons_frame, text="停止模拟", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(control_buttons_frame, text="重置", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            control_buttons_frame, 
            text="蒙特卡洛模拟理论知识", 
            command=self.show_theory
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
    

        # Points per step
        ttk.Label(self.control_frame, text="每次模拟点数:").pack(anchor=tk.W, pady=(10, 0))
        self.points_per_step_var = tk.IntVar(value=100)
        points_scale = ttk.Scale(self.control_frame, from_=10, to=1000, variable=self.points_per_step_var, orient=tk.HORIZONTAL)
        points_scale.pack(fill=tk.X)
        points_entry = ttk.Entry(self.control_frame, textvariable=self.points_per_step_var, width=10)
        points_entry.pack(anchor=tk.W)

        # Speed Control
        speed_frame = ttk.Frame(self.control_frame)
        speed_frame.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(speed_frame, text="模拟速度 (点/批):").pack(side=tk.LEFT, padx=(0, 5))
        self.speed_var = tk.IntVar(value=100) # Points per batch/update
        speed_scale = ttk.Scale(speed_frame, from_=10, to=1000, orient=tk.HORIZONTAL,
                                variable=self.speed_var, length=150)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        speed_label = ttk.Label(speed_frame, textvariable=self.speed_var, width=4)
        speed_label.pack(side=tk.LEFT, padx=(5, 0))

        # --- Initial Setup ---
        self.create_param_ui()
        self.setup_plot()
        self.update_results()

    def on_sim_type_change(self, event=None):
        """Handle changes in the simulation type selection."""
        # Clear previous parameter widgets
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        sim_type = self.sim_type_var.get()

        if sim_type == "计算 π 值":
            # No specific parameters needed for Pi calculation in this setup
            ttk.Label(self.param_frame, text="使用单位正方形 [0,1]x[0,1]").pack(pady=5)

        elif sim_type == "估算积分":
            # Function string
            ttk.Label(self.param_frame, text="函数 f(x):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.func_str_var = tk.StringVar(value="x**2")
            ttk.Entry(self.param_frame, textvariable=self.func_str_var, width=25).grid(row=0, column=1, columnspan=3, sticky=tk.EW, pady=2)

            # Integration limits [a, b]
            ttk.Label(self.param_frame, text="积分下限 a:").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.a_var = tk.DoubleVar(value=0.0)
            ttk.Entry(self.param_frame, textvariable=self.a_var, width=8).grid(row=1, column=1, sticky=tk.W, pady=2)
            ttk.Label(self.param_frame, text="积分上限 b:").grid(row=1, column=2, sticky=tk.W, pady=2)
            self.b_var = tk.DoubleVar(value=1.0)
            ttk.Entry(self.param_frame, textvariable=self.b_var, width=8).grid(row=1, column=3, sticky=tk.W, pady=2)

            # Bounding box limits [min_y, max_y] for Hit-or-Miss
            ttk.Label(self.param_frame, text="采样 Y 最小值:").grid(row=2, column=0, sticky=tk.W, pady=2)
            self.min_y_var = tk.DoubleVar(value=0.0)
            ttk.Entry(self.param_frame, textvariable=self.min_y_var, width=8).grid(row=2, column=1, sticky=tk.W, pady=2)
            ttk.Label(self.param_frame, text="采样 Y 最大值:").grid(row=2, column=2, sticky=tk.W, pady=2)
            self.max_y_var = tk.DoubleVar(value=1.0) # User should adjust this based on function
            ttk.Entry(self.param_frame, textvariable=self.max_y_var, width=8).grid(row=2, column=3, sticky=tk.W, pady=2)
            ttk.Button(self.param_frame, text="自动估算Y范围", command=self.auto_estimate_y_range).grid(row=3, column=0, columnspan=4, pady=5)

        # Reset plot and results when type changes
        self.reset_simulation()

    def create_param_ui(self):
        """Create specific parameter widgets based on simulation type."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        sim_type = self.sim_type_var.get()

        if sim_type == "计算 π 值":
            # No specific parameters needed for Pi calculation itself
            ttk.Label(self.param_frame, text="使用单位正方形和内切圆进行模拟。").pack(anchor=tk.W)
        elif sim_type == "估算积分":
            # Function input
            ttk.Label(self.param_frame, text="函数 f(x):").pack(anchor=tk.W)
            self.func_str_var = tk.StringVar(value="x**2")
            func_entry = ttk.Entry(self.param_frame, textvariable=self.func_str_var, width=30)
            func_entry.pack(anchor=tk.W, fill=tk.X)
            func_entry.bind("<FocusOut>", self.update_integral_function) # Update when focus leaves
            func_entry.bind("<Return>", self.update_integral_function) # Update on Enter

            # Integration bounds
            bounds_frame = ttk.Frame(self.param_frame)
            bounds_frame.pack(fill=tk.X, pady=5)
            ttk.Label(bounds_frame, text="积分下限 (a):").pack(side=tk.LEFT)
            self.integral_a_var = tk.DoubleVar(value=0.0)
            a_entry = ttk.Entry(bounds_frame, textvariable=self.integral_a_var, width=8)
            a_entry.pack(side=tk.LEFT, padx=5)
            a_entry.bind("<FocusOut>", self.update_integral_function)
            a_entry.bind("<Return>", self.update_integral_function)

            ttk.Label(bounds_frame, text="积分上限 (b):").pack(side=tk.LEFT)
            self.integral_b_var = tk.DoubleVar(value=1.0)
            b_entry = ttk.Entry(bounds_frame, textvariable=self.integral_b_var, width=8)
            b_entry.pack(side=tk.LEFT, padx=5)
            b_entry.bind("<FocusOut>", self.update_integral_function)
            b_entry.bind("<Return>", self.update_integral_function)

            # Max Y (optional, for hit-or-miss) - Can be added later if needed
            # ttk.Label(self.param_frame, text="函数在[a,b]上的最大值(可选):").pack(anchor=tk.W)
            # self.integral_max_y_var = tk.DoubleVar(value=1.0) # Or calculate automatically
            # max_y_entry = ttk.Entry(self.param_frame, textvariable=self.integral_max_y_var, width=10)
            # max_y_entry.pack(anchor=tk.W)

            self.update_integral_function() # Initial function parse

    def update_integral_function(self, event=None):
        """解析函数字符串并更新积分函数"""
        func_str = self.func_str_var.get().strip()
        
        # 检查是否为空
        if not func_str:
            self.integral_func = None
            self.status_var.set("错误: 请输入函数表达式")
            return False
        
        try:
            # 安全的函数评估环境
            safe_dict = {
                "x": 0.5,  # 测试值
                "math": math,
                "np": np,
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "exp": np.exp, "log": np.log, "log10": np.log10,
                "sqrt": np.sqrt, "abs": np.abs, "pi": np.pi,
                "e": np.e
            }
            
            # 测试函数是否可以被解析和执行
            eval(func_str, {"__builtins__": {}}, safe_dict)
            
            # 如果测试成功，创建实际的函数对象
            def func(x):
                safe_locals = safe_dict.copy()
                safe_locals["x"] = x
                return eval(func_str, {"__builtins__": {}}, safe_locals)
            
            # 测试函数在积分区间的端点
            a = self.a_var.get()
            b = self.b_var.get()
            func(a)  # 测试下限
            func(b)  # 测试上限
            
            # 更新积分函数和边界
            self.integral_func = func
            self.integral_a = a
            self.integral_b = b
            
            # 尝试自动估计Y范围
            try:
                x_samples = np.linspace(a, b, 20)  # 少量样本点用于快速检查
                y_samples = [func(x) for x in x_samples]
                self.integral_min_y = min(0, min(y_samples))  # 确保包含0
                self.integral_max_y = max(0, max(y_samples))  # 确保包含0
                
                # 添加一些边距
                padding = (self.integral_max_y - self.integral_min_y) * 0.2
                self.integral_min_y -= padding
                self.integral_max_y += padding
                
                # 更新UI中的值（如果存在）
                if hasattr(self, 'min_y_var'):
                    self.min_y_var.set(round(self.integral_min_y, 4))
                if hasattr(self, 'max_y_var'):
                    self.max_y_var.set(round(self.integral_max_y, 4))
            except Exception:
                # 如果自动估计失败，使用默认值
                self.integral_min_y = 0.0
                self.integral_max_y = 1.0
            
            self.status_var.set(f"函数已设置: f(x) = {func_str}")
            return True
            
        except Exception as e:
            self.integral_func = None
            error_msg = str(e)
            self.status_var.set(f"函数解析错误: {error_msg}")
            return False

    def setup_plot(self):
        """Set up the plot area based on the simulation type."""
        self.ax1.clear()
        self.ax2.clear()
        sim_type = self.sim_type_var.get()

        # --- Setup Convergence Plot (ax2) ---
        self.ax2.set_xlabel("模拟点数")
        self.ax2.set_ylabel("估算值")
        self.ax2.grid(True, linestyle='--', alpha=0.6)
        self.line_estimate, = self.ax2.plot([], [], 'b-', label='估算值') # Line object for estimates
        self.line_true = None # Placeholder for true value line

        # --- Setup Main Simulation Plot (ax1) ---
        if sim_type == "计算 π 值":
            self.ax1.set_title("蒙特卡洛计算 π")
            self.ax1.set_xlabel("X")
            self.ax1.set_ylabel("Y")
            self.ax1.set_xlim(0, 1)
            self.ax1.set_ylim(0, 1)
            self.ax1.set_aspect('equal', adjustable='box')
            circle = plt.Circle((0, 0), 1, color='blue', fill=False, linestyle='--', alpha=0.7)
            self.ax1.add_patch(circle)
            self.ax1.grid(True, linestyle='--', alpha=0.6)
            # Initialize scatter plots for points
            self.scatter_inside, = self.ax1.plot([], [], 'go', markersize=2, alpha=0.6, label='内部')
            self.scatter_outside, = self.ax1.plot([], [], 'ro', markersize=2, alpha=0.6, label='外部')
            self.ax1.legend(loc='upper right')

            # Setup convergence plot specific for Pi
            self.ax2.set_title("π 估算值收敛过程")
            self.line_true = self.ax2.axhline(math.pi, color='r', linestyle='--', label=f'真实 π ≈ {math.pi:.6f}')
            self.ax2.legend()

        elif sim_type == "估算积分":
            self.ax1.set_title("蒙特卡洛估算积分 (Hit-or-Miss)")
            self.ax1.set_xlabel("X")
            self.ax1.set_ylabel("Y")
            # Plot the function itself
            if self.integral_func and self.integral_a < self.integral_b:
                x_func = np.linspace(self.integral_a, self.integral_b, 200)
                try:
                    y_func = [self.integral_func(x) for x in x_func]
                    self.ax1.plot(x_func, y_func, 'b-', label=f'f(x)={self.func_str_var.get()}', linewidth=2)
                except Exception as e:
                    print(f"Error plotting function: {e}")
                    messagebox.showwarning("绘图错误", f"无法绘制函数图像: {e}")

            # Draw the bounding box
            rect = plt.Rectangle((self.integral_a, self.integral_min_y),
                                 self.integral_b - self.integral_a,
                                 self.integral_max_y - self.integral_min_y,
                                 fill=False, color='purple', linestyle='--', label='采样区域')
            self.ax1.add_patch(rect)
            self.ax1.set_xlim(self.integral_a - 0.1 * (self.integral_b - self.integral_a),
                            self.integral_b + 0.1 * (self.integral_b - self.integral_a))
            self.ax1.set_ylim(self.integral_min_y - 0.1 * abs(self.integral_max_y - self.integral_min_y),
                            self.integral_max_y + 0.1 * abs(self.integral_max_y - self.integral_min_y))
            self.ax1.grid(True, linestyle='--', alpha=0.6)

            # Initialize scatter plots for points (hits and misses)
            self.scatter_inside, = self.ax1.plot([], [], 'go', markersize=2, alpha=0.6, label='命中 (Hit)')
            self.scatter_outside, = self.ax1.plot([], [], 'ro', markersize=2, alpha=0.6, label='未命中 (Miss)')
            self.ax1.legend(loc='upper right')

            # Setup convergence plot specific for Integral
            self.ax2.set_title("积分估算值收敛过程")
            try:
                from scipy.integrate import quad
                true_integral, _ = quad(self.integral_func, self.integral_a, self.integral_b)
                self.line_true = self.ax2.axhline(true_integral, color='r', linestyle='--', label=f'真实积分 ≈ {true_integral:.6f}')
            except Exception as e:
                print(f"Could not calculate true integral: {e}")
                self.line_true = None # Cannot draw true value line
            self.ax2.legend()

        self.canvas.draw_idle()

    def run_simulation(self):
        """运行蒙特卡洛模拟"""
        sim_type = self.sim_type_var.get()
        
        # 如果是积分估算，先验证函数
        if sim_type == "估算积分":
            if not self.integral_func:
                # 尝试更新函数
                if not self.update_integral_function():
                    messagebox.showerror("错误", "请先定义一个有效的积分函数。")
                    return
            
            # 验证积分区间
            a = self.a_var.get()
            b = self.b_var.get()
            if a >= b:
                messagebox.showerror("错误", "积分下限必须小于上限。")
                return
            
            # 更新Y范围
            if hasattr(self, 'min_y_var') and hasattr(self, 'max_y_var'):
                self.integral_min_y = self.min_y_var.get()
                self.integral_max_y = self.max_y_var.get()
                if self.integral_min_y >= self.integral_max_y:
                    messagebox.showerror("错误", "Y范围的最小值必须小于最大值。")
                    return
        
        # 开始模拟
        self.simulation_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED) # Disable reset while running
        # Disable parameter changes while running
        for widget in self.param_frame.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Scale, ttk.Combobox)):
                widget.config(state=tk.DISABLED)
                
        # 安全地禁用类型选择下拉框
        try:
            # 遍历所有窗口控件查找类型下拉框
            for widget in self.master.winfo_children():
                if isinstance(widget, ttk.Frame) or isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) or isinstance(child, tk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Combobox):
                                    grandchild.config(state=tk.DISABLED)
        except Exception as e:
            print(f"无法禁用类型选择下拉框: {e}")
            # 这里仅打印错误但不中断模拟

        self.run_simulation_step()

    def stop_simulation(self):
        """Stop the simulation loop."""
        if not self.simulation_running:
            return
        self.simulation_running = False
        if self.simulation_task:
            self.master.after_cancel(self.simulation_task)
            self.simulation_task = None
        self.start_button.config(text="继续模拟", state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL) # Enable reset when stopped
        # Re-enable parameter changes
        for widget in self.param_frame.winfo_children():
             if isinstance(widget, (ttk.Entry, ttk.Scale, ttk.Combobox)):
                widget.config(state=tk.NORMAL)
                
        # 安全地启用类型选择下拉框
        try:
            # 遍历所有窗口控件查找类型下拉框
            for widget in self.master.winfo_children():
                if isinstance(widget, ttk.Frame) or isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) or isinstance(child, tk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Combobox):
                                    grandchild.config(state="readonly")
        except Exception as e:
            print(f"无法启用类型选择下拉框: {e}")
            # 这里仅打印错误但不中断模拟

    def reset_simulation(self):
        """Reset the simulation state and plots."""
        self.stop_simulation() # Ensure any running task is stopped
        self.total_points = 0
        self.points_inside = 0
        # self.sum_f_values = 0.0 # Removed
        self.points_x_inside.clear()
        self.points_y_inside.clear()
        self.points_x_outside.clear()
        self.points_y_outside.clear()
        # self.integral_points_x.clear() # Removed
        # self.integral_points_y.clear() # Removed
        self.iteration_history.clear() # Clear history
        self.estimate_history.clear()  # Clear history

        self.setup_plot() # Re-setup plots for the current type
        self.update_results()
        self.status_var.set("就绪 (已重置)")

    def run_simulation_step(self):
        """Perform one step (batch) of the simulation."""
        if not self.simulation_running:
            return

        start_time = time.perf_counter()
        sim_type = self.sim_type_var.get()
        points_in_batch = self.speed_var.get() # Use speed variable

        new_x_inside, new_y_inside = [], []
        new_x_outside, new_y_outside = [], []
        batch_points_inside = 0 # Points inside for this batch

        for _ in range(points_in_batch):
            self.total_points += 1

            if sim_type == "计算 π 值":
                x, y = random.random(), random.random()
                is_inside = (x*x + y*y <= 1.0)
                if is_inside:
                    self.points_inside += 1
                    batch_points_inside += 1
                    new_x_inside.append(x)
                    new_y_inside.append(y)
                else:
                    new_x_outside.append(x)
                    new_y_outside.append(y)

            elif sim_type == "估算积分":
                if not self.integral_func or self.integral_a >= self.integral_b or self.integral_min_y >= self.integral_max_y:
                    messagebox.showerror("错误", "积分参数无效，请检查函数、区间和Y范围。")
                    self.stop_simulation()
                    return

                # Sample within the bounding box
                x = random.uniform(self.integral_a, self.integral_b)
                y = random.uniform(self.integral_min_y, self.integral_max_y)

                try:
                    f_x = self.integral_func(x)
                except Exception as e:
                    print(f"Error evaluating function at x={x}: {e}")
                    self.stop_simulation()
                    messagebox.showerror("函数求值错误", f"在 x={x:.4f} 处计算函数值时出错: {e}")
                    return

                # Check if the point is a "hit" (between 0 and f(x) or f(x) and 0)
                # This handles both positive and negative functions relative to the bounding box
                is_inside = (self.integral_min_y <= y <= f_x) or (f_x <= y <= self.integral_max_y and f_x >= self.integral_min_y)
                # Simplified check assuming bounding box contains the relevant area:
                is_inside_area = (y >= self.integral_min_y and y <= f_x) if f_x >= self.integral_min_y else (y <= self.integral_max_y and y >= f_x)

                # More robust check for hit-or-miss (area under curve relative to baseline y=0)
                # A 'hit' means the random y falls between 0 and f(x)
                is_hit = (y >= 0 and y <= f_x) or (y <= 0 and y >= f_x)

                if is_hit:
                    self.points_inside += 1 # Count 'hits' for integral estimation
                    batch_points_inside += 1
                    new_x_inside.append(x)
                    new_y_inside.append(y)
                else:
                    new_x_outside.append(x)
                    new_y_outside.append(y)

        # --- Update Data Lists ---
        self.points_x_inside.extend(new_x_inside)
        self.points_y_inside.extend(new_y_inside)
        self.points_x_outside.extend(new_x_outside)
        self.points_y_outside.extend(new_y_outside)

        # --- Update Convergence History ---
        if self.total_points > 0:
            current_estimate = 0.0
            if sim_type == "计算 π 值":
                current_estimate = 4.0 * self.points_inside / self.total_points
            elif sim_type == "估算积分":
                box_area = (self.integral_b - self.integral_a) * (self.integral_max_y - self.integral_min_y)
                if box_area > 0: # Avoid division by zero
                     # Estimate is ratio of hits * bounding box area
                     current_estimate = box_area * (self.points_inside / self.total_points)

            # Add to history (only add every N points for performance if needed)
            if self.total_points % max(1, points_in_batch // 10) == 0 or self.total_points < 100: # Update history frequently at start
                 self.iteration_history.append(self.total_points)
                 self.estimate_history.append(current_estimate)

        # --- Update Plots ---
        # Limit plotted points for performance
        max_plot_points = 10000 # Increase max plotted points
        step = max(1, len(self.points_x_inside) // max_plot_points) if len(self.points_x_inside) > max_plot_points else 1
        step_out = max(1, len(self.points_x_outside) // max_plot_points) if len(self.points_x_outside) > max_plot_points else 1

        # Update ax1 (Main simulation)
        self.scatter_inside.set_data(self.points_x_inside[::step], self.points_y_inside[::step])
        self.scatter_outside.set_data(self.points_x_outside[::step_out], self.points_y_outside[::step_out])
        self.ax1.relim() # Recalculate limits if needed (though usually fixed)
        self.ax1.autoscale_view(tight=True) # Adjust view

        # Update ax2 (Convergence)
        if self.iteration_history:
            self.line_estimate.set_data(self.iteration_history, self.estimate_history)
            self.ax2.relim()
            self.ax2.autoscale_view(tight=False) # Allow some margin on convergence plot
            # Adjust Y limits dynamically for better view
            if len(self.estimate_history) > 1:
                min_est = min(self.estimate_history)
                max_est = max(self.estimate_history)
                padding = (max_est - min_est) * 0.1 + 1e-6 # Add small padding
                true_val = None
                if sim_type == "计算 π 值": true_val = math.pi
                elif sim_type == "估算积分" and self.line_true: true_val = self.line_true.get_ydata()[0]

                if true_val is not None:
                    min_lim = min(min_est, true_val) - padding
                    max_lim = max(max_est, true_val) + padding
                else:
                    min_lim = min_est - padding
                    max_lim = max_est + padding
                self.ax2.set_ylim(min_lim, max_lim)
            self.ax2.set_xlim(0, self.total_points * 1.05) # Adjust X limit

        self.canvas.draw_idle() # Use draw_idle for better responsiveness

        # --- Update Results Text ---
        self.update_results()

        # --- Update Status Bar ---
        self.status_var.set(f"模拟中... 点数: {self.total_points}")

        # --- Schedule next step ---
        time.perf_counter() - start_time
        # Simple delay - more sophisticated adaptive delay could be used
        delay_ms = 5 # Base delay in ms
        self.simulation_task = self.master.after(delay_ms, self.run_simulation_step)

    def update_results(self):
        """Update the text area with current simulation results."""
        self.result_text.delete(1.0, tk.END)
        sim_type = self.sim_type_var.get()
        result_str = f"模拟类型: {sim_type}\n"
        result_str += f"已模拟点数: {self.total_points}\n"
        result_str += "------------------------------------\n"

        if sim_type == "计算 π 值":
            if self.total_points > 0:
                pi_estimate = 4.0 * self.points_inside / self.total_points
                error = abs(pi_estimate - math.pi)
                result_str += f"内部点数 (Hits): {self.points_inside}\n"
                result_str += f"π 估算值: {pi_estimate:.8f}\n"
                result_str += f"真实 π 值: {math.pi:.8f}\n"
                result_str += f"绝对误差: {error:.8f}\n"
            else:
                result_str += "π 估算值: N/A\n"

        elif sim_type == "估算积分":
             result_str += f"函数 f(x): {self.func_str_var.get()}\n"
             result_str += f"积分区间: [{self.integral_a}, {self.integral_b}]\n"
             result_str += f"采样区域 Y: [{self.integral_min_y}, {self.integral_max_y}]\n"
             if self.total_points > 0:
                 box_area = (self.integral_b - self.integral_a) * (self.integral_max_y - self.integral_min_y)
                 if box_area > 1e-9: # Check if box area is valid
                     hit_ratio = self.points_inside / self.total_points
                     integral_estimate = box_area * hit_ratio
                     result_str += f"命中点数 (Hits): {self.points_inside}\n"
                     result_str += f"命中率: {hit_ratio:.4f}\n"
                     result_str += f"采样区域面积: {box_area:.6f}\n"
                     result_str += f"积分估算值 (Hit/Miss): {integral_estimate:.8f}\n"

                     # Add true value comparison if possible
                     try:
                         from scipy.integrate import quad
                         # Ensure integral_func is valid before calling quad
                         if self.integral_func:
                             true_integral, abserr = quad(self.integral_func, self.integral_a, self.integral_b)
                             error = abs(integral_estimate - true_integral)
                             result_str += f"真实积分值 (scipy.quad): {true_integral:.8f} (±{abserr:.2e})\n"
                             result_str += f"绝对误差: {error:.8f}\n"
                         else:
                             result_str += "真实积分值: (函数未设置)\n"
                     except ImportError:
                          result_str += "真实积分值: (需要安装 scipy 库)\n"
                     except Exception as e:
                         result_str += f"真实积分值: (计算错误 - {e})\n"
                 else:
                     result_str += "积分估算值: (采样区域面积无效)\n"
             else:
                 result_str += "积分估算值: N/A\n"

        self.result_text.insert(tk.END, result_str)

    def auto_estimate_y_range(self):
        """Attempt to automatically estimate min/max Y for the function in the interval [a, b]."""
        if not self.integral_func:
            messagebox.showerror("错误", "请先确保函数已正确设置。")
            return
        try:
            a = self.a_var.get()
            b = self.b_var.get()
            if a >= b:
                messagebox.showerror("错误", "积分下限 a 必须小于上限 b。")
                return

            x_samples = np.linspace(a, b, 500) # Sample 500 points
            y_samples = [self.integral_func(x) for x in x_samples]

            min_y_est = min(y_samples)
            max_y_est = max(y_samples)

            # Add some padding
            padding = (max_y_est - min_y_est) * 0.15
            self.min_y_var.set(round(min_y_est - padding, 4))
            self.max_y_var.set(round(max_y_est + padding, 4))
            messagebox.showinfo("自动估算完成", f"估算的 Y 范围设置为 [{self.min_y_var.get()}, {self.max_y_var.get()}]。\n请检查并根据需要调整。")

        except Exception as e:
            messagebox.showerror("自动估算错误", f"估算 Y 范围时出错: {e}")

    def show_theory(self):
        """显示蒙特卡洛模拟理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 蒙特卡洛模拟知识点内容
            sections = {
                "基本概念": """
定义：
蒙特卡洛模拟通过随机抽样的方法来模拟复杂系统的行为或过程，以获得问题的近似解。它利用大量的随机数来模拟各种不确定因素，然后根据这些随机样本计算出所关注的统计量或结果。

原理：
基于大数定律，即当样本数量足够大时，样本的统计特征会趋近于总体的真实特征。通过生成大量的随机样本，模拟系统的各种可能情况，进而估计出系统的期望结果、概率分布等重要信息。

关键要素：
1.随机数生成：
是蒙特卡洛模拟的基础，需要生成符合特定概率分布的随机数序列。例如，均匀分布随机数常用于模拟等概率事件，而正态分布随机数则适用于描述具有中心趋势和一定波动的现象。
2.模型构建：
根据实际问题建立相应的数学模型或模拟模型，明确输入变量、输出变量以及它们之间的关系。例如，在投资组合模拟中，需要确定各种资产的收益率分布、相关性以及投资组合的目标函数等。
3.模拟次数：
模拟次数决定了结果的准确性和可靠性。一般来说，模拟次数越多，结果越接近真实值，但计算成本也会相应增加。
""",
                "应用": """
金融领域：
1.风险评估：
用于评估投资组合的风险，通过模拟各种资产价格的随机波动，计算投资组合在不同情景下的价值变化，进而得到风险指标，如在险价值（VaR）和预期损失（ES）等。
2.期权定价：
模拟标的资产价格的路径，根据期权的行权条件计算期权在不同路径下的收益，然后通过对大量路径的平均得到期权的理论价格。

工程领域：
1.可靠性分析：
对复杂系统的可靠性进行评估，模拟系统中各个组件的失效概率和失效模式，以确定整个系统在一定时间内的可靠度。
2.优化设计：
在工程设计中，通过蒙特卡洛模拟生成大量的设计方案样本，然后根据目标函数和约束条件筛选出最优或较优的设计方案。

科学研究：
1.物理模拟：
在原子核物理、统计物理等领域，用于模拟粒子的运动、相互作用以及物质的微观结构等。例如，通过蒙特卡洛模拟研究材料的相变过程、分子的扩散现象等。
2.生物医学：
在生物医学研究中，用于模拟生物分子的结构和动力学、药物分子与生物靶点的相互作用以及疾病传播模型等，为药物研发和疾病防控提供理论支持。

其他领域：
1.交通规划：
模拟交通流量的变化，评估不同交通规划方案的可行性和效果，为城市交通基础设施的建设和管理提供决策依据。
2.市场营销：
模拟消费者的购买行为和市场需求的变化，帮助企业制定营销策略、优化产品设计和预测市场份额等。
"""
        
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "蒙特卡洛模拟理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建蒙特卡洛模拟理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("蒙特卡洛模拟理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="蒙特卡洛模拟理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)    

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = MonteCarloApp(root)
    root.mainloop()
