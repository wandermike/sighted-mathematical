import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # 明确指定后端，避免冲突
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
import matplotlib.animation as animation
from matplotlib.font_manager import FontProperties  # 添加字体支持

# 设置中文字体
try:
    # 尝试加载Microsoft YaHei或SimHei字体
    font_path = matplotlib.font_manager.findfont(matplotlib.font_manager.FontProperties(family='SimHei'))
    chinese_font = FontProperties(fname=font_path)
    matplotlib.rcParams['font.family'] = ['sans-serif']
    # 添加字体路径确保跨平台支持
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'STSong', 'FangSong', 'Arial Unicode MS'] 
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except:
    # 如果无法加载中文字体，设置回退选项
    chinese_font = FontProperties()
    print("警告：无法加载中文字体，可能导致显示问题")

class DeterminantApp:
    def __init__(self, master):
        self.master = master
        self.master.title("行列式可视化")
        self.master.geometry("1200x800")
        self.master.configure(bg="#E6F3FF")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.master, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 创建右侧绘图区域
        self.plot_frame = ttk.Frame(self.main_frame, padding=10)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建行列式输入区
        self.create_matrix_input()
        
        # 创建操作按钮
        self.create_action_buttons()
        
        # 创建可视化类型选择
        self.create_visualization_options()
        
        # 创建绘图区
        self.create_plot_area()
        
        # 初始化变量
        self.matrix_size = 2
        self.animation_speed = 0.5
        self.current_animation = None
        self.step_text = tk.StringVar(value="")
        self.ani = None  # 添加初始化动画属性
        
        # 创建说明标签
        self.result_label = ttk.Label(self.plot_frame, text="行列式值: ", font=("SimHei", 12))
        self.result_label.pack(side=tk.BOTTOM, pady=10)
        
        self.explanation_text = tk.Text(self.plot_frame, height=5, width=50, wrap=tk.WORD, font=("SimHei", 10))
        self.explanation_text.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.explanation_text.insert(tk.END, "行列式几何意义：表示由矩阵列向量构成的平行四边形/平行六面体的有向面积/体积。\n计算中请观察基向量的变换过程。")
        self.explanation_text.config(state=tk.DISABLED)
        
        # 步骤显示
        self.step_label = ttk.Label(self.plot_frame, textvariable=self.step_text, font=("SimHei", 12))
        self.step_label.pack(side=tk.BOTTOM, pady=5)
        
        # 设置默认矩阵
        self.reset_matrix_to_identity()
        
        # 添加返回主菜单按钮，方便与main.py集成
        return_button = ttk.Button(
            self.control_frame, 
            text="返回主菜单", 
            command=self.master.destroy
        )
        return_button.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
    # 添加与main.py集成所需的方法
    def close_current_window(self):
        """支持与主程序的集成，关闭当前打开的窗口"""
        if hasattr(self, 'ani') and self.ani:
            self.ani.event_source.stop()
        if hasattr(self, 'current_window') and self.current_window:
            self.current_window.destroy()
    
    def create_matrix_input(self):
        """创建矩阵输入区域"""
        matrix_frame = ttk.LabelFrame(self.control_frame, text="矩阵输入", padding=10)
        matrix_frame.pack(fill=tk.X, pady=10)
        
        # 矩阵大小选择
        size_frame = ttk.Frame(matrix_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="矩阵大小:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.StringVar(value="2")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, values=["2", "3"], width=5)
        size_combo.pack(side=tk.LEFT, padx=5)
        size_combo.bind("<<ComboboxSelected>>", self.change_matrix_size)
        
        # 矩阵输入框架
        self.matrix_input_frame = ttk.Frame(matrix_frame)
        self.matrix_input_frame.pack(fill=tk.X, pady=10)
        
        # 初始化2x2矩阵输入
        self.matrix_entries = []
        self.update_matrix_entries(2)
    
    def update_matrix_entries(self, size):
        """更新矩阵输入框"""
        # 清除现有的输入框
        for row in self.matrix_entries:
            for entry in row:
                entry.destroy()
        
        # 创建新的输入框
        self.matrix_entries = []
        for i in range(size):
            row_entries = []
            row_frame = ttk.Frame(self.matrix_input_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            for j in range(size):
                entry = ttk.Entry(row_frame, width=5)
                entry.pack(side=tk.LEFT, padx=5)
                entry.insert(0, "1" if i == j else "0")  # 默认为单位矩阵
                row_entries.append(entry)
            
            self.matrix_entries.append(row_entries)
    
    def change_matrix_size(self, event=None):
        """更改矩阵大小"""
        try:
            new_size = int(self.size_var.get())
            if new_size in [2, 3]:
                self.matrix_size = new_size
                self.update_matrix_entries(new_size)
        except ValueError:
            pass
    
    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 计算行列式按钮
        calculate_button = ttk.Button(
            button_frame, 
            text="计算行列式", 
            command=self.calculate_determinant
        )
        calculate_button.pack(fill=tk.X, pady=5)
        
        # 动画展示按钮
        visualize_button = ttk.Button(
            button_frame, 
            text="动画展示", 
            command=self.visualize_determinant
        )
        visualize_button.pack(fill=tk.X, pady=5)
        
        # 重置按钮
        reset_button = ttk.Button(
            button_frame, 
            text="重置为单位矩阵", 
            command=self.reset_matrix_to_identity
        )
        reset_button.pack(fill=tk.X, pady=5)
        
        # 随机矩阵按钮
        random_button = ttk.Button(
            button_frame, 
            text="生成随机矩阵", 
            command=self.generate_random_matrix
        )
        random_button.pack(fill=tk.X, pady=5)
        
        # 步骤解析按钮
        steps_button = ttk.Button(
            button_frame, 
            text="逐步计算过程", 
            command=self.step_by_step_calculation
        )
        steps_button.pack(fill=tk.X, pady=5)
        
        # 添加理论知识按钮
        theory_button = ttk.Button(
            button_frame, 
            text="行列式理论知识", 
            command=self.show_theory
        )
        theory_button.pack(fill=tk.X, pady=5)
    
    def create_visualization_options(self):
        """创建可视化选项"""
        viz_frame = ttk.LabelFrame(self.control_frame, text="可视化选项", padding=10)
        viz_frame.pack(fill=tk.X, pady=10)
        
        # 动画速度
        speed_frame = ttk.Frame(viz_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="动画速度:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=1.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 高级选项
        advanced_frame = ttk.Frame(viz_frame)
        advanced_frame.pack(fill=tk.X, pady=5)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        grid_check = ttk.Checkbutton(advanced_frame, text="显示网格", 
                                    variable=self.show_grid_var)
        grid_check.pack(side=tk.LEFT, padx=5)
        
        self.show_vectors_var = tk.BooleanVar(value=True)
        vectors_check = ttk.Checkbutton(advanced_frame, text="显示向量", 
                                       variable=self.show_vectors_var)
        vectors_check.pack(side=tk.LEFT, padx=5)
    
    def create_plot_area(self):
        """创建绘图区域，支持无限缩放和平移"""
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # 设置默认视图范围
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        
        # 添加坐标轴
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # 标记坐标轴
        self.ax.set_xlabel('X轴', fontproperties=chinese_font)
        self.ax.set_ylabel('Y轴', fontproperties=chinese_font)
        self.ax.set_title('行列式几何可视化', fontproperties=chinese_font)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加增强的导航工具栏
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        
        # 创建自定义工具栏类以增强缩放功能
        class EnhancedNavigationToolbar(NavigationToolbar2Tk):
            def __init__(self, canvas, window):
                super().__init__(canvas, window)
                
                # 添加复位按钮
                self.reset_button = ttk.Button(self, text="复位视图", command=self.reset_view)
                self.reset_button.pack(side=tk.LEFT, padx=2)
                
                # 添加自适应按钮
                self.auto_button = ttk.Button(self, text="自适应矩阵", command=self.auto_adjust)
                self.auto_button.pack(side=tk.LEFT, padx=2)
                
                # 存储父类引用以访问主应用实例
                self.parent_app = None
            
            def reset_view(self):
                """重置视图到默认范围"""
                self.canvas.figure.axes[0].set_xlim(-5, 5)
                self.canvas.figure.axes[0].set_ylim(-5, 5)
                self.canvas.figure.axes[0].set_aspect('equal')
                self.canvas.draw_idle()
            
            def auto_adjust(self):
                """自动调整视图以适应当前矩阵"""
                if self.parent_app:
                    try:
                        matrix = self.parent_app.get_matrix_from_entries()
                        if matrix is not None:
                            # 找出矩阵的最大绝对值
                            if self.parent_app.matrix_size == 2:
                                v1 = np.array([matrix[0, 0], matrix[1, 0]])
                                v2 = np.array([matrix[0, 1], matrix[1, 1]])
                                max_val = max(np.max(np.abs(v1)), np.max(np.abs(v2)), 1)
                            else:  # 3x3
                                v1 = np.array([matrix[0, 0], matrix[1, 0], matrix[2, 0]])
                                v2 = np.array([matrix[0, 1], matrix[1, 1], matrix[2, 1]])
                                v3 = np.array([matrix[0, 2], matrix[1, 2], matrix[2, 2]])
                                max_val = max(np.max(np.abs(v1)), np.max(np.abs(v2)), 
                                             np.max(np.abs(v3)), 1)
                            
                            # 设置比最大值稍大的范围，添加20%的边距
                            margin = max_val * 0.2
                            ax = self.canvas.figure.axes[0]
                            ax.set_xlim(-max_val-margin, max_val+margin)
                            ax.set_ylim(-max_val-margin, max_val+margin)
                            self.canvas.draw_idle()
                    except Exception as e:
                        messagebox.showerror("视图调整错误", f"无法调整视图: {str(e)}")
        
        # 创建增强工具栏
        self.toolbar = EnhancedNavigationToolbar(self.canvas, self.plot_frame)
        # 设置父应用引用
        self.toolbar.parent_app = self
        self.toolbar.update()
        
        # 设置缩放和平移事件处理
        self.setup_scroll_zoom()
    
    def setup_scroll_zoom(self):
        """设置鼠标滚轮缩放和拖动平移，支持2D和3D视图"""
        def on_scroll(event):
            # 只处理滚轮在绘图区域内的事件
            if event.inaxes != self.ax:
                return
            
            # 获取当前视图
            event.canvas.figure
            
            # 检测是2D还是3D视图
            is_3d = hasattr(self.ax, 'get_proj')
            
            if is_3d:
                # 3D视图的缩放
                # 获取当前视图范围
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                z_min, z_max = self.ax.get_zlim()
                
                # 缩放因子
                scale_factor = 1.2 if event.button == 'up' else 1/1.2
                
                # 计算新范围 - 确保保持中心点
                x_center = (x_min + x_max) / 2
                y_center = (y_min + y_max) / 2
                z_center = (z_min + z_max) / 2
                
                new_width = (x_max - x_min) / scale_factor
                new_height = (y_max - y_min) / scale_factor
                new_depth = (z_max - z_min) / scale_factor
                
                # 设置新视图 - 确保同时缩放所有三个轴
                self.ax.set_xlim(x_center - new_width/2, x_center + new_width/2)
                self.ax.set_ylim(y_center - new_height/2, y_center + new_height/2)
                self.ax.set_zlim(z_center - new_depth/2, z_center + new_depth/2)
            else:
                # 2D视图的缩放
                # 获取当前视图范围
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                
                # 缩放因子
                scale_factor = 1.2 if event.button == 'up' else 1/1.2
                
                # 计算鼠标位置为中心的新视图范围
                x_center = event.xdata
                y_center = event.ydata
                
                # 计算新范围
                new_width = (x_max - x_min) / scale_factor
                new_height = (y_max - y_min) / scale_factor
                
                # 设置新视图
                self.ax.set_xlim(x_center - new_width/2, x_center + new_width/2)
                self.ax.set_ylim(y_center - new_height/2, y_center + new_height/2)
            
            # 重绘画布
            self.canvas.draw_idle()
        
        # 连接滚轮事件
        self.canvas.mpl_connect('scroll_event', on_scroll)
        
        # 添加3D旋转视图增强功能
        def on_mouse_move(event):
            # 只有在3D视图中才处理视角旋转
            if not hasattr(self.ax, 'get_proj'):
                return
            
            # 仅处理按下右键并移动的情况
            if event.button != 3:  # 3代表右键
                return
            
            # 获取鼠标移动距离，调整视角
            dx = event.x - getattr(self, '_last_mouse_x', event.x)
            dy = event.y - getattr(self, '_last_mouse_y', event.y)
            
            # 保存当前鼠标位置
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            
            # 调整方位角和仰角
            current_azim = self.ax.azim
            current_elev = self.ax.elev
            
            # 根据鼠标移动改变视角
            new_azim = current_azim + dx
            new_elev = current_elev - dy
            
            # 限制仰角范围，防止视图翻转
            if new_elev > 90:
                new_elev = 90
            elif new_elev < -90:
                new_elev = -90
            
            # 设置新视角
            self.ax.view_init(elev=new_elev, azim=new_azim)
            self.canvas.draw_idle()
        
        # 保存鼠标按下状态
        def on_mouse_press(event):
            if hasattr(self.ax, 'get_proj'):
                self._last_mouse_x = event.x
                self._last_mouse_y = event.y
        
        # 连接鼠标事件
        self.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        self.canvas.mpl_connect('button_press_event', on_mouse_press)
    
    def _limit_matrix_values(self, matrix, max_value=10):
        """限制矩阵值大小，防止视图超出范围"""
        if np.max(np.abs(matrix)) > max_value:
            scale_factor = max_value / np.max(np.abs(matrix))
            limited_matrix = matrix * scale_factor
            messagebox.showinfo("矩阵缩放", 
                               f"矩阵值过大，已自动缩放为原来的 {scale_factor:.2f} 倍以确保显示效果")
            return limited_matrix
        return matrix
    
    def get_matrix_from_entries(self):
        """从输入框获取矩阵并限制其范围"""
        matrix = []
        for i in range(self.matrix_size):
            row = []
            for j in range(self.matrix_size):
                try:
                    value = float(self.matrix_entries[i][j].get())
                    row.append(value)
                except ValueError:
                    messagebox.showerror("输入错误", f"位置 ({i+1},{j+1}) 的值无效，请输入数字")
                    return None
            matrix.append(row)
        
        # 转换为numpy数组并限制最大值
        matrix_array = np.array(matrix)
        return self._limit_matrix_values(matrix_array)
    
    def calculate_determinant(self):
        """计算并显示行列式的值"""
        matrix = self.get_matrix_from_entries()
        if matrix is not None:
            try:
                det_value = np.linalg.det(matrix)
                self.result_label.config(text=f"行列式值: {det_value:.4f}")
                
                # 更新解释文本
                self.update_explanation(matrix, det_value)
                
                # 绘制静态图形
                self.plot_determinant(matrix)
            except np.linalg.LinAlgError:
                messagebox.showerror("计算错误", "无法计算行列式，请检查矩阵是否有效")
    
    def update_explanation(self, matrix, det_value):
        """更新解释文本"""
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        
        if self.matrix_size == 2:
            self.explanation_text.insert(tk.END, 
                f"2x2矩阵行列式表示由两个列向量构成的平行四边形面积。\n"
                f"计算公式: {matrix[0,0]}*{matrix[1,1]} - {matrix[0,1]}*{matrix[1,0]} = {det_value:.4f}\n"
                f"行列式的正负代表平行四边形的方向（正值表示列向量按逆时针排列）。")
        else:  # 3x3
            self.explanation_text.insert(tk.END, 
                f"3x3矩阵行列式表示由三个列向量构成的平行六面体体积。\n"
                f"行列式值 {det_value:.4f} 的绝对值即为体积大小。\n"
                f"行列式的正负取决于三个向量构成的坐标系是否为右手系。")
        
        self.explanation_text.config(state=tk.DISABLED)
    
    def plot_determinant(self, matrix):
        """绘制行列式的静态可视化"""
        try:
            self.ax.clear()
            
            if self.matrix_size == 2:
                self.plot_2d_determinant(matrix)
            else:  # 3x3
                self.plot_3d_determinant(matrix)
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("绘图错误", f"无法绘制行列式: {str(e)}")
    
    def plot_2d_determinant(self, matrix):
        """绘制2D行列式可视化"""
        # 设置坐标轴范围，确保矩阵显示在视图内
        max_val = max(np.max(np.abs(matrix)), 5)  # 至少为5
        margin = max_val * 0.2  # 添加20%的边距
        self.ax.set_xlim(-max_val-margin, max_val+margin)
        self.ax.set_ylim(-max_val-margin, max_val+margin)
        self.ax.set_aspect('equal')
        
        # 绘制网格
        if self.show_grid_var.get():
            self.ax.grid(True)
        
        # 变换后的基向量
        v1 = np.array([matrix[0, 0], matrix[1, 0]])
        v2 = np.array([matrix[0, 1], matrix[1, 1]])
        
        # 绘制坐标轴
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # 绘制变换后的向量
        if self.show_vectors_var.get():
            self.ax.arrow(0, 0, v1[0], v1[1], head_width=max_val/25, head_length=max_val/25, 
                         fc='red', ec='red', label='向量1')
            self.ax.arrow(0, 0, v2[0], v2[1], head_width=max_val/25, head_length=max_val/25, 
                         fc='blue', ec='blue', label='向量2')
        
        # 绘制平行四边形
        vertices = np.array([[0, 0], v1, v1+v2, v2])
        poly = Polygon(vertices, alpha=0.3, facecolor='green', edgecolor='black')
        self.ax.add_patch(poly)
        
        # 标注行列式值
        det_value = np.linalg.det(matrix)
        self.ax.text(0.05, 0.95, f'行列式值: {det_value:.4f}', 
                    transform=self.ax.transAxes, fontsize=12, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                    fontproperties=chinese_font)  # 使用中文字体
        
        # 设置标题和标签 - 使用中文字体
        self.ax.set_title('2D行列式几何表示 - 平行四边形面积', fontproperties=chinese_font)
        self.ax.set_xlabel('X轴', fontproperties=chinese_font)
        self.ax.set_ylabel('Y轴', fontproperties=chinese_font)
        self.ax.legend(prop=chinese_font)
    
    def plot_3d_determinant(self, matrix):
        """绘制3D行列式可视化"""
        # 重新创建3D轴
        self.ax.remove()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # 变换后的基向量
        v1 = np.array([matrix[0, 0], matrix[1, 0], matrix[2, 0]])
        v2 = np.array([matrix[0, 1], matrix[1, 1], matrix[2, 1]])
        v3 = np.array([matrix[0, 2], matrix[1, 2], matrix[2, 2]])
        
        # 设置坐标范围
        max_range = max([np.max(np.abs(v1)), np.max(np.abs(v2)), np.max(np.abs(v3)), 5])
        margin = max_range * 0.2  # 添加20%的边距
        self.ax.set_xlim(-max_range-margin, max_range+margin)
        self.ax.set_ylim(-max_range-margin, max_range+margin)
        self.ax.set_zlim(-max_range-margin, max_range+margin)
        
        # 绘制坐标轴
        self.ax.plot([0, 0], [0, 0], [-max_range-margin, max_range+margin], 'k-', alpha=0.2)
        self.ax.plot([0, 0], [-max_range-margin, max_range+margin], [0, 0], 'k-', alpha=0.2)
        self.ax.plot([-max_range-margin, max_range+margin], [0, 0], [0, 0], 'k-', alpha=0.2)
        
        # 绘制基向量
        if self.show_vectors_var.get():
            self.ax.quiver(0, 0, 0, v1[0], v1[1], v1[2], color='r', label='向量1')
            self.ax.quiver(0, 0, 0, v2[0], v2[1], v2[2], color='b', label='向量2')
            self.ax.quiver(0, 0, 0, v3[0], v3[1], v3[2], color='g', label='向量3')
        
        # 绘制平行六面体 - 使用顶点和边
        vertices = np.array([
            [0, 0, 0],
            v1, v2, v3,
            v1+v2, v1+v3, v2+v3,
            v1+v2+v3
        ])
        
        # 绘制边
        edges = [
            [0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 4], 
            [2, 6], [3, 5], [3, 6], [4, 7], [5, 7], [6, 7]
        ]
        
        for edge in edges:
            self.ax.plot([vertices[edge[0]][0], vertices[edge[1]][0]],
                        [vertices[edge[0]][1], vertices[edge[1]][1]],
                        [vertices[edge[0]][2], vertices[edge[1]][2]], 'k-', alpha=0.6)
        
        # 标注行列式值
        det_value = np.linalg.det(matrix)
        self.ax.text2D(0.05, 0.95, f'行列式值: {det_value:.4f}', 
                     transform=self.ax.transAxes, fontsize=12, 
                     verticalalignment='top', 
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                     fontproperties=chinese_font)  # 使用中文字体
        
        # 设置标题和标签
        self.ax.set_title('3D行列式几何表示 - 平行六面体体积', fontproperties=chinese_font)
        self.ax.set_xlabel('X轴', fontproperties=chinese_font)
        self.ax.set_ylabel('Y轴', fontproperties=chinese_font)
        self.ax.set_zlabel('Z轴', fontproperties=chinese_font)
        self.ax.legend(prop=chinese_font)
    
    def visualize_determinant(self):
        """创建行列式计算的动态可视化"""
        matrix = self.get_matrix_from_entries()
        if matrix is None:
            return
        
        # 停止任何现有动画
        if hasattr(self, 'ani') and self.ani:
            self.ani.event_source.stop()
        
        # 清除图形
        self.ax.clear()
        
        try:
            # 删除可视化类型的判断，直接调用相应方法
            if self.matrix_size == 2:
                self.animate_2d_determinant(matrix)
            else:  # 3x3
                self.animate_3d_determinant(matrix)
        except Exception as e:
            messagebox.showerror("动画错误", f"无法创建动画: {str(e)}")
    
    def animate_2d_determinant(self, matrix):
        """2D行列式动画"""
        # 变换后的基向量
        v1_final = np.array([matrix[0, 0], matrix[1, 0]])
        v2_final = np.array([matrix[0, 1], matrix[1, 1]])
        
        # 初始基向量
        v1_start = np.array([1, 0])
        v2_start = np.array([0, 1])
        
        # 设置坐标轴并确保足够大的视图范围
        self.ax.clear()
        max_range = max([np.max(np.abs(v1_final)), np.max(np.abs(v2_final)), 5])
        margin = max_range * 0.2  # 添加20%的边距
        self.ax.set_xlim(-max_range-margin, max_range+margin)
        self.ax.set_ylim(-max_range-margin, max_range+margin)
        self.ax.set_aspect('equal')
        
        if self.show_grid_var.get():
            self.ax.grid(True)
        
        # 绘制坐标轴
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # 创建初始图形元素
        arrow1, = self.ax.plot([0, v1_start[0]], [0, v1_start[1]], 'r-', lw=2)
        arrow2, = self.ax.plot([0, v2_start[0]], [0, v2_start[1]], 'b-', lw=2)
        
        # 确保matplotlib的最新版本兼容性
        try:
            from matplotlib.pyplot import Polygon as PlotPolygon
            polygon = PlotPolygon([[0, 0], v1_start, v1_start+v2_start, v2_start], 
                                  alpha=0.3, facecolor='green', edgecolor='black')
        except ImportError:
            # 使用matplotlib.patches.Polygon作为备选
            polygon = Polygon(np.array([[0, 0], v1_start, v1_start+v2_start, v2_start]), 
                              alpha=0.3, facecolor='green', edgecolor='black')
        
        self.ax.add_patch(polygon)
        
        det_text = self.ax.text(0.05, 0.95, '', transform=self.ax.transAxes, 
                              fontsize=12, verticalalignment='top', 
                              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 动画函数
        def animate(i):
            t = i / 100  # 从0到1的插值
            
            # 当前向量状态
            v1_current = v1_start + t * (v1_final - v1_start)
            v2_current = v2_start + t * (v2_final - v2_start)
            
            # 更新箭头
            arrow1.set_data([0, v1_current[0]], [0, v1_current[1]])
            arrow2.set_data([0, v2_current[0]], [0, v2_current[1]])
            
            # 更新多边形
            vertices = np.array([[0, 0], v1_current, v1_current+v2_current, v2_current])
            polygon.set_xy(vertices)
            
            # 计算当前行列式
            current_matrix = np.array([[v1_current[0], v2_current[0]], 
                                      [v1_current[1], v2_current[1]]])
            det = np.linalg.det(current_matrix)
            det_text.set_text(f'行列式值: {det:.4f}')
            
            return arrow1, arrow2, polygon, det_text
        
        # 创建动画
        self.ani = animation.FuncAnimation(
            self.fig, animate, frames=101, interval=50, blit=True)
        
        # 设置标题和标签 - 使用中文字体
        self.ax.set_title('2D行列式几何表示 - 平行四边形面积', fontproperties=chinese_font)
        self.ax.set_xlabel('X轴', fontproperties=chinese_font)
        self.ax.set_ylabel('Y轴', fontproperties=chinese_font)
        
        # 显示动画
        self.canvas.draw()
    
    def animate_3d_determinant(self, matrix):
        """3D行列式动画"""
        # 重新创建3D轴
        self.ax.remove()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # 变换后的基向量
        v1_final = np.array([matrix[0, 0], matrix[1, 0], matrix[2, 0]])
        v2_final = np.array([matrix[0, 1], matrix[1, 1], matrix[2, 1]])
        v3_final = np.array([matrix[0, 2], matrix[1, 2], matrix[2, 2]])
        
        # 初始基向量
        v1_start = np.array([1, 0, 0])
        v2_start = np.array([0, 1, 0])
        v3_start = np.array([0, 0, 1])
        
        # 设置坐标范围并添加边距
        max_range = max([np.max(np.abs(v1_final)), np.max(np.abs(v2_final)), 
                        np.max(np.abs(v3_final)), 5])
        margin = max_range * 0.2  # 添加20%的边距
        self.ax.set_xlim(-max_range-margin, max_range+margin)
        self.ax.set_ylim(-max_range-margin, max_range+margin)
        self.ax.set_zlim(-max_range-margin, max_range+margin)
        
        # 绘制坐标轴
        self.ax.plot([0, 0], [0, 0], [-max_range-margin, max_range+margin], 'k-', alpha=0.2)
        self.ax.plot([0, 0], [-max_range-margin, max_range+margin], [0, 0], 'k-', alpha=0.2)
        self.ax.plot([-max_range-margin, max_range+margin], [0, 0], [0, 0], 'k-', alpha=0.2)
        
        # 创建初始向量
        arrow1 = self.ax.quiver(0, 0, 0, v1_start[0], v1_start[1], v1_start[2], color='r')
        arrow2 = self.ax.quiver(0, 0, 0, v2_start[0], v2_start[1], v2_start[2], color='b')
        arrow3 = self.ax.quiver(0, 0, 0, v3_start[0], v3_start[1], v3_start[2], color='g')
        
        # 标注行列式值
        det_text = self.ax.text2D(0.05, 0.95, '', transform=self.ax.transAxes, 
                                fontsize=12, verticalalignment='top', 
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                                fontproperties=chinese_font)
        
        # 动画函数
        def animate(i):
            # 清除上一帧
            self.ax.clear()
            
            # 重新设置坐标轴
            self.ax.set_xlim(-max_range-margin, max_range+margin)
            self.ax.set_ylim(-max_range-margin, max_range+margin)
            self.ax.set_zlim(-max_range-margin, max_range+margin)
            
            # 绘制坐标轴
            self.ax.plot([0, 0], [0, 0], [-max_range-margin, max_range+margin], 'k-', alpha=0.2)
            self.ax.plot([0, 0], [-max_range-margin, max_range+margin], [0, 0], 'k-', alpha=0.2)
            self.ax.plot([-max_range-margin, max_range+margin], [0, 0], [0, 0], 'k-', alpha=0.2)
            
            t = i / 100  # 从0到1的插值
            
            # 当前向量状态
            v1_current = v1_start + t * (v1_final - v1_start)
            v2_current = v2_start + t * (v2_final - v2_start)
            v3_current = v3_start + t * (v3_final - v3_start)
            
            # 绘制当前向量
            self.ax.quiver(0, 0, 0, v1_current[0], v1_current[1], v1_current[2], color='r')
            self.ax.quiver(0, 0, 0, v2_current[0], v2_current[1], v2_current[2], color='b')
            self.ax.quiver(0, 0, 0, v3_current[0], v3_current[1], v3_current[2], color='g')
            
            # 绘制平行六面体 - 使用顶点和边
            vertices = np.array([
                [0, 0, 0],
                v1_current, v2_current, v3_current,
                v1_current+v2_current, v1_current+v3_current, v2_current+v3_current,
                v1_current+v2_current+v3_current
            ])
            
            # 绘制边
            edges = [
                [0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 4], 
                [2, 6], [3, 5], [3, 6], [4, 7], [5, 7], [6, 7]
            ]
            
            for edge in edges:
                self.ax.plot([vertices[edge[0]][0], vertices[edge[1]][0]],
                            [vertices[edge[0]][1], vertices[edge[1]][1]],
                            [vertices[edge[0]][2], vertices[edge[1]][2]], 'k-', alpha=0.6)
            
            # 计算当前行列式
            current_matrix = np.array([
                [v1_current[0], v2_current[0], v3_current[0]],
                [v1_current[1], v2_current[1], v3_current[1]],
                [v1_current[2], v2_current[2], v3_current[2]]
            ])
            det = np.linalg.det(current_matrix)
            
            # 更新行列式文本
            self.ax.text2D(0.05, 0.95, f'行列式值: {det:.4f}', 
                         transform=self.ax.transAxes, fontsize=12, 
                         verticalalignment='top', 
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                         fontproperties=chinese_font)
            
            # 设置标题和标签
            self.ax.set_title('3D行列式几何表示 - 平行六面体体积', fontproperties=chinese_font)
            self.ax.set_xlabel('X轴', fontproperties=chinese_font)
            self.ax.set_ylabel('Y轴', fontproperties=chinese_font)
            self.ax.set_zlabel('Z轴', fontproperties=chinese_font)
            
            return []
        
        # 创建动画
        self.ani = animation.FuncAnimation(
            self.fig, animate, frames=101, interval=50, blit=False)
        
        # 显示动画
        self.canvas.draw()
    
    def step_by_step_calculation(self):
        """逐步计算行列式"""
        matrix = self.get_matrix_from_entries()
        if matrix is None:
            return
        
        if self.matrix_size == 2:
            self.step_by_step_2d(matrix)
        else:
            self.step_by_step_3d(matrix)
    
    def step_by_step_2d(self, matrix):
        """2x2行列式的逐步计算"""
        a, b = matrix[0, 0], matrix[0, 1]
        c, d = matrix[1, 0], matrix[1, 1]
        
        # 创建步骤
        steps = [
            f"对于2x2矩阵 [[{a}, {b}], [{c}, {d}]]",
            f"行列式计算公式: |A| = ad - bc",
            f"计算: |A| = ({a})×({d}) - ({b})×({c})",
            f"计算: |A| = {a*d} - {b*c}",
            f"最终结果: |A| = {a*d - b*c}"
        ]
        
        # 显示步骤
        self.show_steps(steps)
    
    def step_by_step_3d(self, matrix):
        """3x3行列式的逐步计算（用代数余子式法）"""
        a, b, c = matrix[0, 0], matrix[0, 1], matrix[0, 2]
        d, e, f = matrix[1, 0], matrix[1, 1], matrix[1, 2]
        g, h, i = matrix[2, 0], matrix[2, 1], matrix[2, 2]
        
        # 计算代数余子式
        A11 = e*i - f*h
        A12 = -(d*i - f*g)
        A13 = d*h - e*g
        
        # 创建步骤
        steps = [
            f"对于3x3矩阵 [[{a}, {b}, {c}], [{d}, {e}, {f}], [{g}, {h}, {i}]]",
            f"使用代数余子式展开（沿第一行）",
            f"计算 A11 = |[[{e}, {f}], [{h}, {i}]]| = {e}×{i} - {f}×{h} = {A11}",
            f"计算 A12 = -|[[{d}, {f}], [{g}, {i}]]| = -({d}×{i} - {f}×{g}) = {A12}",
            f"计算 A13 = |[[{d}, {e}], [{g}, {h}]]| = {d}×{h} - {e}×{g} = {A13}",
            f"行列式 = {a} × {A11} + {b} × {A12} + {c} × {A13}",
            f"行列式 = {a*A11} + {b*A12} + {c*A13}",
            f"最终结果: |A| = {a*A11 + b*A12 + c*A13}"
        ]
        
        # 显示步骤
        self.show_steps(steps)
    
    def show_steps(self, steps):
        """显示计算步骤"""
        # 创建新窗口
        step_window = tk.Toplevel(self.master)
        step_window.title("行列式计算步骤")
        step_window.geometry("500x400")
        
        # 创建标签和按钮
        ttk.Label(step_window, text="行列式计算步骤", font=("SimHei", 16)).pack(pady=10)
        
        # 步骤文本框
        step_text = tk.Text(step_window, height=15, width=50, font=("SimHei", 12))
        step_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # 显示所有步骤
        for step in steps:
            step_text.insert(tk.END, step + "\n\n")
        
        step_text.config(state=tk.DISABLED)
        
        # 关闭按钮
        ttk.Button(step_window, text="关闭", command=step_window.destroy).pack(pady=10)
    
    def reset_matrix_to_identity(self):
        """将矩阵重置为单位矩阵"""
        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, "1" if i == j else "0")
        
        # 重置结果和图形
        self.result_label.config(text="行列式值: ")
        
        # 重绘单位矩阵
        try:
            identity = np.eye(self.matrix_size)
            self.plot_determinant(identity)
        except Exception as e:
            messagebox.showerror("重置错误", f"重置矩阵时出错: {str(e)}")
    
    def generate_random_matrix(self):
        """生成随机矩阵"""
        try:
            # 生成-5到5之间的随机整数
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    self.matrix_entries[i][j].delete(0, tk.END)
                    # 避免生成全零矩阵
                    random_val = np.random.randint(-5, 6)
                    if random_val == 0:
                        random_val = 1
                    self.matrix_entries[i][j].insert(0, str(random_val))
            
            # 计算并显示新矩阵的行列式
            self.calculate_determinant()
        except Exception as e:
            messagebox.showerror("随机矩阵错误", f"生成随机矩阵时出错: {str(e)}")

    def show_theory(self):
        """显示行列式理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 行列式知识点内容
            sections = {
                "基本概念": """
行列式是线性代数中的一个重要概念，它是一个将方阵映射到实数的函数。

定义：
- n阶行列式是n阶方阵的一个标量值
- 记作|A|或det(A)，其中A是n×n矩阵
- 2×2矩阵的行列式: |A| = a₁₁a₂₂ - a₁₂a₂₁
- 3×3及更高阶矩阵可以通过代数余子式展开法计算

行列式的基本性质：
1. 转置不变性：|A| = |Aᵀ|
2. 如果矩阵有一行或一列全为零，则行列式为零
3. 交换两行或两列，行列式变号
4. 某行(列)乘以常数k，等于行列式乘以k
5. 某行(列)的k倍加到另一行(列)，行列式不变
""",
                "几何意义": """
1. 二维情况：
   - 2×2矩阵行列式的绝对值等于由两个列向量构成的平行四边形的面积
   - 行列式的符号表示定向，正值表示列向量按逆时针排列

2. 三维情况：
   - 3×3矩阵行列式的绝对值等于由三个列向量构成的平行六面体的体积
   - 行列式符号表示右手法则，正值表示列向量满足右手法则

3. n维情况：
   - n×n矩阵行列式的绝对值等于由n个列向量构成的n维平行体的n维体积
   - 行列式为零意味着列向量线性相关，所构成的平行体"塌陷"为零体积

这种几何解释使得行列式在向量空间变换、体积缩放等方面有着直观的应用。
""",
                "计算方法": """
1. 代数余子式展开法：
   - 沿任意行或列展开
   - |A| = Σ(-1)^(i+j) * a_ij * M_ij
   - 其中M_ij是去掉第i行第j列后的子矩阵的行列式

2. 三角化方法：
   - 通过初等行变换将矩阵转化为上三角形式
   - 此时行列式等于对角线元素的乘积
   - 每次交换两行需要变换行列式符号

3. 特殊矩阵的行列式：
   - 对角矩阵：行列式等于对角元素的乘积
   - 三角矩阵：行列式等于对角元素的乘积
   - 幂等矩阵：行列式为0或1
   - 正交矩阵：行列式为±1
""",
                "应用": """
1. 线性方程组：
   - 克莱默法则使用行列式求解线性方程组
   - 行列式为零意味着方程组可能无解或有无穷多解

2. 矩阵的可逆性：
   - 矩阵可逆当且仅当其行列式不为零
   - 逆矩阵的计算涉及伴随矩阵和行列式

3. 特征值和特征向量：
   - 特征多项式的常数项是行列式的±倍
   - |A-λI| = 0 是求特征值的关键方程

4. 坐标变换：
   - 行列式的绝对值表示单位体积在变换后的缩放比例
   - 雅可比行列式在积分变量替换中至关重要

5. 向量分析：
   - 向量的混合积和标量三重积可用行列式表示
   - 矢量场的散度和旋度计算中也会用到行列式
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "行列式理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建行列式理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("行列式理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="行列式理论知识", 
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

def main():
    """应用程序主入口点"""
    try:
        root = tk.Tk()
        DeterminantApp(root)
        root.mainloop()
    except Exception as e:
        print(f"启动应用程序时出错: {str(e)}")
        if tk.Tk().winfo_exists():
            messagebox.showerror("启动错误", f"启动应用程序时出错: {str(e)}")

if __name__ == "__main__":
    main()