import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
import random
import time
import threading

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MiddleSchoolMonteCarloSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("蒙特卡洛方法计算圆周率")
        self.root.geometry("1000x650")
        
        # 定义颜色
        self.bg_dark_blue = "#1A3665"    # 深蓝色背景
        self.bg_navy = "#223C6A"         # 海军蓝用于控件
        self.accent_green = "#2ECC71"    # 绿色强调色
        self.text_white = "#FFFFFF"      # 白色文本
        self.text_light = "#D0D0D0"      # 浅灰色文本
        
        # 设置背景颜色
        self.root.config(bg=self.bg_dark_blue)
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg=self.bg_dark_blue)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_frame = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="蒙特卡洛方法计算圆周率",
            font=("SimHei", 24, "bold"),
            bg=self.bg_dark_blue,
            fg=self.text_white
        )
        title_label.pack(side=tk.LEFT)
        
        # 创建左侧控制面板
        self.left_panel = tk.Frame(self.main_frame, bg=self.bg_navy, width=280)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=0)
        self.left_panel.pack_propagate(False)
        
        # 创建右侧可视化区域
        self.right_panel = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置控制面板
        self.setup_control_panel()
        
        # 设置可视化区域
        self.setup_visualization()
        
        # 初始化模拟变量
        self.simulation_running = False
        self.simulation_thread = None
        self.total_points = 0
        self.points_inside = 0
        self.inside_x = []
        self.inside_y = []
        self.outside_x = []
        self.outside_y = []
        self.pi_estimates = []
        self.iteration_counts = []
    
    def setup_control_panel(self):
        """设置左侧控制面板"""
        # 添加面板标题
        panel_title = tk.Label(
            self.left_panel,
            text="模拟设置",
            font=("SimHei", 16, "bold"),
            bg=self.bg_navy,
            fg=self.text_white,
            pady=10
        )
        panel_title.pack(fill=tk.X)
        
        # 添加分隔线
        separator = tk.Frame(self.left_panel, height=2, bg=self.accent_green)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # 每次添加点数
        points_frame = tk.Frame(self.left_panel, bg=self.bg_navy)
        points_frame.pack(fill=tk.X, padx=15, pady=10)
        
        points_label = tk.Label(
            points_frame,
            text="每次添加点数:",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white
        )
        points_label.pack(anchor=tk.W)
        
        self.points_per_update = tk.IntVar(value=100)
        points_scale = ttk.Scale(
            points_frame,
            from_=10,
            to=1000,
            variable=self.points_per_update,
            orient=tk.HORIZONTAL
        )
        points_scale.pack(fill=tk.X, pady=5)
        
        points_value = tk.Label(
            points_frame,
            textvariable=self.points_per_update,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white
        )
        points_value.pack(anchor=tk.E)
        
        # 模拟速度
        speed_frame = tk.Frame(self.left_panel, bg=self.bg_navy)
        speed_frame.pack(fill=tk.X, padx=15, pady=10)
        
        speed_label = tk.Label(
            speed_frame,
            text="模拟速度:",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white
        )
        speed_label.pack(anchor=tk.W)
        
        self.simulation_speed = tk.IntVar(value=50)
        speed_scale = ttk.Scale(
            speed_frame,
            from_=10,
            to=100,
            variable=self.simulation_speed,
            orient=tk.HORIZONTAL
        )
        speed_scale.pack(fill=tk.X, pady=5)
        
        speed_label_frame = tk.Frame(speed_frame, bg=self.bg_navy)
        speed_label_frame.pack(fill=tk.X)
        
        slow_label = tk.Label(
            speed_label_frame,
            text="慢",
            font=("SimHei", 10),
            bg=self.bg_navy,
            fg=self.text_white
        )
        slow_label.pack(side=tk.LEFT)
        
        fast_label = tk.Label(
            speed_label_frame,
            text="快",
            font=("SimHei", 10),
            bg=self.bg_navy,
            fg=self.text_white
        )
        fast_label.pack(side=tk.RIGHT)
        
        # 按钮框架
        button_frame = tk.Frame(self.left_panel, bg=self.bg_navy)
        button_frame.pack(fill=tk.X, padx=15, pady=20)
        
        # 开始按钮
        self.start_button = tk.Button(
            button_frame,
            text="开始模拟",
            command=self.toggle_simulation,
            bg=self.accent_green,
            fg=self.text_white,
            font=("SimHei", 12),
            padx=15,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 重置按钮
        reset_button = tk.Button(
            button_frame,
            text="重置",
            command=self.reset_simulation,
            bg=self.accent_green,
            fg=self.text_white,
            font=("SimHei", 12),
            padx=15,
            pady=5
        )
        reset_button.pack(side=tk.LEFT)
        
        # 解释框架
        explanation_frame = tk.LabelFrame(
            self.left_panel,
            text="模拟说明",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        explanation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        explanation_text = """
蒙特卡洛方法是一种利用随机数来解决问题的方法。

在这个模拟中，我们随机在正方形中生成点，然后计算落在内切圆内的点的比例。

由于圆的面积为 πr²，正方形的面积为 (2r)²，所以：
π ≈ 4 × (圆内点数 / 总点数)

点数越多，估计越准确！
        """
        
        explanation_label = tk.Label(
            explanation_frame,
            text=explanation_text,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white,
            justify=tk.LEFT,
            wraplength=250
        )
        explanation_label.pack(fill=tk.BOTH, expand=True)
        
        # 结果框架
        self.results_frame = tk.LabelFrame(
            self.left_panel,
            text="模拟结果",
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_white,
            padx=10,
            pady=10
        )
        self.results_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 当前估计值
        self.pi_estimate_var = tk.StringVar(value="π ≈ 等待模拟...")
        pi_estimate_label = tk.Label(
            self.results_frame,
            textvariable=self.pi_estimate_var,
            font=("SimHei", 14),
            bg=self.bg_navy,
            fg=self.accent_green,
            pady=5
        )
        pi_estimate_label.pack(fill=tk.X)
        
        # 真实值
        true_pi_label = tk.Label(
            self.results_frame,
            text=f"真实值: π = 3.14159...",
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white
        )
        true_pi_label.pack(fill=tk.X)
        
        # 总点数
        self.total_points_var = tk.StringVar(value="总点数: 0")
        total_points_label = tk.Label(
            self.results_frame,
            textvariable=self.total_points_var,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white
        )
        total_points_label.pack(fill=tk.X)
        
        # 圆内点数
        self.inside_points_var = tk.StringVar(value="圆内点数: 0")
        inside_points_label = tk.Label(
            self.results_frame,
            textvariable=self.inside_points_var,
            font=("SimHei", 11),
            bg=self.bg_navy,
            fg=self.text_white
        )
        inside_points_label.pack(fill=tk.X)
    
    def setup_visualization(self):
        """设置可视化区域"""
        # 创建上下分割的框架
        top_frame = tk.Frame(self.right_panel, bg=self.bg_dark_blue)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        bottom_frame = tk.Frame(self.right_panel, bg=self.bg_dark_blue)
        bottom_frame.pack(fill=tk.X, expand=False)
        
        # 创建左右分割的框架（用于散点图和折线图）
        scatter_frame = tk.Frame(top_frame, bg=self.bg_dark_blue)
        scatter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        line_frame = tk.Frame(top_frame, bg=self.bg_dark_blue)
        line_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建散点图 (Monte Carlo 模拟)
        self.scatter_fig, self.scatter_ax = plt.subplots(figsize=(4, 4))
        self.scatter_fig.patch.set_facecolor(self.bg_dark_blue)
        self.scatter_ax.set_facecolor(self.bg_dark_blue)
        
        # 设置散点图标题和标签
        self.scatter_ax.set_title("蒙特卡洛模拟", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.scatter_ax.set_xlabel("X", color=self.text_white, fontsize=12)
        self.scatter_ax.set_ylabel("Y", color=self.text_white, fontsize=12)
        
        # 设置散点图范围
        self.scatter_ax.set_xlim(0, 1)
        self.scatter_ax.set_ylim(0, 1)
        
        # 设置刻度标签颜色
        self.scatter_ax.tick_params(axis='x', colors=self.text_white)
        self.scatter_ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.scatter_ax.spines.values():
            spine.set_color(self.text_white)
        
        # 画一个正方形和内切圆
        circle = plt.Circle((0.5, 0.5), 0.5, fill=False, color=self.text_white, linestyle='--')
        self.scatter_ax.add_artist(circle)
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', edgecolor='green', label='圆内'),
            Patch(facecolor='red', edgecolor='red', label='圆外')
        ]
        self.scatter_ax.legend(handles=legend_elements, loc='upper right', facecolor=self.bg_navy, edgecolor=self.bg_navy, labelcolor=self.text_white)
        
        # 创建散点图画布
        self.scatter_canvas = FigureCanvasTkAgg(self.scatter_fig, master=scatter_frame)
        self.scatter_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 创建折线图 (π 估计值)
        self.line_fig, self.line_ax = plt.subplots(figsize=(4, 4))
        self.line_fig.patch.set_facecolor(self.bg_dark_blue)
        self.line_ax.set_facecolor(self.bg_dark_blue)
        
        # 设置折线图标题和标签
        self.line_ax.set_title("π 估计值", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.line_ax.set_xlabel("模拟点数", color=self.text_white, fontsize=12)
        self.line_ax.set_ylabel("π 估计值", color=self.text_white, fontsize=12)
        
        # 设置 y 轴范围
        self.line_ax.set_ylim(2.5, 3.5)
        
        # 设置刻度标签颜色
        self.line_ax.tick_params(axis='x', colors=self.text_white)
        self.line_ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.line_ax.spines.values():
            spine.set_color(self.text_white)
        
        # 绘制真实值线
        self.line_ax.axhline(y=np.pi, color='red', linestyle='--', label=f'真实值 π ≈ {np.pi:.6f}')
        
        # 添加图例
        self.line_ax.legend(loc='upper right', facecolor=self.bg_navy, edgecolor=self.bg_navy, labelcolor=self.text_white)
        
        # 创建折线图画布
        self.line_canvas = FigureCanvasTkAgg(self.line_fig, master=line_frame)
        self.line_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 设置图形大小调整事件
        self.scatter_fig.tight_layout(pad=2.0)
        self.line_fig.tight_layout(pad=2.0)
        self.scatter_canvas.draw()
        self.line_canvas.draw()
    
    def toggle_simulation(self):
        """开始/停止模拟"""
        if self.simulation_running:
            # 停止模拟
            self.simulation_running = False
            self.start_button.config(text="开始模拟", bg=self.accent_green)
        else:
            # 开始模拟
            self.simulation_running = True
            self.start_button.config(text="停止模拟", bg="#E74C3C")  # 红色
            
            # 创建新线程运行模拟
            if self.simulation_thread is None or not self.simulation_thread.is_alive():
                self.simulation_thread = threading.Thread(target=self.run_simulation)
                self.simulation_thread.daemon = True
                self.simulation_thread.start()
    
    def run_simulation(self):
        """运行蒙特卡洛模拟"""
        while self.simulation_running:
            # 获取每次更新的点数和速度
            points_per_update = self.points_per_update.get()
            speed = self.simulation_speed.get()
            
            # 计算延迟时间（速度越大，延迟越小）
            delay = (110 - speed) / 100.0  # 从 0.1 到 1.0 秒
            
            # 生成新的随机点
            new_points_x = [random.random() for _ in range(points_per_update)]
            new_points_y = [random.random() for _ in range(points_per_update)]
            
            # 判断点是否在圆内
            for i in range(points_per_update):
                x, y = new_points_x[i], new_points_y[i]
                self.total_points += 1
                
                # 检查点是否在圆内 (以 (0.5, 0.5) 为圆心的半径为 0.5 的圆)
                if (x - 0.5)**2 + (y - 0.5)**2 <= 0.5**2:
                    self.inside_x.append(x)
                    self.inside_y.append(y)
                    self.points_inside += 1
                else:
                    self.outside_x.append(x)
                    self.outside_y.append(y)
            
            # 计算 π 估计值
            pi_estimate = 4 * self.points_inside / self.total_points
            self.pi_estimates.append(pi_estimate)
            self.iteration_counts.append(self.total_points)
            
            # 更新图形
            self.update_plots()
            
            # 更新结果显示
            self.update_results(pi_estimate)
            
            # 延迟
            time.sleep(delay)
    
    def update_plots(self):
        """更新散点图和折线图"""
        # 清除当前散点图
        self.scatter_ax.clear()
        
        # 设置散点图标题和标签
        self.scatter_ax.set_title("蒙特卡洛模拟", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.scatter_ax.set_xlabel("X", color=self.text_white, fontsize=12)
        self.scatter_ax.set_ylabel("Y", color=self.text_white, fontsize=12)
        
        # 设置散点图范围
        self.scatter_ax.set_xlim(0, 1)
        self.scatter_ax.set_ylim(0, 1)
        
        # 设置刻度标签颜色
        self.scatter_ax.tick_params(axis='x', colors=self.text_white)
        self.scatter_ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.scatter_ax.spines.values():
            spine.set_color(self.text_white)
        
        # 画一个正方形和内切圆
        circle = plt.Circle((0.5, 0.5), 0.5, fill=False, color=self.text_white, linestyle='--')
        self.scatter_ax.add_artist(circle)
        
        # 绘制散点
        if self.inside_x:
            self.scatter_ax.scatter(self.inside_x, self.inside_y, color='green', s=5, alpha=0.7, label='圆内')
        if self.outside_x:
            self.scatter_ax.scatter(self.outside_x, self.outside_y, color='red', s=5, alpha=0.7, label='圆外')
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', edgecolor='green', label='圆内'),
            Patch(facecolor='red', edgecolor='red', label='圆外')
        ]
        self.scatter_ax.legend(handles=legend_elements, loc='upper right', facecolor=self.bg_navy, edgecolor=self.bg_navy, labelcolor=self.text_white)
        
        # 清除当前折线图
        self.line_ax.clear()
        
        # 设置折线图标题和标签
        self.line_ax.set_title("π 估计值", color=self.text_white, fontsize=14, fontfamily='SimHei')
        self.line_ax.set_xlabel("模拟点数", color=self.text_white, fontsize=12)
        self.line_ax.set_ylabel("π 估计值", color=self.text_white, fontsize=12)
        
        # 设置 y 轴范围 - 动态调整
        min_estimate = min(self.pi_estimates) if self.pi_estimates else 2.5
        max_estimate = max(self.pi_estimates) if self.pi_estimates else 3.5
        y_min = max(2.5, min_estimate - 0.2)
        y_max = min(3.5, max_estimate + 0.2)
        self.line_ax.set_ylim(y_min, y_max)
        
        # 设置刻度标签颜色
        self.line_ax.tick_params(axis='x', colors=self.text_white)
        self.line_ax.tick_params(axis='y', colors=self.text_white)
        
        # 设置图形边框颜色
        for spine in self.line_ax.spines.values():
            spine.set_color(self.text_white)
        
        # 绘制真实值线
        self.line_ax.axhline(y=np.pi, color='red', linestyle='--', label=f'真实值 π ≈ {np.pi:.6f}')
        
        # 绘制估计值折线
        if self.pi_estimates:
            self.line_ax.plot(self.iteration_counts, self.pi_estimates, color='blue', marker='', linestyle='-', label='估计值')
        
        # 添加图例
        self.line_ax.legend(loc='upper right', facecolor=self.bg_navy, edgecolor=self.bg_navy, labelcolor=self.text_white)
        
        # 更新画布
        self.scatter_fig.tight_layout(pad=2.0)
        self.line_fig.tight_layout(pad=2.0)
        self.scatter_canvas.draw()
        self.line_canvas.draw()
    
    def update_results(self, pi_estimate):
        """更新结果显示"""
        self.pi_estimate_var.set(f"π ≈ {pi_estimate:.8f}")
        self.total_points_var.set(f"总点数: {self.total_points}")
        self.inside_points_var.set(f"圆内点数: {self.points_inside}")
    
    def reset_simulation(self):
        """重置模拟"""
        # 停止模拟
        self.simulation_running = False
        self.start_button.config(text="开始模拟", bg=self.accent_green)
        
        # 重置变量
        self.total_points = 0
        self.points_inside = 0
        self.inside_x = []
        self.inside_y = []
        self.outside_x = []
        self.outside_y = []
        self.pi_estimates = []
        self.iteration_counts = []
        
        # 重置结果显示
        self.pi_estimate_var.set("π ≈ 等待模拟...")
        self.total_points_var.set("总点数: 0")
        self.inside_points_var.set("圆内点数: 0")
        
        # 更新图形
        self.update_plots()

if __name__ == "__main__":
    root = tk.Tk()
    app = MiddleSchoolMonteCarloSimulation(root)
    root.mainloop() 