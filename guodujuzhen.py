import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
import matplotlib.animation as animation
import matplotlib.font_manager as fm

# 检查系统中可用的中文字体
def get_available_chinese_font():
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STXihei', 'STHeiti', 'SimSun', 'NSimSun']
    available_font = None
    for font in chinese_fonts:
        if any(f.name == font for f in fm.fontManager.ttflist):
            available_font = font
            break
    return available_font or 'SimHei'

# 设置中文字体
chinese_font = get_available_chinese_font()
plt.rcParams["font.sans-serif"] = [chinese_font]
plt.rcParams["axes.unicode_minus"] = False

class Arrow3D(FancyArrowPatch):
    """
    用于在 3D 坐标系中绘制箭头的对象。
    """
    def __init__(self, xs, ys, zs, *args, **kwargs):
        # xs, ys, zs 为 [起点, 终点] 数据
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.get_proj())
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)

    def update(self, xs, ys, zs):
        self._verts3d = xs, ys, zs

class MatrixTransitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D 基变换与向量表示动画")

        # 创建输入框和按钮的框架
        input_frame = tk.Frame(self.root, bg='#E6F3FF')  # 添加背景色
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            input_frame,
            text="3D 基变换与向量表示",
            font=('SimHei', 16, 'bold'),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        title_label.pack(pady=(0, 20))

        # 输入过渡矩阵的文本框
        matrix_label = tk.Label(
            input_frame,
            text="输入3×3过渡矩阵：",
            font=('SimHei', 12),
            bg='#E6F3FF',
            fg='#2C3E50'
        )
        matrix_label.pack(pady=(0, 10))

        # 创建矩阵输入区域
        self.entry_rows = []
        for i in range(3):
            row_frame = tk.Frame(input_frame, bg='#E6F3FF')
            row_frame.pack(pady=5)
            entry_row = []
            for j in range(3):
                entry = tk.Entry(
                    row_frame,
                    width=8,
                    font=('Consolas', 12),
                    justify='center',
                    relief='solid',
                    bg='white',
                    fg='#2C3E50'
                )
                entry.pack(side=tk.LEFT, padx=5)
                entry.insert(0, '1' if i == j else '0')  # 默认为单位矩阵
                entry_row.append(entry)
            self.entry_rows.append(entry_row)

        # 按钮样式
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

        # 按钮区域
        button_frame = tk.Frame(input_frame, bg='#E6F3FF')
        button_frame.pack(pady=20)

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="过渡矩阵理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)
        
        # 添加随机矩阵按钮
        self.random_button = tk.Button(
            button_frame,
            text="随机矩阵",
            command=self.generate_random_matrix,
            **button_style
        )
        self.random_button.pack(side=tk.LEFT, padx=5)

        # 其他按钮
        self.start_button = tk.Button(button_frame, text="开始动画", command=self.start_animation, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(button_frame, text="暂停动画", command=self.pause_animation, state=tk.DISABLED, **button_style)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="停止动画", command=self.stop_animation, state=tk.DISABLED, **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(button_frame, text="退出", command=self.root.quit, **button_style)
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
        # 添加动画说明文本区域
        self.info_text = tk.Text(
            input_frame,
            height=6,
            width=40,
            font=('SimHei', 11),
            relief='solid',
            bg='white',
            fg='#2C3E50',
            wrap=tk.WORD
        )
        self.info_text.pack(pady=20)
        self.info_text.insert('1.0', '动画说明：\n1. 输入3×3过渡矩阵或使用随机矩阵\n2. 点击"开始动画"观看基变换过程\n3. 可以随时暂停/继续动画\n4. 观察向量在不同基下的表示变化')
        self.info_text.config(state='disabled')

        # 创建Matplotlib图形和画布
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 初始化动画参数
        self.v = np.array([3, 2, 1])
        self.P = None
        self.anim = None
        self.is_paused = False

        # 初始化图形元素
        self.init_plot()

    def init_plot(self):
        # 设置坐标轴范围和标签
        self.ax.set_xlim(-1, 5)
        self.ax.set_ylim(-1, 5)
        self.ax.set_zlim(-1, 5)
        self.ax.set_xlabel("X 轴", fontsize=12)
        self.ax.set_ylabel("Y 轴", fontsize=12)
        self.ax.set_zlabel("Z 轴", fontsize=12)
        self.ax.set_title("3D 基变换与向量表示动画", fontsize=16)

        # 绘制标准基 {e1, e2, e3}（灰色虚线箭头）
        e1 = np.array([1, 0, 0])
        e2 = np.array([0, 1, 0])
        e3 = np.array([0, 0, 1])
        self.arrow_e1 = Arrow3D([0, e1[0]], [0, e1[1]], [0, e1[2]],
                                mutation_scale=20, lw=1.5, arrowstyle="-|>", color="gray")
        self.arrow_e2 = Arrow3D([0, e2[0]], [0, e2[1]], [0, e2[2]],
                                mutation_scale=20, lw=1.5, arrowstyle="-|>", color="gray")
        self.arrow_e3 = Arrow3D([0, e3[0]], [0, e3[2]], [0, e3[2]],
                                mutation_scale=20, lw=1.5, arrowstyle="-|>", color="gray")
        self.ax.add_artist(self.arrow_e1)
        self.ax.add_artist(self.arrow_e2)
        self.ax.add_artist(self.arrow_e3)
        self.ax.text(e1[0], e1[1], e1[2], "$e_1$", color="gray", fontsize=12)
        self.ax.text(e2[0], e2[1], e2[2], "$e_2$", color="gray", fontsize=12)
        self.ax.text(e3[0], e3[1], e3[2], "$e_3$", color="gray", fontsize=12)

        # 绘制固定向量 v（黑色大箭头）
        self.arrow_v = Arrow3D([0, self.v[0]], [0, self.v[1]], [0, self.v[2]],
                               mutation_scale=20, lw=2.5, arrowstyle="-|>", color="black")
        self.ax.add_artist(self.arrow_v)
        self.ax.text(self.v[0], self.v[1], self.v[2], "$v=(3,2,1)$", color="black", fontsize=12)

        # 初始化新基向量箭头（初始时与标准基一致）
        self.newA1 = Arrow3D([0, 1], [0, 0], [0, 0],
                             mutation_scale=20, lw=2, arrowstyle="-|>", color="red")
        self.newA2 = Arrow3D([0, 0], [0, 1], [0, 0],
                             mutation_scale=20, lw=2, arrowstyle="-|>", color="blue")
        self.newA3 = Arrow3D([0, 0], [0, 0], [0, 1],
                             mutation_scale=20, lw=2, arrowstyle="-|>", color="green")
        self.ax.add_artist(self.newA1)
        self.ax.add_artist(self.newA2)
        self.ax.add_artist(self.newA3)
        self.ax.text(1, 0, 0, "$v_1$", color="red", fontsize=12)
        self.ax.text(0, 1, 0, "$v_2$", color="blue", fontsize=12)
        self.ax.text(0, 0, 1, "$v_3$", color="green", fontsize=12)

        # 初始化分解贡献箭头（改为使用 arrowstyle "->" 并设置 linestyle 为 "dashed"）
        self.contA1 = Arrow3D([0, 0], [0, 0], [0, 0],
                              mutation_scale=20, lw=2, arrowstyle="->", color="red", linestyle="dashed")
        self.contA2 = Arrow3D([0, 0], [0, 0], [0, 0],
                              mutation_scale=20, lw=2, arrowstyle="->", color="blue", linestyle="dashed")
        self.contA3 = Arrow3D([0, 0], [0, 0], [0, 0],
                              mutation_scale=20, lw=2, arrowstyle="->", color="green", linestyle="dashed")
        self.ax.add_artist(self.contA1)
        self.ax.add_artist(self.contA2)
        self.ax.add_artist(self.contA3)

        # 动态文字说明（放置于图形左上角）
        self.text_obj = self.fig.text(0.01, 0.95, "", fontsize=12, color="darkblue",
                                      bbox=dict(facecolor='white', alpha=0.8))

    def generate_random_matrix(self):
        """生成随机矩阵"""
        random_matrix = np.random.uniform(-2, 2, (3, 3))
        for i in range(3):
            for j in range(3):
                self.entry_rows[i][j].delete(0, tk.END)
                self.entry_rows[i][j].insert(0, f"{random_matrix[i,j]:.2f}")

    def get_transition_matrix(self):
        # 从输入框获取过渡矩阵
        try:
            P = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    value = float(self.entry_rows[i][j].get())
                    P[i, j] = value
            return P
        except:
            tk.messagebox.showerror("输入错误", "请输入有效的数字！")
            return None

    def update(self, frame, N_frames, v, newA1, newA2, newA3, contA1, contA2, contA3, text_obj, P):
        # t 从 0 到 1 实现过渡
        t = frame / float(N_frames)
        I = np.eye(3)
        B = I + t * (P - I)  # 当前过渡矩阵：从标准基到新基
        # 新基向量为 B 的各列
        v1 = B[:, 0]
        v2 = B[:, 1]
        v3 = B[:, 2]
        # 求解 v 在当前新基下的坐标：B * [a, b, c]^T = v
        try:
            coeff = np.linalg.solve(B, v)
        except np.linalg.LinAlgError:
            coeff = np.array([0, 0, 0])
        a, b, c = coeff
        # 计算分解贡献：a*v1, a*v1+b*v2, a*v1+b*v2+c*v3
        tip1 = a * v1
        tip2 = tip1 + b * v2
        tip3 = tip2 + c * v3

        # 更新新基箭头（实线箭头显示，新基随 t 动态变化）
        newA1.update([0, v1[0]], [0, v1[1]], [0, v1[2]])
        newA2.update([0, v2[0]], [0, v2[1]], [0, v2[2]])
        newA3.update([0, v3[0]], [0, v3[1]], [0, v3[2]])
        # 更新分解贡献箭头（改为使用有效的 arrowstyle，并加上 linestyle="dashed"）
        contA1.update([0, tip1[0]], [0, tip1[1]], [0, tip1[2]])
        contA2.update([tip1[0], tip2[0]], [tip1[1], tip2[1]], [tip1[2], tip2[2]])
        contA3.update([tip2[0], tip3[0]], [tip2[1], tip3[1]], [tip2[2], tip3[2]])

        # 添加平滑的颜色渐变效果
        color1 = np.array([1, 0, 0])  # 红色
        color2 = np.array([0, 0, 1])  # 蓝色
        color = color1 * (1-t) + color2 * t
        
        # 更新箭头颜色和透明度
        newA1.set_color(color)
        newA2.set_color(color)
        newA3.set_color(color)
        
        # 添加箭头缩放效果
        scale = 1 + 0.2 * np.sin(2 * np.pi * t)
        mutation_scale = 20 * scale
        
        newA1.set_mutation_scale(mutation_scale)
        newA2.set_mutation_scale(mutation_scale)
        newA3.set_mutation_scale(mutation_scale)
        
        # 更新文本显示效果
        text_obj.set_text(
            "标准基下: $v=(3,2,1)$\n" +
            "新基 (过渡中):\n" +
            "  $v_{1}=(%.2f, %.2f, %.2f)$\n" % (v1[0], v1[1], v1[2]) +
            "  $v_{2}=(%.2f, %.2f, %.2f)$\n" % (v2[0], v2[1], v2[2]) +
            "  $v_{3}=(%.2f, %.2f, %.2f)$\n" % (v3[0], v3[1], v3[2]) +
            "系数: $a=%.2f,\, b=%.2f,\, c=%.2f$\n" % (a, b, c) +
            "重构: $a v_{1}+b v_{2}+c v_{3}=(%.2f, %.2f, %.2f)$\n" % (tip3[0], tip3[1], tip3[2]) +
            "过渡参数: t = %.2f" % t
        )
        text_obj.set_bbox(dict(
            facecolor='white',
            edgecolor='#4A90E2',
            alpha=0.8,
            boxstyle='round,pad=0.5'
        ))
        
        return newA1, newA2, newA3, contA1, contA2, contA3, text_obj

    def start_animation(self):
        # 开始动画
        self.P = self.get_transition_matrix()
        if self.P is None:
            return

        # 创建动画
        N_frames = 100
        self.anim = animation.FuncAnimation(
            self.fig, self.update, frames=range(0, N_frames + 1),
            fargs=(N_frames, self.v, self.newA1, self.newA2, self.newA3,
                   self.contA1, self.contA2, self.contA3, self.text_obj, self.P),
            interval=100, blit=False, repeat=True
        )
        self.canvas.draw()

        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

    def pause_animation(self):
        # 暂停动画
        if self.anim is not None:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.anim.event_source.stop()
            else:
                self.anim.event_source.start()

    def stop_animation(self):
        # 停止动画
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
            self.init_plot()
            self.canvas.draw()

        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

    def show_theory(self):
        """显示过渡矩阵理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 过渡矩阵知识点内容
            sections = {
                "基本概念": """
过渡矩阵是在线性空间中，从一个基到另一个基的变换矩阵。设{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}是线性空间V的两个基，若存在矩阵P，使得(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，则称矩阵P为从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵。
""",
                "几何意义": """
过渡矩阵在几何上可以理解为对线性空间中坐标系的一种变换。它将向量在一个基下的坐标表示转换为在另一个基下的坐标表示，就如同在平面或空间中，从一个坐标系转换到另一个坐标系时，向量的坐标会发生相应的变化，而过渡矩阵描述了这种坐标变换的关系。例如，在二维平面中，从直角坐标系转换到一个斜坐标系，过渡矩阵就确定了向量在这两个不同坐标系下坐标的转换方式，保证向量的几何位置和长度、夹角等几何性质在坐标变换前后保持不变。
""",
                "计算方法": """
方法一：根据定义求解
已知两个基{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}，将每个β​i​用α1​,α2​,⋯,αn​线性表示，即β​i​=p1i​α1​+p2i​α2​+⋯+pni​αn​，其中i=1,2,⋯,n。那么过渡矩阵P=(pij​)n×n​，其中pij​为β​j​在αi​下的坐标分量。

方法二：利用可逆矩阵性质
如果已知基变换的表达式(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，且(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是线性无关的向量组，那么矩阵(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是可逆的。此时可以通过P=(α1​,α2​,⋯,αn​)−1(β​1​,β​2​,⋯,β​n​)来计算过渡矩阵P。
""",
                "应用": """
1.坐标变换：在不同基下向量的坐标通过过渡矩阵进行转换。若向量v在基{α1​,α2​,⋯,αn​}下的坐标为X=(x1​,x2​,⋯,xn​)T，在基{β​1​,β​2​,⋯,β​n​}下的坐标为Y=(y1​,y2​,⋯,yn​)T，且从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有X=PY。这在解决线性空间中向量的坐标表示问题时非常有用，方便在不同的基下对向量进行分析和计算。

2.线性变换的矩阵表示：设线性变换T在基{α1​,α2​,⋯,αn​}下的矩阵为A，在基{β​1​,β​2​,⋯,β​n​}下的矩阵为B，从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有B=P−1AP。通过选择合适的基，利用过渡矩阵可以将线性变换的矩阵化为相似标准形，如对角矩阵，从而简化线性变换的计算和性质研究，例如求线性变换的特征值、判断线性变换的可对角化等问题。

3.几何变换：在计算机图形学和几何计算中，过渡矩阵可用于实现图形的各种几何变换，如旋转、缩放、平移等。通过将图形的顶点坐标在不同的基下进行转换，利用过渡矩阵可以方便地实现图形在不同坐标系或不同表示方式下的变换，提高图形处理的效率和灵活性。
"""
            }
            
            # 创建知识框架 - 修改这里，使用self.root而不是self.master
            KnowledgeFrame(self.root, "过渡矩阵理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建过渡矩阵理论知识窗口"""
        theory_window = tk.Toplevel(self.root)
        theory_window.title("过渡矩阵理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="过渡矩阵理论知识", 
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
        
        # 填充内容
        # 基本概念内容
        concept_text = tk.Text(concept_frame, wrap=tk.WORD, width=70, height=20, font=("SimHei", 11))
        concept_text.pack(fill=tk.BOTH, expand=True)
        concept_text.insert(tk.END, """过渡矩阵是在线性空间中，从一个基到另一个基的变换矩阵。设{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}是线性空间V的两个基，若存在矩阵P，使得(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，则称矩阵P为从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵。""")
        concept_text.config(state=tk.DISABLED)
        
        # 几何意义内容
        geometric_text = tk.Text(geometric_frame, wrap=tk.WORD, width=70, height=20, font=("SimHei", 11))
        geometric_text.pack(fill=tk.BOTH, expand=True)
        geometric_text.insert(tk.END, """过渡矩阵在几何上可以理解为对线性空间中坐标系的一种变换。它将向量在一个基下的坐标表示转换为在另一个基下的坐标表示，就如同在平面或空间中，从一个坐标系转换到另一个坐标系时，向量的坐标会发生相应的变化，而过渡矩阵描述了这种坐标变换的关系。例如，在二维平面中，从直角坐标系转换到一个斜坐标系，过渡矩阵就确定了向量在这两个不同坐标系下坐标的转换方式，保证向量的几何位置和长度、夹角等几何性质在坐标变换前后保持不变。""")
        geometric_text.config(state=tk.DISABLED)
        
        # 计算方法内容
        calculation_text = tk.Text(calculation_frame, wrap=tk.WORD, width=70, height=20, font=("SimHei", 11))
        calculation_text.pack(fill=tk.BOTH, expand=True)
        calculation_text.insert(tk.END, """方法一：根据定义求解
已知两个基{α1​,α2​,⋯,αn​}和{β​1​,β​2​,⋯,β​n​}，将每个β​i​用α1​,α2​,⋯,αn​线性表示，即β​i​=p1i​α1​+p2i​α2​+⋯+pni​αn​，其中i=1,2,⋯,n。那么过渡矩阵P=(pij​)n×n​，其中pij​为β​j​在αi​下的坐标分量。

方法二：利用可逆矩阵性质
如果已知基变换的表达式(β​1​,β​2​,⋯,β​n​)=(α1​,α2​,⋯,αn​)P，且(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是线性无关的向量组，那么矩阵(α1​,α2​,⋯,αn​)和(β​1​,β​2​,⋯,β​n​)都是可逆的。此时可以通过P=(α1​,α2​,⋯,αn​)−1(β​1​,β​2​,⋯,β​n​)来计算过渡矩阵P。""")
        calculation_text.config(state=tk.DISABLED)
        
        # 应用内容
        application_text = tk.Text(application_frame, wrap=tk.WORD, width=70, height=20, font=("SimHei", 11))
        application_text.pack(fill=tk.BOTH, expand=True)
        application_text.insert(tk.END, """1.坐标变换：在不同基下向量的坐标通过过渡矩阵进行转换。若向量v在基{α1​,α2​,⋯,αn​}下的坐标为X=(x1​,x2​,⋯,xn​)T，在基{β​1​,β​2​,⋯,β​n​}下的坐标为Y=(y1​,y2​,⋯,yn​)T，且从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有X=PY。这在解决线性空间中向量的坐标表示问题时非常有用，方便在不同的基下对向量进行分析和计算。

2.线性变换的矩阵表示：设线性变换T在基{α1​,α2​,⋯,αn​}下的矩阵为A，在基{β​1​,β​2​,⋯,β​n​}下的矩阵为B，从基{α1​,α2​,⋯,αn​}到基{β​1​,β​2​,⋯,β​n​}的过渡矩阵为P，则有B=P−1AP。通过选择合适的基，利用过渡矩阵可以将线性变换的矩阵化为相似标准形，如对角矩阵，从而简化线性变换的计算和性质研究，例如求线性变换的特征值、判断线性变换的可对角化等问题。

3.几何变换：在计算机图形学和几何计算中，过渡矩阵可用于实现图形的各种几何变换，如旋转、缩放、平移等。通过将图形的顶点坐标在不同的基下进行转换，利用过渡矩阵可以方便地实现图形在不同坐标系或不同表示方式下的变换，提高图形处理的效率和灵活性。""")
        application_text.config(state=tk.DISABLED)
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                                 command=theory_window.destroy)
        close_button.pack(pady=10)

                    

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixTransitionApp(root)
    root.mainloop()
