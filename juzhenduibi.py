import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 自定义3D箭头类
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)

class MatrixComparisonApp:
    def __init__(self, master):
        self.master = master
        self.master.title("矩阵对比可视化")
        
        # 设置窗口样式
        style = ttk.Style()
        style.configure('TLabel', background='#E6F3FF')
        style.configure('TCombobox', background='#E6F3FF')
        
        # 创建左侧控制面板
        self.control_frame = tk.Frame(master, bg='#E6F3FF', width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            self.control_frame,
            text="矩阵对比可视化",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(pady=10)
        
        # 添加维度选择
        dimension_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        dimension_frame.pack(pady=10)
        
        self.dimension_var = tk.StringVar(value="2D")
        tk.Radiobutton(
            dimension_frame,
            text="2D模式",
            variable=self.dimension_var,
            value="2D",
            command=self.switch_dimension,
            bg='#E6F3FF'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            dimension_frame,
            text="3D模式",
            variable=self.dimension_var,
            value="3D",
            command=self.switch_dimension,
            bg='#E6F3FF'
        ).pack(side=tk.LEFT, padx=10)

        # 添加矩阵阶数选择
        size_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        size_frame.pack(pady=10)
        
        tk.Label(
            size_frame,
            text="矩阵阶数：",
            font=('SimHei', 11),
            bg='#E6F3FF',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar(value="2")
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["2", "3", "4"],
            state='readonly',
            width=5
        )
        size_combo.pack(side=tk.LEFT, padx=5)
        size_combo.bind('<<ComboboxSelected>>', self.update_matrix_size)
        
        # 矩阵输入区域
        self.matrix_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        self.matrix_frame.pack(pady=10)
        
        # 创建矩阵输入框
        self.create_matrix_inputs()
        
        # 按钮区域
        self.create_buttons()
        
        # 说明文本区域
        self.create_info_text()
        
        # 创建绘图区域
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111)  # 默认创建2D图形
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化动画状态
        self.animation = None
        self.paused = False
        
        # 初始化绘图
        self.switch_dimension()

    def create_matrix_inputs(self):
        """创建矩阵输入区域"""
        # 清除现有的矩阵输入框
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        size = int(self.size_var.get())
        
        # 矩阵A输入区域
        matrix_a_frame = tk.LabelFrame(
            self.matrix_frame,
            text="矩阵 A",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        matrix_a_frame.pack(fill=tk.X, pady=10)
        
        self.matrix_a_entries = []
        for i in range(size):
            row_frame = tk.Frame(matrix_a_frame, bg='#E6F3FF')
            row_frame.pack(pady=2)
            row_entries = []
            for j in range(size):
                entry = tk.Entry(row_frame, width=6)
                entry.pack(side=tk.LEFT, padx=2)
                entry.insert(0, "1" if i == j else "0")
                row_entries.append(entry)
            self.matrix_a_entries.append(row_entries)
        
        # 矩阵B输入区域
        matrix_b_frame = tk.LabelFrame(
            self.matrix_frame,
            text="矩阵 B",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50'
        )
        matrix_b_frame.pack(fill=tk.X, pady=10)
        
        self.matrix_b_entries = []
        for i in range(size):
            row_frame = tk.Frame(matrix_b_frame, bg='#E6F3FF')
            row_frame.pack(pady=2)
            row_entries = []
            for j in range(size):
                entry = tk.Entry(row_frame, width=6)
                entry.pack(side=tk.LEFT, padx=2)
                entry.insert(0, "1" if i == j else "0")
                row_entries.append(entry)
            self.matrix_b_entries.append(row_entries)

    def create_buttons(self):
        button_frame = tk.Frame(self.control_frame, bg='#E6F3FF')
        button_frame.pack(pady=20)
        
        button_style = {
            'font': ('SimHei', 11),
            'relief': 'raised',
            'bg': '#4A90E2',
            'fg': 'white',
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2',
            'width': 12,
            'borderwidth': 2
        }
        
        self.start_button = tk.Button(
            button_frame,
            text="开始动画",
            command=self.start_animation,
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            button_frame,
            text="暂停动画",
            command=self.toggle_pause,
            state=tk.DISABLED,
            **button_style
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            button_frame,
            text="重置",
            command=self.reset,
            **button_style
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="矩阵对比理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)

    def create_info_text(self):
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
        self.info_text.insert('1.0', '操作说明：\n1. 选择2D或3D模式\n2. 输入两个矩阵\n3. 点击"开始动画"观看矩阵变换对比\n4. 可以随时暂停/继续动画\n5. 使用"重置"清除当前动画')
        self.info_text.config(state='disabled')

    def switch_dimension(self):
        """切换2D/3D模式"""
        plt.clf()  # 清除当前图形
        if self.dimension_var.get() == "3D":
            self.ax = self.fig.add_subplot(111, projection='3d', computed_zorder=False)
            # 设置3D特有属性
            self.ax.set_proj_type('persp')  # 使用透视投影
        else:
            self.ax = self.fig.add_subplot(111)
        
        self.reset_plot()
        
        # 停止任何正在运行的动画
        if hasattr(self, 'animation') and self.animation is not None:
            try:
                self.animation.event_source.stop()
            except:
                pass
            self.animation = None
            # 重置按钮状态
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)

    def update_matrix_size(self, event=None):
        """更新矩阵大小"""
        self.create_matrix_inputs()
        self.reset()

    def get_matrix_a(self):
        """获取矩阵A的值"""
        size = int(self.size_var.get())
        try:
            return np.array([[float(self.matrix_a_entries[i][j].get())
                             for j in range(size)]
                            for i in range(size)])
        except:
            messagebox.showerror("输入错误", "请为矩阵A输入有效的数字！")
            return None
    
    def get_matrix_b(self):
        """获取矩阵B的值"""
        size = int(self.size_var.get())
        try:
            return np.array([[float(self.matrix_b_entries[i][j].get())
                             for j in range(size)]
                            for i in range(size)])
        except:
            messagebox.showerror("输入错误", "请为矩阵B输入有效的数字！")
            return None
    
    def reset_plot(self):
        """重置绘图"""
        self.ax.clear()
        if self.dimension_var.get() == "3D":
            self.ax.set_xlim([-5, 5])
            self.ax.set_ylim([-5, 5])
            self.ax.set_zlim([-5, 5])
            self.ax.set_xlabel("X 轴", fontsize=10)
            self.ax.set_ylabel("Y 轴", fontsize=10)
            self.ax.set_zlabel("Z 轴", fontsize=10)
        else:
            self.ax.set_xlim([-5, 5])
            self.ax.set_ylim([-5, 5])
            self.ax.set_xlabel("X 轴", fontsize=10)
            self.ax.set_ylabel("Y 轴", fontsize=10)
            self.ax.grid(True)
        
        self.ax.set_title("矩阵变换对比", fontsize=14)
        self.canvas.draw()
    
    def start_animation(self):
        """开始动画"""
        # 获取矩阵
        A = self.get_matrix_a()
        B = self.get_matrix_b()
        
        if A is None or B is None:
            return
        
        size = int(self.size_var.get())
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # 停止任何现有动画
        if hasattr(self, 'animation') and self.animation is not None:
            try:
                self.animation.event_source.stop()
            except:
                pass
            self.animation = None
        
        # 创建动画
        frames = 60
        
        def update(frame):
            self.ax.clear()
            if self.dimension_var.get() == "3D":
                self.ax.set_xlim([-5, 5])
                self.ax.set_ylim([-5, 5])
                self.ax.set_zlim([-5, 5])
                self.ax.set_xlabel("X 轴", fontsize=10)
                self.ax.set_ylabel("Y 轴", fontsize=10)
                self.ax.set_zlabel("Z 轴", fontsize=10)
                
                # 添加坐标轴
                self.ax.plot([-5, 5], [0, 0], [0, 0], 'k--', alpha=0.2)
                self.ax.plot([0, 0], [-5, 5], [0, 0], 'k--', alpha=0.2)
                self.ax.plot([0, 0], [0, 0], [-5, 5], 'k--', alpha=0.2)
            else:
                self.ax.set_xlim([-5, 5])
                self.ax.set_ylim([-5, 5])
                self.ax.set_xlabel("X 轴", fontsize=10)
                self.ax.set_ylabel("Y 轴", fontsize=10)
                self.ax.grid(True)
            
            t = frame / frames
            
            # 计算中间状态
            C_a = t * A + (1-t) * np.eye(size)
            C_b = t * B + (1-t) * np.eye(size)
            
            # 绘制原始基向量和变换后的向量
            if self.dimension_var.get() == "3D":
                # 3D模式下只显示前三个维度
                display_size = min(size, 3)
                for i in range(display_size):
                    # 原始基向量 - 修复3D quiver参数
                    basis = np.zeros(3)  # 确保是3D向量
                    basis[i] = 1
                    self.ax.quiver(0, 0, 0, basis[0], basis[1], basis[2], 
                                 color='gray', alpha=0.5, length=1.0)
                    
                    # 矩阵A的变换结果 - 确保向量有3个分量
                    vec_a = np.zeros(3)
                    vec_a[:display_size] = C_a[:display_size, i]
                    self.ax.quiver(0, 0, 0, vec_a[0], vec_a[1], vec_a[2], 
                                 color='blue', alpha=0.7, length=1.0)
                    
                    # 矩阵B的变换结果 - 确保向量有3个分量
                    vec_b = np.zeros(3)
                    vec_b[:display_size] = C_b[:display_size, i]
                    self.ax.quiver(0, 0, 0, vec_b[0], vec_b[1], vec_b[2], 
                                 color='red', alpha=0.7, length=1.0)
            else:
                # 2D模式下只显示前两个维度
                display_size = min(size, 2)
                for i in range(display_size):
                    # 原始基向量
                    basis = np.zeros(2)
                    basis[i] = 1
                    self.ax.quiver(0, 0, *basis, color='gray', alpha=0.5, 
                                 angles='xy', scale_units='xy', scale=1)
                    
                    # 矩阵A的变换结果
                    vec_a = C_a[:2, i]
                    self.ax.quiver(0, 0, *vec_a, color='blue', alpha=0.7,
                                 angles='xy', scale_units='xy', scale=1)
                    
                    # 矩阵B的变换结果
                    vec_b = C_b[:2, i]
                    self.ax.quiver(0, 0, *vec_b, color='red', alpha=0.7,
                                 angles='xy', scale_units='xy', scale=1)
            
            # 添加图例
            self.ax.plot([], [], color='gray', label='原始基向量')
            self.ax.plot([], [], color='blue', label='矩阵A变换')
            self.ax.plot([], [], color='red', label='矩阵B变换')
            self.ax.legend()
            
            return []
        
        # 使用更稳定的动画配置
        self.animation = FuncAnimation(
            self.fig, 
            update, 
            frames=frames,
            interval=50, 
            blit=False,  # 禁用blit以确保正确渲染
            repeat=True  # 允许动画重复
        )
        
        # 强制重绘
        self.canvas.draw_idle()
        
        # 确保动画与Tkinter事件循环集成
        self.master.after(100, self._ensure_animation_running)

    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not hasattr(self, 'animation') or self.animation is None:
            return
        
        if self.paused:
            self.animation.event_source.start()
            self.pause_button.config(text="暂停动画")
        else:
            self.animation.event_source.stop()
            self.pause_button.config(text="继续动画")
        self.paused = not self.paused
    
    def reset(self):
        """重置界面"""
        if hasattr(self, 'animation') and self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
        
        # 重置按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button.config(text="暂停动画")
        self.paused = False
        
        # 重置绘图
        self.reset_plot()

    def show_theory(self):
        """显示矩阵对比理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 矩阵对比知识点内容
            sections = {
                "基本概念": """
1.同型矩阵：两个矩阵如果行数和列数分别相等，则称它们是同型矩阵。

2.矩阵相等：若两个同型矩阵对应位置的元素都相等，则这两个矩阵相等。

3.矩阵的秩：矩阵的秩是矩阵的一个重要数字特征，它是指矩阵中线性无关的行（或列）向量的最大个数。
""",
                "几何意义": """
1.同型矩阵：从几何角度看，同型矩阵可以表示相同维度空间中的线性变换或向量组。例如，两个2×2的矩阵都可以表示二维平面上的线性变换，它们作用于平面上的向量，将向量进行拉伸、旋转、反射等操作。

2.矩阵相等：矩阵相等意味着它们所代表的线性变换或向量组在所有对应方面都是完全相同的，在几何上表现为对空间的变换效果完全一致，或者所表示的向量组在空间中的位置和分布完全相同。

3.矩阵的秩：矩阵的秩反映了矩阵所对应的线性变换对空间的 “压缩” 程度。秩越大，说明线性变换后空间的 “维数” 越高，保留的信息越多；秩越小，空间被 “压缩” 得越厉害。例如，一个秩为1的2×2矩阵，它将二维平面上的向量都映射到一条直线上，即把二维空间压缩到了一维空间。
""",
                "计算方法": """
1.同型矩阵判断：直接比较两个矩阵的行数和列数是否分别相等即可。

2.矩阵相等判断：对于同型矩阵，逐一比较对应位置的元素是否相等。

3.矩阵秩的计算：
  -初等变换法：通过对矩阵进行初等行变换或初等列变换，将矩阵化为阶梯形矩阵，阶梯形矩阵中非零行的行数就是矩阵的秩。
  -利用行列式：对于n阶方阵，如果它的某个r阶子式不为零，而所有r+1阶子式（如果存在的话）都为零，则矩阵的秩为r。
""",
                "应用": """
1.同型矩阵：在矩阵运算中，只有同型矩阵才能进行加法和减法运算。例如，在多个线性变换组合的问题中，如果这些线性变换可以用同型矩阵表示，那么它们的和或差就对应了组合后的线性变换，方便分析和计算多个线性变换的综合效果。

2.矩阵相等：在求解线性方程组时，如果两个增广矩阵相等，那么它们所对应的线性方程组是同解方程组。此外，在证明一些矩阵性质或等式时，常常需要根据矩阵相等的定义来进行推导和论证。

3.矩阵的秩：
  -判断线性方程组的解：根据系数矩阵的秩和增广矩阵的秩的关系来判断线性方程组解的情况。当系数矩阵的秩等于增广矩阵的秩且等于未知数的个数时，线性方程组有唯一解；当系数矩阵的秩等于增广矩阵的秩且小于未知数的个数时，线性方程组有无穷多解；当系数矩阵的秩不等于增广矩阵的秩时，线性方程组无解。
  -向量组的线性相关性：可以通过矩阵的秩来判断向量组的线性相关性。若向量组构成的矩阵的秩等于向量组中向量的个数，则向量组线性无关；若秩小于向量的个数，则向量组线性相关。
  -矩阵的相似与合同：在研究矩阵的相似和合同关系时，矩阵的秩是一个重要的不变量。相似矩阵和合同矩阵具有相同的秩，这一性质在判断矩阵是否相似或合同以及对矩阵进行分类时具有重要作用。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "矩阵对比理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建矩阵对比理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("矩阵对比理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="矩阵对比理论知识", 
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

    def _ensure_animation_running(self):
        """确保动画正在运行"""
        if hasattr(self, 'animation') and self.animation is not None:
            # 强制更新画布
            self.canvas.draw_idle()
            # 刷新事件
            self.fig.canvas.flush_events()
            # 继续检查
            if not self.paused:
                self.master.after(100, self._ensure_animation_running)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixComparisonApp(root)
    root.mainloop() 