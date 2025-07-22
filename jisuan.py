import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# 设置中文字体及防止负号显示异常
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 自定义 3D 箭头类
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        try:
            xs3d, ys3d, zs3d = self._verts3d
            if self.axes is None:
                return
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)
        except Exception as e:
            print(f"Arrow3D draw error: {str(e)}")

    def do_3d_projection(self, renderer=None):
        try:
            xs3d, ys3d, zs3d = self._verts3d
            if self.axes is None:
                return np.inf
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            return np.min(zs)
        except Exception as e:
            print(f"Arrow3D projection error: {str(e)}")
            return np.inf

class VectorOperationsApp:
    def __init__(self, master):
        self.master = master
        self.master.title("3D向量运算可视化")
        
        # 设置窗口样式
        style = ttk.Style()
        style.configure('TLabel', background='#E6F3FF')
        style.configure('TCombobox', background='#E6F3FF')
        
        # 创建左侧控制面板
        self.control_frame = tk.Frame(master, bg='#E6F3FF', width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题和返回按钮放在同一行
        title_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        title_frame.pack(fill=tk.X, pady=10)
        
        # 返回按钮放在左侧
        self.return_button = tk.Button(
            title_frame,
            text="返回",
            command=self.master.destroy,  # 只关闭当前窗口，不启动新窗口
            bg="#E74C3C",
            fg="white",
            font=('SimHei', 10),
            width=6,
            relief=tk.RAISED,
            bd=2
        )
        self.return_button.pack(side=tk.LEFT, padx=5)
        
        # 标题放在右侧
        title_label = tk.Label(
            title_frame,
            text="3D向量运算可视化",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(side=tk.RIGHT, padx=5)
        
        # 运算类型选择
        operation_frame = tk.LabelFrame(
            self.control_frame,
            text="运算类型",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        operation_frame.pack(fill=tk.X, pady=10)
        
        self.operation_var = tk.StringVar()
        operations = ["向量加法", "向量减法", "标量乘法"]
        self.operation_combobox = ttk.Combobox(
            operation_frame,
            textvariable=self.operation_var,
            values=operations,
            state='readonly',
            font=('SimHei', 10)
        )
        self.operation_combobox.pack(padx=10, pady=5)
        self.operation_combobox.current(0)
        self.operation_combobox.bind('<<ComboboxSelected>>', self.on_operation_change)
        
        # 向量输入区域
        input_frame = tk.LabelFrame(
            self.control_frame,
            text="向量输入",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        input_frame.pack(fill=tk.X, pady=10)
        
        # 向量 a 输入
        vector_a_frame = tk.LabelFrame(
            input_frame,
            text="向量 a",
            bg='#E6F3FF',
            font=('SimHei', 10)
        )
        vector_a_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建向量 a 的输入框
        a_entries_frame = tk.Frame(vector_a_frame, bg='#E6F3FF')
        a_entries_frame.pack(pady=5)
        
        tk.Label(a_entries_frame, text="x:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.a_x = tk.Entry(a_entries_frame, width=8)
        self.a_x.pack(side=tk.LEFT, padx=2)
        self.a_x.insert(0, "1")
        
        tk.Label(a_entries_frame, text="y:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.a_y = tk.Entry(a_entries_frame, width=8)
        self.a_y.pack(side=tk.LEFT, padx=2)
        self.a_y.insert(0, "0")
        
        tk.Label(a_entries_frame, text="z:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.a_z = tk.Entry(a_entries_frame, width=8)
        self.a_z.pack(side=tk.LEFT, padx=2)
        self.a_z.insert(0, "0")
        
        # 向量 b 输入
        vector_b_frame = tk.LabelFrame(
            input_frame,
            text="向量 b",
            bg='#E6F3FF',
            font=('SimHei', 10)
        )
        vector_b_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建向量 b 的输入框
        b_entries_frame = tk.Frame(vector_b_frame, bg='#E6F3FF')
        b_entries_frame.pack(pady=5)
        
        tk.Label(b_entries_frame, text="x:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.b_x = tk.Entry(b_entries_frame, width=8)
        self.b_x.pack(side=tk.LEFT, padx=2)
        self.b_x.insert(0, "0")
        
        tk.Label(b_entries_frame, text="y:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.b_y = tk.Entry(b_entries_frame, width=8)
        self.b_y.pack(side=tk.LEFT, padx=2)
        self.b_y.insert(0, "1")
        
        tk.Label(b_entries_frame, text="z:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.b_z = tk.Entry(b_entries_frame, width=8)
        self.b_z.pack(side=tk.LEFT, padx=2)
        self.b_z.insert(0, "0")
        
        # 标量 k 输入框（初始隐藏）
        self.scalar_frame = tk.LabelFrame(
            input_frame,
            text="标量 k",
            bg='#E6F3FF',
            font=('SimHei', 10)
        )
        
        k_frame = tk.Frame(self.scalar_frame, bg='#E6F3FF')
        k_frame.pack(pady=5)
        
        tk.Label(k_frame, text="k:", bg='#E6F3FF').pack(side=tk.LEFT, padx=2)
        self.scalar_k = tk.Entry(k_frame, width=8)
        self.scalar_k.pack(side=tk.LEFT, padx=2)
        self.scalar_k.insert(0, "2")
        
        # 按钮区域
        button_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        button_frame.pack(pady=20)
        
        # 按钮样式
        button_style = {
            'font': ('SimHei', 11),
            'width': 10,
            'relief': tk.RAISED,
            'bd': 2
        }
        
        # 添加按钮
        self.start_button = tk.Button(
            button_frame,
            text="开始动画",
            command=self.calculate,
            bg="#4CAF50",
            fg="white",
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            button_frame,
            text="暂停动画",
            command=self.toggle_pause,
            bg="#FF9800",
            fg="white",
            state=tk.DISABLED,
            **button_style
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            button_frame,
            text="重置",
            command=self.reset,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="理论知识", 
            command=self.show_theory,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
        
        # 添加说明文本区域
        self.info_text = tk.Text(
            self.control_frame,
            height=6,
            width=40,
            font=('SimHei', 11),
            relief='solid',
            bg='white',
            fg='#2C3E50',
            wrap=tk.WORD
        )
        self.info_text.pack(pady=20)
        self.info_text.insert('1.0', '操作说明：\n1. 选择向量运算类型\n2. 输入向量参数\n3. 点击"开始动画"观看运算过程\n4. 可以随时暂停/继续动画\n5. 使用"重置"清除当前动画')
        self.info_text.config(state='disabled')
        
        # 创建右侧绘图区域
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化绘图
        self.reset_plot()
    
    def on_closing(self):
        """窗口关闭时清理资源"""
        try:
            if hasattr(self, 'animation') and self.animation is not None:
                self.animation.event_source.stop()
            plt.close('all')
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
        finally:
            self.master.destroy()
    
    def init_input_widgets(self):
        """初始化输入控件"""
        # 清除现有控件
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        operation = self.operation_var.get()
        
        # 向量 a 输入
        vector_a_frame = tk.LabelFrame(self.input_frame, text="向量 a", bg="#E6F3FF", font=("SimHei", 11))
        vector_a_frame.pack(fill=tk.X, pady=5)
        
        a_x_frame = tk.Frame(vector_a_frame, bg="#E6F3FF")
        a_x_frame.pack(fill=tk.X, pady=2)
        tk.Label(a_x_frame, text="x:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
        self.a_x = tk.Entry(a_x_frame, width=10)
        self.a_x.pack(side=tk.LEFT, padx=5)
        self.a_x.insert(0, "1")
        
        a_y_frame = tk.Frame(vector_a_frame, bg="#E6F3FF")
        a_y_frame.pack(fill=tk.X, pady=2)
        tk.Label(a_y_frame, text="y:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
        self.a_y = tk.Entry(a_y_frame, width=10)
        self.a_y.pack(side=tk.LEFT, padx=5)
        self.a_y.insert(0, "2")
        
        a_z_frame = tk.Frame(vector_a_frame, bg="#E6F3FF")
        a_z_frame.pack(fill=tk.X, pady=2)
        tk.Label(a_z_frame, text="z:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
        self.a_z = tk.Entry(a_z_frame, width=10)
        self.a_z.pack(side=tk.LEFT, padx=5)
        self.a_z.insert(0, "1")
        
        if operation in ["向量加法", "向量减法", "向量点乘"]:
            # 向量 b 输入
            vector_b_frame = tk.LabelFrame(self.input_frame, text="向量 b", bg="#E6F3FF", font=("SimHei", 11))
            vector_b_frame.pack(fill=tk.X, pady=5)
            
            b_x_frame = tk.Frame(vector_b_frame, bg="#E6F3FF")
            b_x_frame.pack(fill=tk.X, pady=2)
            tk.Label(b_x_frame, text="x:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
            self.b_x = tk.Entry(b_x_frame, width=10)
            self.b_x.pack(side=tk.LEFT, padx=5)
            self.b_x.insert(0, "2")
            
            b_y_frame = tk.Frame(vector_b_frame, bg="#E6F3FF")
            b_y_frame.pack(fill=tk.X, pady=2)
            tk.Label(b_y_frame, text="y:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
            self.b_y = tk.Entry(b_y_frame, width=10)
            self.b_y.pack(side=tk.LEFT, padx=5)
            self.b_y.insert(0, "1")
            
            b_z_frame = tk.Frame(vector_b_frame, bg="#E6F3FF")
            b_z_frame.pack(fill=tk.X, pady=2)
            tk.Label(b_z_frame, text="z:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
            self.b_z = tk.Entry(b_z_frame, width=10)
            self.b_z.pack(side=tk.LEFT, padx=5)
            self.b_z.insert(0, "3")
        
        elif operation == "标量乘法":
            # 标量 k 输入
            scalar_frame = tk.LabelFrame(self.input_frame, text="标量 k", bg="#E6F3FF", font=("SimHei", 11))
            scalar_frame.pack(fill=tk.X, pady=5)
            
            k_frame = tk.Frame(scalar_frame, bg="#E6F3FF")
            k_frame.pack(fill=tk.X, pady=2)
            tk.Label(k_frame, text="k:", bg="#E6F3FF", width=3).pack(side=tk.LEFT, padx=5)
            self.scalar_k = tk.Entry(k_frame, width=10)
            self.scalar_k.pack(side=tk.LEFT, padx=5)
            self.scalar_k.insert(0, "2")
    
    def on_operation_change(self, event=None):
        """运算类型改变时更新输入控件"""
        operation = self.operation_var.get()
        
        # 重置绘图
        self.reset_plot()
        
        # 显示或隐藏标量输入框
        if operation == "标量乘法":
            # 隐藏向量b的输入框
            if hasattr(self, 'b_x'):
                self.b_x.master.master.pack_forget()
            if hasattr(self, 'b_y'):
                self.b_y.master.master.pack_forget()
            if hasattr(self, 'b_z'):
                self.b_z.master.master.pack_forget()
            
            # 显示标量k的输入框
            self.scalar_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            # 隐藏标量k的输入框
            self.scalar_frame.pack_forget()
    
    def reset_plot(self):
        """重置绘图"""
        if hasattr(self, 'animation') and self.animation is not None:
            # 安全停止动画
            if hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
                self.animation.event_source.stop()
            self.animation = None
        
        # 重新初始化坐标轴
        self.ax.clear()
        self.ax.set_xlim([-5, 5])
        self.ax.set_ylim([-5, 5])
        self.ax.set_zlim([-5, 5])
        self.ax.set_xlabel("X 轴", fontsize=10)
        self.ax.set_ylabel("Y 轴", fontsize=10)
        self.ax.set_zlabel("Z 轴", fontsize=10)
        self.ax.set_title("3D 向量运算可视化", fontsize=14)
        self.ax.set_facecolor('#F0F8FF')
        self.canvas.draw()
    
    def reset(self):
        """重置界面"""
        self.reset_plot()
        self.operation_combobox.current(0)
        self.init_input_widgets()
    
    def get_vector_a(self):
        """获取向量 a 的值"""
        try:
            return [float(self.a_x.get()), float(self.a_y.get()), float(self.a_z.get())]
        except:
            messagebox.showerror("输入错误", "请为向量 a 输入有效的数字！")
            return None
    
    def get_vector_b(self):
        """获取向量 b 的值"""
        try:
            return [float(self.b_x.get()), float(self.b_y.get()), float(self.b_z.get())]
        except:
            messagebox.showerror("输入错误", "请为向量 b 输入有效的数字！")
            return None
    
    def get_scalar_k(self):
        """获取标量 k 的值"""
        try:
            return float(self.scalar_k.get())
        except:
            messagebox.showerror("输入错误", "请为标量 k 输入有效的数字！")
            return None
    
    def calculate(self):
        """计算并显示结果"""
        operation = self.operation_var.get()
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        if operation == "向量加法":
            a = self.get_vector_a()
            b = self.get_vector_b()
            if a is not None and b is not None:
                self.animate_vector_addition(a, b)
        
        elif operation == "向量减法":
            a = self.get_vector_a()
            b = self.get_vector_b()
            if a is not None and b is not None:
                self.animate_vector_subtraction(a, b)
        
        elif operation == "标量乘法":
            a = self.get_vector_a()
            k = self.get_scalar_k()
            if a is not None and k is not None:
                self.animate_scalar_multiplication(a, k)
        
        elif operation == "向量点乘":
            a = self.get_vector_a()
            b = self.get_vector_b()
            if a is not None and b is not None:
                self.animate_dot_product(a, b)
        
        # 动画完成后恢复按钮状态
        self.start_button.config(state=tk.NORMAL)
    
    def animate_vector_addition(self, a, b):
        """向量加法动画"""
        # 停止现有动画
        if hasattr(self, 'animation') and self.animation is not None:
            if hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
                self.animation.event_source.stop()
            self.animation = None
        
        # 计算结果向量
        c = np.array(a) + np.array(b)
        
        # 设置坐标轴范围
        all_points = np.vstack([np.zeros(3), a, b, c])
        min_vals = np.min(all_points, axis=0) - 0.5
        max_vals = np.max(all_points, axis=0) + 0.5
        
        frames = 60
        self.paused = False  # 初始化暂停状态
        
        def update(frame):
            self.ax.clear()
            self.ax.set_title("向量加法: a + b = c", fontsize=16)
            self.ax.set_xlim(min_vals[0], max_vals[0])
            self.ax.set_ylim(min_vals[1], max_vals[1])
            self.ax.set_zlim(min_vals[2], max_vals[2])
            self.ax.set_box_aspect([1, 1, 1])
            self.ax.set_facecolor('#F0F8FF')
            
            t = min(frame / 30, 1.0)  # 0到1的过渡
            
            # 绘制向量 a
            arr_a = Arrow3D([0, a[0]], [0, a[1]], [0, a[2]],
                           mutation_scale=20, lw=2, arrowstyle="-|>", color="blue")
            self.ax.add_artist(arr_a)
            self.ax.text(a[0], a[1], a[2], f" a={a}", color="blue")
            
            # 绘制向量 b（从a的终点开始）
            if t > 0.5:
                t2 = (t - 0.5) * 2  # 0到1的过渡
                arr_b = Arrow3D([a[0], a[0] + b[0]*t2],
                              [a[1], a[1] + b[1]*t2],
                              [a[2], a[2] + b[2]*t2],
                              mutation_scale=20, lw=2, arrowstyle="-|>", color="red")
                self.ax.add_artist(arr_b)
                self.ax.text(a[0] + b[0], a[1] + b[1], a[2] + b[2], f" b={b}", color="red")
            
            # 绘制结果向量 c
            arr_c = Arrow3D([0, c[0]*t], [0, c[1]*t], [0, c[2]*t],
                           mutation_scale=20, lw=2.5, arrowstyle="-|>", color="green", alpha=0.5)
            self.ax.add_artist(arr_c)
            if t == 1.0:
                self.ax.text(c[0], c[1], c[2], f" c={c}", color="green")
                # 动画完成后恢复按钮状态
                self.start_button.config(state=tk.NORMAL)
            
            # 设置坐标轴标签
            self.ax.set_xlabel("X 轴", fontsize=12)
            self.ax.set_ylabel("Y 轴", fontsize=12)
            self.ax.set_zlabel("Z 轴", fontsize=12)
            
            return []
        
        self.animation = FuncAnimation(self.fig, update, frames=frames,
                                     interval=50, blit=True)
        self.canvas.draw()

    def animate_vector_subtraction(self, a, b):
        """向量减法动画"""
        # 停止现有动画
        if hasattr(self, 'animation') and self.animation is not None:
            if hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
                self.animation.event_source.stop()
            self.animation = None
        
        # 计算结果向量
        c = np.array(a) - np.array(b)
        
        # 设置坐标轴范围
        all_points = np.vstack([np.zeros(3), a, b, c])
        min_vals = np.min(all_points, axis=0) - 0.5
        max_vals = np.max(all_points, axis=0) + 0.5
        
        frames = 60
        self.paused = False  # 初始化暂停状态
        
        def update(frame):
            self.ax.clear()
            self.ax.set_title("向量减法: a - b = c", fontsize=16)
            self.ax.set_xlim(min_vals[0], max_vals[0])
            self.ax.set_ylim(min_vals[1], max_vals[1])
            self.ax.set_zlim(min_vals[2], max_vals[2])
            self.ax.set_box_aspect([1, 1, 1])
            self.ax.set_facecolor('#F0F8FF')
            
            t = min(frame / 30, 1.0)  # 0到1的过渡
            
            # 绘制向量 a
            arr_a = Arrow3D([0, a[0]], [0, a[1]], [0, a[2]],
                           mutation_scale=20, lw=2, arrowstyle="-|>", color="blue")
            self.ax.add_artist(arr_a)
            self.ax.text(a[0], a[1], a[2], f" a={a}", color="blue")
            
            # 绘制向量 -b
            if t > 0.5:
                t2 = (t - 0.5) * 2  # 0到1的过渡
                neg_b = [-b[0], -b[1], -b[2]]
                arr_b = Arrow3D([a[0], a[0] + neg_b[0]*t2],
                              [a[1], a[1] + neg_b[1]*t2],
                              [a[2], a[2] + neg_b[2]*t2],
                              mutation_scale=20, lw=2, arrowstyle="-|>", color="red")
                self.ax.add_artist(arr_b)
                self.ax.text(a[0] + neg_b[0], a[1] + neg_b[1], a[2] + neg_b[2],
                            f" -b={neg_b}", color="red")
            
            # 绘制结果向量 c
            arr_c = Arrow3D([0, c[0]*t], [0, c[1]*t], [0, c[2]*t],
                           mutation_scale=20, lw=2.5, arrowstyle="-|>", color="green", alpha=0.5)
            self.ax.add_artist(arr_c)
            if t == 1.0:
                self.ax.text(c[0], c[1], c[2], f" c={c}", color="green")
                # 动画完成后恢复按钮状态
                self.start_button.config(state=tk.NORMAL)
            
            # 设置坐标轴标签
            self.ax.set_xlabel("X 轴", fontsize=12)
            self.ax.set_ylabel("Y 轴", fontsize=12)
            self.ax.set_zlabel("Z 轴", fontsize=12)
            
            return []
        
        self.animation = FuncAnimation(self.fig, update, frames=frames,
                                     interval=50, blit=True)
        self.canvas.draw()

    def animate_scalar_multiplication(self, a, k):
        """标量乘法动画"""
        # 停止现有动画
        if hasattr(self, 'animation') and self.animation is not None:
            if hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
                self.animation.event_source.stop()
            self.animation = None
        
        # 计算结果向量
        c = k * np.array(a)
        
        # 设置坐标轴范围
        all_points = np.vstack([np.zeros(3), a, c])
        min_vals = np.min(all_points, axis=0) - 0.5
        max_vals = np.max(all_points, axis=0) + 0.5
        
        frames = 60
        self.paused = False  # 初始化暂停状态
        
        def update(frame):
            self.ax.clear()
            self.ax.set_title(f"标量乘法: {k}·a = c", fontsize=16)
            self.ax.set_xlim(min_vals[0], max_vals[0])
            self.ax.set_ylim(min_vals[1], max_vals[1])
            self.ax.set_zlim(min_vals[2], max_vals[2])
            self.ax.set_box_aspect([1, 1, 1])
            self.ax.set_facecolor('#F0F8FF')
            
            t = min(frame / 60, 1.0)  # 0到1的过渡
            
            # 绘制原始向量 a
            arr_a = Arrow3D([0, a[0]], [0, a[1]], [0, a[2]],
                           mutation_scale=20, lw=2, arrowstyle="-|>", color="blue")
            self.ax.add_artist(arr_a)
            self.ax.text(a[0], a[1], a[2], f" a={a}", color="blue")
            
            # 绘制结果向量 c
            scale = 1 + (k - 1) * t
            arr_c = Arrow3D([0, a[0]*scale], [0, a[1]*scale], [0, a[2]*scale],
                           mutation_scale=20, lw=2.5, arrowstyle="-|>", color="green")
            self.ax.add_artist(arr_c)
            if t == 1.0:
                self.ax.text(c[0], c[1], c[2], f" c={c}", color="green")
                # 动画完成后恢复按钮状态
                self.start_button.config(state=tk.NORMAL)
            
            # 设置坐标轴标签
            self.ax.set_xlabel("X 轴", fontsize=12)
            self.ax.set_ylabel("Y 轴", fontsize=12)
            self.ax.set_zlabel("Z 轴", fontsize=12)
            
            return []
        
        self.animation = FuncAnimation(self.fig, update, frames=frames,
                                     interval=50, blit=True)
        self.canvas.draw()

    def animate_dot_product(self, a, b):
        """点乘动画"""
        # 实现点乘的可视化效果

    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not hasattr(self, 'animation') or self.animation is None:
            return
        
        if self.paused:
            self.animation.event_source.start()
            self.pause_button.config(text="暂停")
        else:
            self.animation.event_source.stop()
            self.pause_button.config(text="继续")
        self.paused = not self.paused

    def save_plot(self):
        """保存当前图形为图片"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, dpi=300)
                messagebox.showinfo("保存成功", f"图形已保存为 {filename}")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存图形时出错: {str(e)}")

    def show_help(self):
        """显示帮助信息"""
        help_text = """操作说明：
1. 输入向量参数
2. 点击'计算'开始动画
3. 使用'暂停/继续'控制动画
4. 使用'重置'清除所有内容
5. 使用'保存'将当前图形保存为图片
6. 使用'切换视角'改变视图角度"""
        messagebox.showinfo("帮助", help_text)

    def toggle_view(self):
        """切换视图角度"""
        if self.current_view == '3d':
            self.ax.view_init(elev=20, azim=45)
            self.current_view = '2d'
        else:
            self.ax.view_init(elev=30, azim=45)
            self.current_view = '3d'
        self.canvas.draw()

    def stop_animation(self):
        """停止动画"""
        if hasattr(self, 'animation') and self.animation is not None:
            if hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
                self.animation.event_source.stop()
            self.animation = None
            self.reset_plot()
            self.canvas.draw()
        
        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def show_theory(self):
        """显示向量运算理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 向量运算知识点内容
            sections = {
                "基本概念": """
向量：向量是既有大小又有方向的量，在数学中通常用有向线段来表示。在线性代数中，向量可以用坐标表示，例如在二维空间中，向量v=(v1​,v2​)，其中v1​和v2​分别是向量在x轴和y轴上的分量。

1.向量加法：对于两个向量u=(u1​,u2​,⋯,un​)和v=(v1​,v2​,⋯,vn​)，它们的和u+v是一个新的向量，其坐标为(u1​+v1​,u2​+v2​,⋯,un​+vn​)。向量加法满足交换律u+v=v+u和结合律(u+v)+w=u+(v+w)。

2.向量减法：向量减法是向量加法的逆运算，对于向量u和v，u−v=u+(−v)，其中−v是v的相反向量，即−v=(−v1​,−v2​,⋯,−vn​)。

3.标量乘法：标量乘法是一个标量（实数）与向量的运算。对于标量k和向量v=(v1​,v2​,⋯,vn​)，kv=(kv1​,kv2​,⋯,kvn​)。当k>0时，kv与v方向相同，长度变为原来的k倍；当k<0时，kv与v方向相反，长度变为原来的∣k∣倍；当k=0时，kv=0。
""",
                "几何意义": """
向量运算的几何意义：

1.向量加法：在几何上，向量加法可以用平行四边形法则或三角形法则来表示。以平行四边形法则为例，将两个向量u和v的起点重合，以它们为邻边作平行四边形，那么从公共起点出发的对角线所表示的向量就是u+v。三角形法则是将一个向量的终点与另一个向量的起点相连，那么从第一个向量的起点到第二个向量的终点所构成的向量就是它们的和。

2.向量减法：向量减法u−v的几何意义可以看作是从向量v的终点指向向量u的终点的向量。

3.标量乘法：标量乘法kv表示将向量v沿着其原有方向（k>0）或相反方向（k<0）进行拉伸或压缩，拉伸或压缩的倍数为∣k∣。
""",
                "计算方法": """
向量计算的主要方法：

1. 向量加法：直接将对应坐标相加。
2. 向量减法：将对应坐标相减。
3. 标量乘法：用标量乘以向量的每个坐标。
""",
                "应用": """
1.物理学：在力学中，力、速度、加速度等都是向量，向量运算用于分析物体的受力情况、运动状态等。例如，多个力作用于一个物体时，通过向量加法可以求出合力；通过标量乘法可以计算力在某个方向上的分力。

2.计算机图形学：用于图形的平移、旋转、缩放等变换。例如，将一个点的坐标表示为向量，通过向量加法可以实现点的平移，通过标量乘法可以实现点的缩放。在三维图形中，向量运算还用于计算光照模型、法线向量等。

3.数据分析与机器学习：在数据处理中，向量可以表示数据样本，向量运算可以用于数据的标准化、特征提取等操作。在机器学习算法中，如线性回归、支持向量机等，向量运算被广泛用于计算模型的参数、预测结果等。

4.导航与定位：在导航系统中，向量用于表示位置、方向和位移。通过向量运算可以计算出从一个位置到另一个位置的位移向量，以及根据方向向量和速度向量计算出物体的运动轨迹。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "向量运算理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建向量运算理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("向量运算理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="向量运算理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
        # 几何意义选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="几何意义")
        
        # 计算方法选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="计算方法")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10)

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = VectorOperationsApp(root)
    root.mainloop()