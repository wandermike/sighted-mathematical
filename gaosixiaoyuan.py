import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageTk
import os

# 检查系统中可用的中文字体
def get_available_chinese_font():
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STXihei', 'STHeiti', 'SimSun', 'NSimSun']
    available_font = None
    for font in chinese_fonts:
        if any(f.name == font for f in fm.fontManager.ttflist):
            available_font = font
            break
    return available_font or 'SimHei'  # 如果都不可用，默认使用 SimHei

# 设置中文字体
chinese_font = get_available_chinese_font()
plt.rcParams["font.sans-serif"] = [chinese_font]
plt.rcParams["axes.unicode_minus"] = False

# 使用内置样式
plt.style.use('ggplot')

# 添加商标加载函数
def add_logo(window, size=(80, 80)):
    """
    在窗口右上角添加商标
    
    参数:
    window -- 要添加商标的窗口
    size -- 商标大小，默认为(80, 80)
    """
    try:
        # 尝试加载商标图片
        logo_path = "yuanhui.png"
        if os.path.exists(logo_path):
            # 加载并调整商标大小
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize(size, Image.LANCZOS)  # 调整大小
            logo_tk = ImageTk.PhotoImage(logo_image)
            
            # 创建一个标签来显示商标
            logo_label = tk.Label(
                window,
                image=logo_tk,
                bg='#E6F3FF',  # 使用淡蓝色背景
                bd=0
            )
            # 放置在右上角
            logo_label.place(x=window.winfo_width()-size[0]-10, y=10)
            
            # 保存引用，防止垃圾回收
            logo_label.image = logo_tk
            
            # 绑定窗口大小变化事件，确保商标始终在右上角
            def adjust_logo_position(event=None):
                logo_label.place(x=window.winfo_width()-size[0]-10, y=10)
            
            window.bind("<Configure>", adjust_logo_position)
            
            # 初始调整一次位置
            window.after(100, adjust_logo_position)
            
            return logo_label
    except Exception as e:
        print(f"无法加载商标: {str(e)}")
        return None

class GaussianEliminationApp:
    def __init__(self, master):
        self.master = master
        master.title("高斯消元动画展示")
        
        # 设置主窗口背景色为淡蓝色
        master.configure(bg='#E6F3FF')  # 淡蓝色背景
        
        # 创建主框架并设置背景色
        main_frame = tk.Frame(master, bg='#E6F3FF')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 添加商标
        add_logo(master)
        
        # 输入区域改进
        input_frame = tk.Frame(main_frame, bg='#E6F3FF')
        input_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=10)
        
        # 左侧：矩阵大小选择区域
        size_frame = tk.Frame(input_frame, bg='#E6F3FF')
        size_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # 矩阵大小选择标签
        tk.Label(
            size_frame,
            text="矩阵大小设置：",
            bg='#E6F3FF',
            font=('SimHei', 11, 'bold'),
            fg='#2C3E50'
        ).pack(anchor=tk.W, pady=5)
        
        # 行数选择
        row_frame = tk.Frame(size_frame, bg='#E6F3FF')
        row_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            row_frame,
            text="行数：",
            bg='#E6F3FF',
            font=('SimHei', 10)
        ).pack(side=tk.LEFT)
        self.row_var = tk.StringVar(value="3")
        row_spinbox = ttk.Spinbox(
            row_frame,
            from_=1,
            to=10,
            width=5,
            textvariable=self.row_var,
            command=self.update_matrix_size,
            style='Matrix.TSpinbox',
            font=('Consolas', 11)
        )
        row_spinbox.pack(side=tk.LEFT, padx=5)
        
        # 列数选择
        col_frame = tk.Frame(size_frame, bg='#E6F3FF')
        col_frame.pack(fill=tk.X, pady=2)
        tk.Label(
            col_frame,
            text="列数：",
            bg='#E6F3FF',
            font=('SimHei', 10)
        ).pack(side=tk.LEFT)
        self.col_var = tk.StringVar(value="4")
        col_spinbox = ttk.Spinbox(
            col_frame,
            from_=1,
            to=10,
            width=5,
            textvariable=self.col_var,
            command=self.update_matrix_size
        )
        col_spinbox.pack(side=tk.LEFT, padx=5)
        
        # 中间：矩阵输入区域
        matrix_input_frame = tk.Frame(input_frame, bg='#E6F3FF')
        matrix_input_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # 矩阵输入提示
        tk.Label(
            matrix_input_frame,
            text="矩阵输入格式示例：\n3 4\n2 1 -1 8\n-3 -1 2 -11\n-2 1 2 -3",
            bg='#E6F3FF',
            font=('SimHei', 11),
            fg='#2C3E50',
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=5)
        
        # 创建自定义颜色映射
        self.custom_cmap = LinearSegmentedColormap.from_list('custom', 
            ['#FFFFFF', '#E3F2FD', '#90CAF9', '#2196F3'])
        
        # 设置矩阵输入框样式
        self.matrix_text = tk.Text(
            matrix_input_frame,
            height=10,
            width=45,
            font=('Consolas', 12),
            relief='solid',
            padx=15,
            pady=15,
            bg='white',
            fg='#2C3E50',
            insertbackground='#4A90E2',
            selectbackground='#4A90E2',
            selectforeground='white',
            wrap='none'
        )
        self.matrix_text.pack(pady=5)
        
        # 右侧：按钮区域
        button_frame = tk.Frame(input_frame, bg='#E6F3FF')
        button_frame.pack(side=tk.RIGHT, padx=20, fill=tk.Y)
        
        # 按钮样式保持不变
        button_style = {
            'font': ('SimHei', 11),
            'relief': 'raised',
            'bg': '#4A90E2',
            'fg': 'white',
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2',
            'width': 12,
            'borderwidth': 2
        }
        
        # 随机生成矩阵按钮
        self.random_button = tk.Button(
            button_frame,
            text="随机生成",
            command=self.generate_random_matrix,
            **button_style
        )
        self.random_button.pack(side=tk.TOP, pady=15)
        
        # 使用默认矩阵按钮
        self.default_button = tk.Button(
            button_frame,
            text="使用默认矩阵",
            command=self.use_default_matrix,
            **button_style
        )
        self.default_button.pack(side=tk.TOP, pady=15)
        
        # 生成动画按钮
        self.submit_button = tk.Button(
            button_frame,
            text="生成动画",
            command=self.generate_animation,
            **button_style
        )
        self.submit_button.pack(side=tk.TOP, pady=15)
        
        # 在按钮区域添加重新输入按钮
        self.reset_button = tk.Button(
            button_frame,
            text="重新输入",
            command=self.reset_animation,
            **button_style
        )
        self.reset_button.pack(side=tk.TOP, pady=15)
        # 初始时禁用重新输入按钮
        self.reset_button.config(state='disabled')

        # 添加理论知识按钮
        self.theory_button = tk.Button(
            button_frame, 
            text="高斯消元法理论知识", 
            command=self.show_theory,
            **button_style
        )
        self.theory_button.pack(side=tk.TOP, pady=15)
        
        # 动画显示区域
        self.animation_frame = tk.Frame(main_frame, bg='#E6F3FF')
        self.animation_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # 创建动画画布并设置背景色
        self.fig = plt.figure(figsize=(10, 8))
        self.fig.patch.set_facecolor('#E6F3FF')
        
        # Table 区域：上部区域
        self.ax_table = self.fig.add_axes([0.05, 0.35, 0.9, 0.55])
        self.ax_table.set_facecolor('#F5F9FF')
        self.ax_table.axis('off')
        
        # 说明日志区域：下部区域
        self.ax_log = self.fig.add_axes([0.1, 0.05, 0.8, 0.25])  # 缩小宽度使其居中
        self.ax_log.set_facecolor('#F5F9FF')
        self.ax_log.axis('off')
        
        # 修改说明文本背景框的创建方式
        self.description_box = self.ax_log.add_patch(
            FancyBboxPatch(
                (0, 0),  # 位置
                1, 1,    # 宽度和高度
                boxstyle='round,pad=0.5',  # 圆角和内边距
                facecolor='#FFFFFF',
                edgecolor='#4A90E2',
                alpha=0.9,
                transform=self.ax_log.transAxes,
                zorder=1,
                linewidth=2
            )
        )
        
        # 修改说明文本样式
        self.log_text = self.ax_log.text(
            0.5, 0.5,  # 居中显示
            "",
            transform=self.ax_log.transAxes,
            fontsize=13,  # 加大字号
            fontweight='bold',  # 加粗
            verticalalignment='center',
            horizontalalignment='center',
            color='#2C3E50',
            zorder=2,  # 确保文本在背景框之上
            family='SimHei'
        )
        
        # 暂停/继续按钮区域
        self.ax_pause = self.fig.add_axes([0.85, 0.95, 0.12, 0.04])
        self.ax_pause.set_facecolor('#E6F3FF')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.animation_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 当前动画对象
        self.animation = None
        self.frames = []
        self.current_frame = 0
        
        # 默认矩阵
        self.default_matrix = np.array([[2, 1, -1, 8],
                                        [-3, -1, 2, -11],
                                        [-2, 1, 2, -3]], dtype=float)
        
        # 暂停/继续按钮
        self.pause_button = Button(
            self.ax_pause, 
            "暂停",
            color='#4A90E2',
            hovercolor='#357ABD'
        )
        self.pause_button.on_clicked(self.pause_handler)
        
        # 手动设置按钮文本的样式
        self.pause_button.label.set_fontfamily('SimHei')
        self.pause_button.label.set_fontsize(10)
        self.pause_button.label.set_weight('bold')
        self.pause_button.label.set_color('white')
        
        self.paused = False
        
        # 添加必要的初始化变量
        self.padding = 0.1  # 文本框内边距
        self.current_description = ""  # 当前显示的描述文本
        self.text_animation_speed = 0.02  # 文本动画速度
        self.chars_per_frame = 3  # 每帧显示的字符数
    
    def use_default_matrix(self):
        """使用默认矩阵"""
        self.matrix_text.delete(1.0, tk.END)
        rows, cols = self.default_matrix.shape
        self.matrix_text.insert(tk.END, f"{rows} {cols}\n")
        # 格式化输出默认矩阵，保留两位小数
        for row in self.default_matrix:
            row_str = " ".join([f"{x:.2f}" for x in row])
            self.matrix_text.insert(tk.END, row_str + "\n")
        
        # 更新大小选择器
        self.row_var.set(str(rows))
        self.col_var.set(str(cols))
    
    def input_matrix(self):
        matrix_str = self.matrix_text.get(1.0, tk.END).strip()
        if not matrix_str:
            return self.default_matrix
        
        lines = matrix_str.split("\n")
        if len(lines) < 1:
            return self.default_matrix
        
        # 第一行是行列数
        first_line = lines[0].split()
        if len(first_line) != 2:
            messagebox.showerror("输入错误", "第一行必须包含两个数字，表示矩阵的行数和列数！")
            return None
        
        try:
            m, n = int(first_line[0]), int(first_line[1])
        except ValueError:
            messagebox.showerror("输入错误", "第一行必须包含两个整数，表示矩阵的行数和列数！")
            return None
        
        if len(lines) - 1 != m:
            messagebox.showerror("输入错误", f"矩阵行数应为 {m} 行，但实际输入了 {len(lines)-1} 行！")
            return None
        
        mat = []
        for i in range(1, len(lines)):
            row = lines[i].split()
            if len(row) != n:
                messagebox.showerror("输入错误", f"第 {i} 行元素个数应为 {n} 个，但实际输入了 {len(row)} 个！")
                return None
            try:
                mat.append(list(map(float, row)))
            except ValueError:
                messagebox.showerror("输入错误", f"第 {i} 行包含非数字元素！")
                return None
        
        return np.array(mat, dtype=float)
    
    def style_table(self, table):
        """美化表格样式"""
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        
        # 设置表格样式
        for key, cell in table.get_celld().items():
            # 基础样式
            cell.set_linewidth(1.5)
            cell.set_edgecolor('#4A90E2')  # 蓝色边框
            cell.set_facecolor('white')
            cell.set_alpha(0.9)  # 略微透明
            
            # 设置文本样式
            text = cell.get_text()
            text.set_fontweight('bold')  # 文字加粗
            text.set_color('#2C3E50')    # 文字颜色
            
            # 设置单元格内边距
            cell.PAD = 0.3  # 增加内边距
            
            # 设置单元格对齐方式
            cell._loc = 'center'
            text.set_horizontalalignment('center')
            text.set_verticalalignment('center')
    
    def generate_gaussian_elimination_frames(self, A):
        frames = []
        mat = A.copy()
        m, n = mat.shape
        frames.append({
            'matrix': mat.copy(),
            'description': "初始矩阵\n这是原始输入矩阵，用于进行高斯消元。",
            'highlights': []
        })
        r = 0  # 当前主元所在行
        for c in range(n):
            if r >= m:
                break
            # 在当前列寻找非零主元
            pivot_row = None
            for i in range(r, m):
                if abs(mat[i, c]) > 1e-9:
                    pivot_row = i
                    break
            if pivot_row is None:
                continue  # 此列无非零元，跳过
            # 标示选取主元
            frames.append({
                'matrix': mat.copy(),
                'description': f"选取主元：第 {pivot_row+1} 行 第 {c+1} 列\n" + 
                             f"数值 {mat[pivot_row, c]:.2f}\n" +
                             "选取非零主元，确保该列有效数据用于后续归一化和消元。",
                'highlights': [('cell', (pivot_row, c), '#ff9999')]
            })
            # 行交换（若主元所在行不是当前行 r，则交换）
            if pivot_row != r:
                frames.append({
                    'matrix': mat.copy(),
                    'description': f"交换第 {r+1} 行与第 {pivot_row+1} 行\n意义：将含有非零主元的行移至上方，避免零除错误。",
                    'highlights': [('row', r, '#ffff99'), ('row', pivot_row, '#ffff99')]
                })
                mat[[r, pivot_row], :] = mat[[pivot_row, r], :]
                frames.append({
                    'matrix': mat.copy(),
                    'description': "行交换后矩阵\n意义：交换完成后，主元位于正确位置，可进行归一化。",
                    'highlights': [('row', r, '#ffff99'), ('row', pivot_row, '#ffff99')]
                })
            # 归一化：将主元所在行乘以因子，使主元变为 1
            pivot_val = mat[r, c]
            if abs(pivot_val - 1) > 1e-9:
                scale = 1 / pivot_val
                frames.append({
                    'matrix': mat.copy(),
                    'description': f"归一化第 {r+1} 行：乘以 {scale:.2f}\n意义：归一化之后，该行主元置为 1，便于后续消元。",
                    'highlights': [('row', r, '#99ccff'), ('cell', (r, c), '#ff9999')]
                })
                mat[r, :] = mat[r, :] * scale
                frames.append({
                    'matrix': mat.copy(),
                    'description': f"归一化后第 {r+1} 行主元为 1\n意义：归一化完成，主元标准化后即可用于消元。",
                    'highlights': [('row', r, '#99ccff'), ('cell', (r, c), '#ff9999')]
                })
            # 消元：用当前主元所在行将下面各行该列的元素消去
            for i in range(r + 1, m):
                factor = mat[i, c]
                if abs(factor) > 1e-9:
                    frames.append({
                        'matrix': mat.copy(),
                        'description': f"利用第 {r+1} 行消去第 {i+1} 行第 {c+1} 列元素（倍数 {factor:.2f}）\n意义：通过消元，使该列下所有元素归零，构造上三角矩阵。",
                        'highlights': [('row', r, '#99ccff'),
                                       ('row', i, '#b3ffb3'),
                                       ('cell', (r, c), '#ff9999'),
                                       ('cell', (i, c), '#ffcc99')]
                    })
                    mat[i, :] = mat[i, :] - factor * mat[r, :]
                    frames.append({
                        'matrix': mat.copy(),
                        'description': f"消元后更新第 {i+1} 行\n意义：经过消元，第 {i+1} 行在该列元素置为 0，矩阵逐步形成行阶梯形。",
                        'highlights': [('row', i, '#b3ffb3')]
                    })
            r += 1

        # 计算矩阵秩：非零行的数量
        rank = 0
        for i in range(m):
            if np.any(np.abs(mat[i, :]) > 1e-9):
                rank += 1
        frames.append({
            'matrix': mat.copy(),
            'description': f"最终行阶梯形矩阵；矩阵秩为 {rank}\n意义：矩阵秩表示线性无关（非零）行的数目，反映矩阵的有效维度。",
            'highlights': []
        })
        return frames
    
    def reset_animation(self):
        """重置动画状态，准备接受新的输入"""
        # 停止当前动画
        if self.animation:
            self.animation._stop()
            self.animation = None
        
        # 清除表格
        self.ax_table.clear()
        self.ax_table.axis('off')
        
        # 清除说明文本
        self.log_text.set_text("")
        
        # 启用所有输入控件
        self.matrix_text.config(state='normal')
        self.random_button.config(state='normal')
        self.default_button.config(state='normal')
        self.submit_button.config(state='normal')
        self.row_var.set("3")
        self.col_var.set("4")
        
        # 禁用重新输入按钮
        self.reset_button.config(state='disabled')
        
        # 重绘画布
        self.canvas.draw()

    def generate_animation(self):
        A = self.input_matrix()
        if A is None:
            return
        
        try:
            # 禁用输入控件
            self.matrix_text.config(state='disabled')
            self.random_button.config(state='disabled')
            self.default_button.config(state='disabled')
            self.submit_button.config(state='disabled')
            
            # 启用重新输入按钮
            self.reset_button.config(state='normal')
            
            self.frames = self.generate_gaussian_elimination_frames(A)
            m, n = A.shape
            
            # 清除之前的表格（如果存在）
            self.ax_table.clear()
            self.ax_table.axis('off')
            
            # 构建初始矩阵对应的 Table
            initial_mat = self.frames[0]['matrix']
            cell_text = [[f"{initial_mat[i, j]:.2f}" for j in range(n)] for i in range(m)]
            
            # 设置单元格宽度
            colWidths = [0.15] * n  # 统一列宽
            
            # 创建表格并设置样式（移除 rowHeights 参数）
            self.table = self.ax_table.table(
                cellText=cell_text,
                cellLoc='center',
                loc='center',
                edges='closed',
                colWidths=colWidths
            )
            self.style_table(self.table)
            
            # 调整表格整体大小和位置
            self.table.scale(1.2, 1.5)  # 放大表格
            
            self.log_text.set_text(self.frames[0]['description'])
            
            # 清除之前的动画
            if self.animation:
                self.animation._stop()
            
            self.current_frame = 0
            self.paused = False
            self.pause_button.label.set_text("暂停")
            
            # 创建新动画
            self.animation = FuncAnimation(
                self.fig, 
                self.update, 
                frames=len(self.frames), 
                interval=2000,
                blit=False, 
                repeat=False,
                cache_frame_data=False
            )
            
            # 添加动画完成事件处理
            def on_animation_complete(event):
                if event.source is self.animation:
                    self.reset_button.config(state='normal')
            
            self.animation._start()
            self.fig.canvas.mpl_connect('draw_event', on_animation_complete)
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"生成动画时发生错误：{str(e)}")
            self.reset_animation()  # 发生错误时重置状态
    
    def update(self, frame_index):
        if frame_index >= len(self.frames):
            return []
        
        frame = self.frames[frame_index]
        mat = frame['matrix']
        m, n = mat.shape
        
        # 更新表格内容
        for i in range(m):
            for j in range(n):
                cell = self.table[(i, j)]
                cell.get_text().set_text(f"{mat[i, j]:.2f}")
                cell.set_facecolor('white')
                cell.set_alpha(0.9)
        
        # 优化高亮效果
        highlight_colors = {
            '#ff9999': '#FF9999',  # 红色
            '#ffff99': '#FFFFC2',  # 黄色
            '#99ccff': '#99CCFF',  # 蓝色
            '#b3ffb3': '#B3FFB3',  # 绿色
        }
        
        # 处理高亮效果
        for hl in frame['highlights']:
            if hl[0] == 'cell':
                (i, j), color = hl[1], highlight_colors.get(hl[2], hl[2])
                try:
                    cell = self.table[(i, j)]
                    # 使用正弦函数创建平滑的渐变效果
                    progress = (np.sin(2 * np.pi * frame_index / 20) + 1) / 2
                    color_rgba = plt.matplotlib.colors.to_rgba(color)
                    alpha = 0.4 + 0.5 * progress
                    cell.set_facecolor(color_rgba)
                    cell.set_alpha(alpha)
                except KeyError:
                    pass
            elif hl[0] == 'row':
                i, color = hl[1], highlight_colors.get(hl[2], hl[2])
                for j in range(n):
                    try:
                        cell = self.table[(i, j)]
                        cell.set_facecolor(color)
                        cell.set_alpha(0.7)
                    except KeyError:
                        pass
        
        # 优化文本动画效果
        if frame_index == 0 or self.current_description != frame['description']:
            self.current_description = frame['description']
            
            # 直接设置文本，不使用逐字动画以提高性能
            self.log_text.set_text(self.current_description)
            
            # 更新背景框
            bbox = self.log_text.get_window_extent()
            text_width = bbox.width / self.fig.dpi
            text_height = bbox.height / self.fig.dpi
            
            # 设置背景框大小
            self.description_box.set_bounds(
                0.5 - (text_width/2 + self.padding),
                0.5 - (text_height/2 + self.padding),
                text_width + 2*self.padding,
                text_height + 2*self.padding
            )
        
        return [self.description_box, self.log_text] + list(self.table.get_children())
    
    def pause_handler(self, event):
        if self.animation is None:
            return
        
        if self.paused:
            self.animation.event_source.start()
            self.pause_button.label.set_text("暂停")
            self.paused = False
        else:
            self.animation.event_source.stop()
            self.pause_button.label.set_text("继续")
            self.paused = True

    def update_matrix_size(self):
        """更新矩阵大小时的回调函数"""
        try:
            rows = int(self.row_var.get())
            cols = int(self.col_var.get())
            if rows > 0 and cols > 0:
                self.matrix_text.delete(1.0, tk.END)
                # 首先写入矩阵大小
                self.matrix_text.insert(tk.END, f"{rows} {cols}\n")
                # 然后添加格式化的零矩阵
                for i in range(rows):
                    row_str = " ".join(["0.00" for _ in range(cols)])
                    self.matrix_text.insert(tk.END, row_str + "\n")
        except ValueError:
            pass

    def generate_random_matrix(self):
        """生成随机矩阵"""
        try:
            rows = int(self.row_var.get())
            cols = int(self.col_var.get())
            if rows > 0 and cols > 0:
                # 生成-10到10之间的随机矩阵
                random_matrix = np.random.uniform(-10, 10, size=(rows, cols))
                # 更新输入框
                self.matrix_text.delete(1.0, tk.END)
                self.matrix_text.insert(tk.END, f"{rows} {cols}\n")
                # 格式化输出，保留两位小数
                for row in random_matrix:
                    row_str = " ".join([f"{x:.2f}" for x in row])
                    self.matrix_text.insert(tk.END, row_str + "\n")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的矩阵大小！")

    def create_theory_frame(self):
        """创建高斯消元法理论知识讲解框架"""
        # 创建一个新的顶层窗口
        self.theory_window = tk.Toplevel(self.master)
        self.theory_window.title("高斯消元法知识点")
        self.theory_window.geometry("700x600")
        self.theory_window.configure(bg="#f0f0f0")
        
        # 创建一个框架来包含所有内容
        main_frame = ttk.Frame(self.theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="高斯消元法原理与应用", 
                              font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件以组织不同部分的内容
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
        # 步骤选项卡
        steps_frame = ttk.Frame(notebook, padding=10)
        notebook.add(steps_frame, text="解题步骤")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用场景")
        
        # 填充基本概念选项卡内容
        self._create_concept_content(concept_frame)
        
        # 填充步骤选项卡内容
        self._create_steps_content(steps_frame)
        
        # 填充应用选项卡内容
        self._create_application_content(application_frame)
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                                command=self.theory_window.destroy)
        close_button.pack(pady=10)

    def _create_concept_content(self, parent_frame):
        """创建基本概念选项卡的内容"""
        # 创建可滚动文本区域
        text_frame = ttk.Frame(parent_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SimHei", 12), 
                          padx=10, pady=10, bg="#ffffff")
        scrollbar = ttk.Scrollbar(text_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加基本概念内容
        concept_text = """
高斯消元法是一种用于求解线性方程组的算法，也常用于计算矩阵的行列式、求逆矩阵和求解矩阵的秩。该方法以德国数学家卡尔·弗里德里希·高斯命名。

基本原理：
高斯消元法的核心思想是通过一系列的初等行变换，将系数矩阵转化为上三角矩阵或行阶梯形矩阵。这些变换包括：
1. 交换两行的位置
2. 用一个非零常数乘以某一行
3. 将某一行的倍数加到另一行

矩阵的三种初等行变换不改变线性方程组的解，但可以简化求解过程。通过系统应用这些变换，我们可以将复杂的线性方程组转化为等价但更容易求解的形式。

高斯消元法与高斯-约当消元法：
- 高斯消元法将矩阵化为上三角形式
- 高斯-约当消元法进一步将矩阵化为对角形式或简化的行阶梯形式

计算复杂度：
对于一个n×n的矩阵，高斯消元法的时间复杂度为O(n³)。
        """
        
        text_area.insert(tk.END, concept_text)
        text_area.config(state=tk.DISABLED)  # 设为只读

    def _create_steps_content(self, parent_frame):
        """创建解题步骤选项卡的内容"""
        # 创建可滚动文本区域
        text_frame = ttk.Frame(parent_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SimHei", 12), 
                          padx=10, pady=10, bg="#ffffff")
        scrollbar = ttk.Scrollbar(text_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加解题步骤内容
        steps_text = """
高斯消元法的基本步骤：

1. 前向消元过程：
   a) 找出第一列中绝对值最大的元素（主元），将其所在行交换到第一行（部分主元消去法）
   b) 用第一行将下面所有行的第一个元素消为零
   c) 对剩余的n-1行n-1列子矩阵重复上述过程

2. 回代求解过程：
   a) 从最后一个非零行开始
   b) 依次代入已知解，求解各个未知数

以三元线性方程组为例：
ax + by + cz = d
ex + fy + gz = h
ix + jy + kz = l

步骤详解：
1. 将方程组写成增广矩阵形式：
   [a b c | d]
   [e f g | h]
   [i j k | l]

2. 选取第一列中绝对值最大的元素作为主元，假设是'a'
   - 如果需要，交换行的位置使'a'在第一行

3. 用第一行消去第二行和第三行中的第一个元素：
   - 第二行 = 第二行 - (e/a) × 第一行
   - 第三行 = 第三行 - (i/a) × 第一行

4. 对剩余的2×2子矩阵重复操作，选取第二列中绝对值最大的元素作为主元
   - 用包含主元的行消去另一行中对应位置的元素

5. 最终得到上三角形式：
   [a b c | d]
   [0 f' g'| h']
   [0 0 k''| l'']

6. 从最后一行开始回代求解：
   z = l''/k''
   y = (h' - g'z)/f'
   x = (d - by - cz)/a

注意事项：
- 如果在消元过程中遇到主元为零，需要寻找非零元素所在行进行交换
- 如果某一列全为零，对应的变量为自由变量
- 如果方程组有无穷多解或无解，会在增广矩阵中反映出来
        """
        
        text_area.insert(tk.END, steps_text)
        text_area.config(state=tk.DISABLED)  # 设为只读

    def _create_application_content(self, parent_frame):
        """创建应用场景选项卡的内容"""
        # 创建可滚动文本区域
        text_frame = ttk.Frame(parent_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SimHei", 12), 
                          padx=10, pady=10, bg="#ffffff")
        scrollbar = ttk.Scrollbar(text_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加应用场景内容
        application_text = """
高斯消元法在科学和工程领域有广泛的应用：

1. 线性方程组求解
   - 电路分析：使用基尔霍夫定律设立方程组，求解电路中的电流和电压
   - 结构分析：计算桁架结构中各杆件的受力情况
   - 流体力学：求解流体流动方程

2. 矩阵运算
   - 计算矩阵的行列式
   - 求解矩阵的逆矩阵
   - 计算矩阵的秩
   - 线性方程组的最小二乘解

3. 数值分析
   - 插值计算中的系数确定
   - 有限元分析中的刚度矩阵求解
   - 边值问题的数值解法

4. 计算机图形学
   - 几何变换矩阵的计算
   - 视图变换
   - 透视投影

5. 机器学习和数据分析
   - 线性回归中的参数求解
   - 主成分分析
   - 最小二乘拟合

6. 密码学
   - 线性密码的分析和破解
   - 某些加密算法中的矩阵运算

高斯消元法是线性代数中最基础也是最重要的算法之一，掌握它对理解更高级的数学概念和算法至关重要。在计算机实现中，通常会采用改进的算法如LU分解等来提高效率和数值稳定性。
        """
        
        text_area.insert(tk.END, application_text)
        text_area.config(state=tk.DISABLED)  # 设为只读

    def show_theory(self):
        """显示高斯消元法理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 高斯消元法知识点内容
            sections = {
                "基本概念": """
高斯消元法是一种用于求解线性方程组的算法，也常用于计算矩阵的行列式、求逆矩阵和求解矩阵的秩。该方法以德国数学家卡尔·弗里德里希·高斯命名。

基本原理：
高斯消元法的核心思想是通过一系列的初等行变换，将系数矩阵转化为上三角矩阵或行阶梯形矩阵。这些变换包括：
1. 交换两行的位置
2. 用一个非零常数乘以某一行
3. 将某一行的倍数加到另一行

矩阵的三种初等行变换不改变线性方程组的解，但可以简化求解过程。通过系统应用这些变换，我们可以将复杂的线性方程组转化为等价但更容易求解的形式。

高斯消元法与高斯-约当消元法：
- 高斯消元法将矩阵化为上三角形式
- 高斯-约当消元法进一步将矩阵化为对角形式或简化的行阶梯形式

计算复杂度：
对于一个n×n的矩阵，高斯消元法的时间复杂度为O(n³)。
""",
                "几何意义": """
在几何视角下，高斯消元法对应于对线性方程组的几何结构进行变换：

方程的几何解释：
1. 在二维空间中，每个方程表示一条直线，解为直线的交点。
2. 在三维空间中，每个方程表示一个平面，解为平面的交线或交点。
3. 更高维空间中，方程对应超平面的交集。

行变换的几何意义：
1. 交换行：调整方程的顺序，不改变解集。
2. 行缩放：将方程的系数和常数项按比例缩放，解集不变。
3. 行相加：用两个方程的线性组合替代原方程，保持解集不变。

行阶梯形的几何含义：
行阶梯形矩阵对应于将原方程组转化为 “上三角” 结构，每一步消元相当于固定一个变量，将问题降维。
""",
                "计算方法": """
高斯消元法的基本步骤：

1. 前向消元过程：
   a) 找出第一列中绝对值最大的元素（主元），将其所在行交换到第一行（部分主元消去法）
   b) 用第一行将下面所有行的第一个元素消为零
   c) 对剩余的n-1行n-1列子矩阵重复上述过程

2. 回代求解过程：
   a) 从最后一个非零行开始
   b) 依次代入已知解，求解各个未知数

以三元线性方程组为例：
ax + by + cz = d
ex + fy + gz = h
ix + jy + kz = l

步骤详解：
1. 将方程组写成增广矩阵形式：
   [a b c | d]
   [e f g | h]
   [i j k | l]

2. 选取第一列中绝对值最大的元素作为主元，假设是'a'
   - 如果需要，交换行的位置使'a'在第一行

3. 用第一行消去第二行和第三行中的第一个元素：
   - 第二行 = 第二行 - (e/a) × 第一行
   - 第三行 = 第三行 - (i/a) × 第一行

4. 对剩余的2×2子矩阵重复操作，选取第二列中绝对值最大的元素作为主元
   - 用包含主元的行消去另一行中对应位置的元素

5. 最终得到上三角形式：
   [a b c | d]
   [0 f' g'| h']
   [0 0 k''| l'']

6. 从最后一行开始回代求解：
   z = l''/k''
   y = (h' - g'z)/f'
   x = (d - by - cz)/a

注意事项：
- 如果在消元过程中遇到主元为零，需要寻找非零元素所在行进行交换
- 如果某一列全为零，对应的变量为自由变量
- 如果方程组有无穷多解或无解，会在增广矩阵中反映出来
""",
                "应用": """
1. 线性方程组求解
   - 电路分析：使用基尔霍夫定律设立方程组，求解电路中的电流和电压
   - 结构分析：计算桁架结构中各杆件的受力情况
   - 流体力学：求解流体流动方程

2. 矩阵运算
   - 计算矩阵的行列式
   - 求解矩阵的逆矩阵
   - 计算矩阵的秩
   - 线性方程组的最小二乘解

3. 数值分析
   - 插值计算中的系数确定
   - 有限元分析中的刚度矩阵求解
   - 边值问题的数值解法

4. 计算机图形学
   - 几何变换矩阵的计算
   - 视图变换
   - 透视投影

5. 机器学习和数据分析
   - 线性回归中的参数求解
   - 主成分分析
   - 最小二乘拟合

6. 密码学
   - 线性密码的分析和破解
   - 某些加密算法中的矩阵运算

高斯消元法是线性代数中最基础也是最重要的算法之一，掌握它对理解更高级的数学概念和算法至关重要。在计算机实现中，通常会采用改进的算法如LU分解等来提高效率和数值稳定性。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "高斯消元法理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建高斯消元法理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("高斯消元法理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="高斯消元法理论知识", 
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

if __name__ == "__main__":
    root = tk.Tk()
    app = GaussianEliminationApp(root)
    root.mainloop()