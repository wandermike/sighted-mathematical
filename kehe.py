import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import warnings
import traceback
import math
from knowledge import KnowledgeLearningClass

# 配置 Matplotlib 以支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

# 忽略特定警告
warnings.filterwarnings("ignore", category=UserWarning, module='sympy')
warnings.filterwarnings("ignore", category=RuntimeWarning)

class KeheApp:
    def __init__(self, root):
        self.root = root
        self.root.title("科赫雪花分形可视化")
        self.root.geometry("1200x800")
        self.knowledge_learner = KnowledgeLearningClass()
        
        # 初始化变量
        self.equation_colors = ["#1E88E5", "#E53935", "#43A047", "#FDD835", "#5E35B1", "#00ACC1", "#FF6D00"]
        self.current_color_index = 0
        self.x_range = tk.StringVar(value="-1.5,1.5")
        self.y_range = tk.StringVar(value="-1.5,1.5")
        self.iteration_depth = tk.IntVar(value=3)  # 科赫雪花迭代深度
        self.show_grid = tk.BooleanVar(value=True)
        self.line_width = tk.DoubleVar(value=1.5)
        self.status_var = tk.StringVar(value="就绪")
        
        # 创建UI
        self.create_ui()
        
        # 绑定事件
        self.bind_events()
        
        # 初始绘制
        self.plot_koch_snowflake()
        
        self.knowledge_learner = KnowledgeLearningClass()
        
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 迭代深度设置
        depth_frame = ttk.Frame(control_frame)
        depth_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(depth_frame, text="迭代深度:").pack(side=tk.LEFT)
        depth_scale = ttk.Scale(depth_frame, from_=0, to=6, variable=self.iteration_depth, 
                               orient=tk.HORIZONTAL, length=150)
        depth_scale.pack(side=tk.LEFT, padx=5)
        depth_label = ttk.Label(depth_frame, text="3")
        depth_label.pack(side=tk.LEFT)
        
        # 观察depth变化
        def update_depth_label(*args):
            depth_label.config(text=str(self.iteration_depth.get()))
        
        self.iteration_depth.trace_add("write", update_depth_label)
        
        # 绘制按钮
        draw_button = ttk.Button(control_frame, text="绘制科赫雪花", command=self.plot_koch_snowflake)
        draw_button.pack(fill=tk.X, pady=5)
        
        # 坐标范围设置
        range_frame = ttk.LabelFrame(control_frame, text="坐标范围", padding=5)
        range_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(range_frame, text="X范围 (min,max):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(range_frame, textvariable=self.x_range, width=15).grid(row=0, column=1, pady=2)
        
        ttk.Label(range_frame, text="Y范围 (min,max):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(range_frame, textvariable=self.y_range, width=15).grid(row=1, column=1, pady=2)
        
        # 线宽设置
        width_frame = ttk.Frame(control_frame)
        width_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(width_frame, text="线宽:").pack(side=tk.LEFT)
        ttk.Scale(width_frame, from_=0.5, to=4.0, variable=self.line_width, 
                 orient=tk.HORIZONTAL, length=150).pack(side=tk.LEFT, expand=True)
        
        # 网格选项
        grid_check = ttk.Checkbutton(control_frame, text="显示网格", variable=self.show_grid, 
                                    command=self.update_plot_settings)
        grid_check.pack(anchor=tk.W, pady=5)
        
        # 颜色选择按钮
        color_button = ttk.Button(control_frame, text="选择颜色", command=self.choose_color)
        color_button.pack(fill=tk.X, pady=5)
        
        # 重置视图按钮
        reset_button = ttk.Button(control_frame, text="重置视图", command=self.reset_view)
        reset_button.pack(fill=tk.X, pady=5)
        
        # 保存图像按钮
        save_button = ttk.Button(control_frame, text="保存图像", command=self.save_figure)
        save_button.pack(fill=tk.X, pady=5)

        knowledge_learning = ttk.Button(control_frame, text="知识介绍", command=self.knowledge_learner.knowledge_learning_8_function)
        knowledge_learning.pack(fill=tk.X,pady=5)
        
        # 信息面板
        info_frame = ttk.LabelFrame(control_frame, text="科赫雪花信息", padding=5)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=30, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert(tk.END, """科赫雪花是一种经典的分形，由三条科赫曲线组成。

每个科赫曲线通过递归方式生成：
1. 从一条直线开始
2. 将直线分成三等份
3. 用两条线段替换中间部分，形成一个向外的等边三角形
4. 对每条新线段重复此过程

科赫雪花具有无限的周长但有限的面积，展示了分形几何的奇妙特性。

使用滑块调整迭代深度，观察复杂度的变化。""")
        self.info_text.config(state=tk.DISABLED)
        
        # 创建右侧绘图区域
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建绘图画布
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加matplotlib工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        
        # 状态栏
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 设置初始绘图
        self.setup_plot()
    
    def setup_plot(self):
        """初始化绘图设置"""
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X', fontsize=10)
        self.ax.set_ylabel('Y', fontsize=10)
        self.ax.set_title('科赫雪花分形', fontsize=12)
        self.ax.grid(self.show_grid.get())
        
        # 设置坐标轴范围
        try:
            x_min, x_max = map(float, self.x_range.get().split(','))
            y_min, y_max = map(float, self.y_range.get().split(','))
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
        except:
            self.ax.set_xlim(-1.5, 1.5)
            self.ax.set_ylim(-1.5, 1.5)
    
    def bind_events(self):
        """绑定事件处理函数"""
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.root.bind('<Key>', self.on_key_press)
    
    def koch_curve(self, p1, p2, depth):
        """生成科赫曲线的点"""
        if depth == 0:
            return [p1, p2]
        
        # 计算三等分点
        x1, y1 = p1
        x2, y2 = p2
        
        # 计算向量和长度
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        
        # 三等分点
        p1_1 = (x1 + dx/3, y1 + dy/3)
        p2_1 = (x1 + 2*dx/3, y1 + 2*dy/3)
        
        # 计算向外的顶点（旋转60度）
        angle = math.atan2(dy, dx) + math.pi/3  # 旋转60度
        length = dist/3
        px = x1 + dx/3 + length * math.cos(angle)
        py = y1 + dy/3 + length * math.sin(angle)
        p_mid = (px, py)
        
        # 递归计算每个子段
        points = []
        points.extend(self.koch_curve(p1, p1_1, depth-1)[:-1])  # 排除重复点
        points.extend(self.koch_curve(p1_1, p_mid, depth-1)[:-1])
        points.extend(self.koch_curve(p_mid, p2_1, depth-1)[:-1])
        points.extend(self.koch_curve(p2_1, p2, depth-1))
        
        return points
    
    def plot_koch_snowflake(self):
        """绘制科赫雪花"""
        self.ax.clear()
        self.setup_plot()
        
        try:
            depth = self.iteration_depth.get()
            
            # 创建初始的等边三角形
            side_length = 2.0
            height = side_length * math.sqrt(3) / 2
            
            # 三角形的三个顶点
            p1 = (-side_length/2, -height/3)
            p2 = (side_length/2, -height/3)
            p3 = (0, 2*height/3)
            
            # 计算三条科赫曲线
            curve1 = self.koch_curve(p1, p2, depth)
            curve2 = self.koch_curve(p2, p3, depth)
            curve3 = self.koch_curve(p3, p1, depth)
            
            # 提取坐标点
            x1, y1 = zip(*curve1)
            x2, y2 = zip(*curve2)
            x3, y3 = zip(*curve3)
            
            # 绘制科赫曲线
            color = self.equation_colors[self.current_color_index % len(self.equation_colors)]
            line_width = self.line_width.get()
            
            self.ax.plot(x1, y1, color=color, linewidth=line_width)
            self.ax.plot(x2, y2, color=color, linewidth=line_width)
            self.ax.plot(x3, y3, color=color, linewidth=line_width)
            
            # 更新画布
            self.canvas.draw()
            
            # 更新状态
            self.status_var.set(f"已绘制科赫雪花 (迭代深度: {depth})")
            
            # 更新信息面板
            total_segments = 3 * (4 ** depth)
            self.update_info(f"""科赫雪花 (迭代深度: {depth})

特性:
- 总线段数: {total_segments}
- 维度: 约 1.26
- 绘制颜色: {color}
- 线宽: {line_width}

科赫雪花是一种经典的分形，由三条科赫曲线组成。每增加一个迭代深度，线段数量会增加4倍。

科赫雪花具有有限的面积但无限的周长，这是分形几何的典型特征。
""")
            
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制科赫雪花时出错: {str(e)}")
            traceback.print_exc()
            self.status_var.set("绘图失败")
    
    def choose_color(self):
        """选择自定义颜色"""
        from tkinter import colorchooser
        
        color = colorchooser.askcolor(title="选择颜色")
        if color[1]:  # 如果用户选择了颜色
            self.equation_colors[self.current_color_index % len(self.equation_colors)] = color[1]
            self.plot_koch_snowflake()
    
    def update_plot_settings(self):
        """更新绘图设置"""
        self.ax.grid(self.show_grid.get())
        self.canvas.draw()
    
    def reset_view(self):
        """重置视图到指定范围"""
        try:
            x_min, x_max = map(float, self.x_range.get().split(','))
            y_min, y_max = map(float, self.y_range.get().split(','))
            
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.canvas.draw()
            
            self.status_var.set("已重置视图")
        except Exception as e:
            messagebox.showerror("视图错误", f"重置视图时出错: {str(e)}")
            traceback.print_exc()
    
    def save_figure(self):
        """保存图像到文件"""
        from tkinter import filedialog
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG图像", "*.png"), ("JPEG图像", "*.jpg"), ("PDF文档", "*.pdf"), ("SVG图像", "*.svg")]
            )
            
            if file_path:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("保存成功", f"图像已保存到: {file_path}")
                self.status_var.set(f"图像已保存到: {file_path}")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存图像时出错: {str(e)}")
            traceback.print_exc()
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件，显示坐标"""
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self.status_var.set(f"坐标: ({x:.2f}, {y:.2f})")
        else:
            self.status_var.set("就绪")
    
    def on_key_press(self, event):
        """处理键盘按键事件"""
        if event.keysym == 'r':
            self.reset_view()  # 按 'r' 键重置视图
        elif event.keysym == 's':
            self.save_figure()  # 按 's' 键保存图像
        elif event.keysym == 'g':
            self.show_grid.set(not self.show_grid.get())  # 按 'g' 键切换网格显示
            self.update_plot_settings()
        elif event.keysym == 'plus' or event.keysym == 'equal':
            # 增加迭代深度
            current = self.iteration_depth.get()
            if current < 6:
                self.iteration_depth.set(current + 1)
                self.plot_koch_snowflake()
        elif event.keysym == 'minus':
            # 减少迭代深度
            current = self.iteration_depth.get()
            if current > 0:
                self.iteration_depth.set(current - 1)
                self.plot_koch_snowflake()
    
    def update_info(self, text):
        """更新信息文本框的内容"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)

# 如果直接运行此文件，则创建窗口并启动应用
if __name__ == "__main__":
    root = tk.Tk()
    app = KeheApp(root)
    root.mainloop()
