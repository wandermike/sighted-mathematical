import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font as tkFont 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap
import warnings
from knowledge import KnowledgeLearningClass

# Suppress specific warnings if needed (e.g., from SymPy)
warnings.filterwarnings("ignore", category=UserWarning, module='sympy')

# Set default font for Matplotlib to support Chinese
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # Ensure minus sign displays correctly


class HessianApp:
    def __init__(self, root):
        self.root = root
        self.root.title("海森矩阵分析")
        self.root.geometry("1200x800")
        self.knowledge_learner = KnowledgeLearningClass()
        
        # 创建自定义颜色映射
        self.create_custom_colormaps()
        
        # 默认函数示例
        self.default_functions = [
            "x**2 + y**2",                # 抛物面（凸）
            "-(x**2 + y**2)",             # 抛物面（凹）
            "x**2 - y**2",                # 鞍面
            "sin(x) * cos(y)",            # 波浪面
            "exp(-(x**2 + y**2)/2)",      # 高斯函数
            "x**3 - 3*x*y**2",             # 猴鞍面
            "1/(x**2+y**2+0.1)",          # 可能出现奇点
            "log(x**2+y**2+0.1)"          # 对数函数
        ]
        
        # 状态变量
        self.current_function = tk.StringVar(value=self.default_functions[0])
        self.x_range = tk.StringVar(value="-2,2")
        self.y_range = tk.StringVar(value="-2,2")
        self.resolution = tk.IntVar(value=40)
        self.show_hessian_points = tk.BooleanVar(value=True)
        self.show_contour = tk.BooleanVar(value=False)
        self.colormap = tk.StringVar(value="viridis")
        self.alpha = tk.DoubleVar(value=0.8)
        self.point_size = tk.IntVar(value=40)
        self.point_density = tk.IntVar(value=15)  # 数值越大，选取点越稀疏
        self.z_auto_scale = tk.BooleanVar(value=True)
        self.z_min = tk.DoubleVar(value=-4)
        self.z_max = tk.DoubleVar(value=4)
        self._limits_set = False # Flag to track if limits have been set initially
        
        # --- Style Configuration ---
        self.style = ttk.Style()
        try:
            # Try themes available on different platforms
            if root.tk.call('tk', 'windowingsystem') == 'win32':
                self.style.theme_use('vista')
            elif root.tk.call('tk', 'windowingsystem') == 'aqua':
                 self.style.theme_use('aqua')
            else: # Default for Linux/other
                self.style.theme_use('clam')
        except tk.TclError:
            print("Warning: Preferred theme not available, using default.")
            self.style.theme_use('default') # Fallback

        # Configure style for the Info LabelFrame and ScrolledText
        self.style.configure("Info.TLabelframe", padding=10, relief=tk.GROOVE, borderwidth=2)
        self.style.configure("Info.TLabelframe.Label", font=("Microsoft YaHei", 11, "bold")) # Style the label frame title

        # Define a custom font for the info text
        self.info_font = tkFont.Font(family="Microsoft YaHei", size=10) # Or "SimHei"

        # 创建UI AFTER style configuration
        self.create_ui()
        
        # 设置绘图
        self._setup_plot()
        
        # 初始绘图
        self.create_plot()
        
        # 添加鼠标交互相关的变量
        self.mouse_pressed = False
        self.last_x = None
        self.last_y = None
        self._event_cids = []
        self.current_surf = None  # 存储当前曲面对象

        self.knowledge_learner = KnowledgeLearningClass()

    def create_custom_colormaps(self):
        """创建自定义颜色映射"""
        self.custom_colormaps = {
            'viridis': plt.cm.viridis, 'plasma': plt.cm.plasma, 'inferno': plt.cm.inferno,
            'magma': plt.cm.magma, 'cividis': plt.cm.cividis, 'coolwarm': plt.cm.coolwarm,
            'rainbow': plt.cm.rainbow, 'terrain': plt.cm.terrain, 'ocean': plt.cm.ocean,
            'gist_earth': plt.cm.gist_earth, 'cubehelix': plt.cm.cubehelix,
            'curvature': LinearSegmentedColormap.from_list(
                'curvature', ['blue', 'lightgray', 'red'], N=256
            )
        }


    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板 (固定宽度)
        control_frame = ttk.Frame(main_frame, width=350)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
        control_frame.pack_propagate(False) # Prevent resizing based on content
        
        # 右侧绘图区域
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=0)
        
        # ===== 控制面板内容 =====
        # Use a consistent padding style
        frame_padding = {"padx": 5, "pady": 5}
        widget_padding = {"padx": 5, "pady": 2}
        
        # 函数输入区域
        func_frame = ttk.LabelFrame(control_frame, text="函数设置")
        func_frame.pack(fill=tk.X, **frame_padding)
        
        ttk.Label(func_frame, text="输入或选择 f(x,y):").pack(anchor=tk.W, **widget_padding)
        
        # 函数输入框和下拉菜单组合
        self.func_entry = ttk.Combobox(func_frame, textvariable=self.current_function, 
                                       values=self.default_functions, width=35)
        self.func_entry.pack(fill=tk.X, expand=True, **widget_padding)
        
        # 范围设置
        range_frame = ttk.Frame(func_frame)
        range_frame.pack(fill=tk.X, **widget_padding)
        
        ttk.Label(range_frame, text="X范围:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(range_frame, textvariable=self.x_range, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(range_frame, text="Y范围:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        ttk.Entry(range_frame, textvariable=self.y_range, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(range_frame, text="分辨率:").grid(row=1, column=0, sticky=tk.W, pady=5)
        resolution_scale = ttk.Scale(range_frame, from_=20, to=100, variable=self.resolution, 
                                    orient=tk.HORIZONTAL)
        resolution_scale.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # Z轴范围设置
        z_range_frame = ttk.LabelFrame(func_frame, text="Z轴范围")
        z_range_frame.pack(fill=tk.X, **frame_padding)

        ttk.Checkbutton(z_range_frame, text="自动缩放", variable=self.z_auto_scale).pack(anchor=tk.W, **widget_padding)

        z_manual_frame = ttk.Frame(z_range_frame)
        z_manual_frame.pack(fill=tk.X, **widget_padding)

        ttk.Label(z_manual_frame, text="Z Min:").grid(row=0, column=0, sticky=tk.W)
        z_min_entry = ttk.Entry(z_manual_frame, textvariable=self.z_min, width=8)
        z_min_entry.grid(row=0, column=1, padx=5)

        ttk.Label(z_manual_frame, text="Z Max:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        z_max_entry = ttk.Entry(z_manual_frame, textvariable=self.z_max, width=8)
        z_max_entry.grid(row=0, column=3, padx=5)
        
        # 可视化设置
        visual_frame = ttk.LabelFrame(control_frame, text="可视化设置")
        visual_frame.pack(fill=tk.X, **frame_padding)
        
        ttk.Checkbutton(visual_frame, text="显示Hessian特征点", variable=self.show_hessian_points).pack(anchor=tk.W, **widget_padding)
        ttk.Checkbutton(visual_frame, text="显示等高线", variable=self.show_contour).pack(anchor=tk.W, **widget_padding)
        
        # 颜色映射选择
        cmap_frame = ttk.Frame(visual_frame)
        cmap_frame.pack(fill=tk.X, **widget_padding)
        ttk.Label(cmap_frame, text="颜色映射:").pack(side=tk.LEFT)
        cmap_combo = ttk.Combobox(cmap_frame, textvariable=self.colormap, 
                                 values=list(self.custom_colormaps.keys()), width=15, state="readonly")
        cmap_combo.pack(side=tk.LEFT, padx=5)
        
        # 透明度设置
        alpha_frame = ttk.Frame(visual_frame)
        alpha_frame.pack(fill=tk.X, **widget_padding)
        ttk.Label(alpha_frame, text="透明度:").pack(side=tk.LEFT)
        alpha_scale = ttk.Scale(alpha_frame, from_=0.1, to=1.0, variable=self.alpha, 
                               orient=tk.HORIZONTAL)
        alpha_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 点大小和密度设置
        point_frame = ttk.LabelFrame(control_frame, text="特征点设置")
        point_frame.pack(fill=tk.X, **frame_padding)
        
        ttk.Label(point_frame, text="点大小:").grid(row=0, column=0, sticky=tk.W, **widget_padding)
        point_size_scale = ttk.Scale(point_frame, from_=10, to=150, variable=self.point_size, 
                                    orient=tk.HORIZONTAL)
        point_size_scale.grid(row=0, column=1, sticky=tk.EW, **widget_padding)
        
        ttk.Label(point_frame, text="点密度:").grid(row=1, column=0, sticky=tk.W, **widget_padding)
        point_density_scale = ttk.Scale(point_frame, from_=1, to=20, variable=self.point_density, 
                                       orient=tk.HORIZONTAL)
        point_density_scale.grid(row=1, column=1, sticky=tk.EW, **widget_padding)
        
        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="绘制", command=self.create_plot).pack(side=tk.LEFT, padx=0,pady=5)
        ttk.Button(button_frame, text="重置", command=self.reset_settings).pack(side=tk.LEFT, padx=0,pady=5)
        ttk.Button(button_frame, text="保存图像", command=self.save_figure).pack(side=tk.LEFT, padx=0,pady=5)
        knowledge_learning = ttk.Button(button_frame, text="知识介绍", command=self.knowledge_learner.knowledge_learning_9_function)
        knowledge_learning.pack(side=tk.LEFT, padx=0,pady=5)
        
        # 信息显示区域 - Apply the style and custom font
        info_frame = ttk.LabelFrame(control_frame, text="信息", style="Info.TLabelframe")
        info_frame.pack(fill=tk.BOTH, expand=True, **frame_padding)
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame, height=10, wrap=tk.WORD,
            font=self.info_font, # Use the custom font
            padx=8, pady=8, relief=tk.FLAT, borderwidth=1,
            bg="#f0f0f0" # Slightly off-white background
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Define tags for bold text here, once
        self.info_text.tag_configure("bold", font=tkFont.Font(family="Microsoft YaHei", size=10, weight="bold"))
        self.info_text.tag_configure("italic", font=tkFont.Font(family="Microsoft YaHei", size=10, slant="italic"))
        self.info_text.tag_configure("code", font=tkFont.Font(family="Consolas", size=10), background="#e0e0e0")

        self.update_info_text(None) # Display initial help text
        self.info_text.config(state=tk.DISABLED)
        
        # ===== 绘图区域 =====
        self.fig_frame = ttk.Frame(plot_frame)
        self.fig_frame.pack(fill=tk.BOTH, expand=True)

    def reset_settings(self):
        """重置所有设置为默认值"""
        self.current_function.set(self.default_functions[0])
        self.x_range.set("-2,2")
        self.y_range.set("-2,2")
        self.resolution.set(40)
        self.show_hessian_points.set(True)
        self.show_contour.set(False)
        self.colormap.set("viridis")
        self.alpha.set(0.8)
        self.point_size.set(40)
        self.point_density.set(15)
        self.z_auto_scale.set(True)
        self.z_min.set(-4)
        self.z_max.set(4)
        self._limits_set = False # Reset the flag so limits recalculate on next plot
        self.create_plot()

    def save_figure(self):
        """保存当前图像"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", f"图像已保存至: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图像时出错: {str(e)}")

    def create_plot(self):
        """创建绘图的主入口点"""
        try:
            # 在绘图前重置颜色栏
            if hasattr(self, 'cbar') and self.cbar:
                try:
                    self.cbar.remove()
                except Exception as e:
                    print(f"清理颜色栏时出错: {e}")
                finally:
                    self.cbar = None
                
            # 保存当前视图状态
            view_state = (self.ax.elev, self.ax.azim) if hasattr(self, 'ax') else None
            
            # 完全重新初始化绘图区域
            self._setup_plot()
            
            # 绘制新的图形
            self._plot_function()
            
            # 恢复视图状态
            if view_state:
                self.ax.view_init(elev=view_state[0], azim=view_state[1])
            
            # 更新画布
            self.canvas.draw_idle()
            
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘图时发生错误: {str(e)}")
            print(f"DEBUG - 完整错误信息: {str(e)}")
            import traceback
            traceback.print_exc()

    def _setup_plot(self):
        """设置绘图区域"""
        try:
            # 如果已有图形则先清理
            if hasattr(self, 'fig') and self.fig:
                plt.close(self.fig)
                for widget in self.fig_frame.winfo_children():
                    widget.destroy()
            
            # 创建新的Figure对象
            self.fig = Figure(figsize=(12, 8), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.fig_frame)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # 创建3D axes并设置初始视角
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.view_init(elev=30, azim=45)
            
            # 使用matplotlib内置的3D旋转功能
            self.ax.mouse_init()
            
            # 绑定鼠标事件 - 简化为只处理点击
            self._bind_mouse_events()
            
        except Exception as e:
            messagebox.showerror("初始化错误", f"初始化绘图区域失败: {str(e)}")
            print(f"DEBUG - 初始化错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def _plot_function(self):
        """实际绘图逻辑"""
        try:
            # 清除旧图形但保留axes实例
            self.ax.clear()
            
            # 设置初始标题
            self.ax.set_title('Hessian矩阵曲率可视化', 
                            fontproperties=FontProperties(family='SimHei', size=12))
            
            # 获取当前函数
            func_str = self.current_function.get()
            if not func_str:
                print("警告: 未指定函数")
                return
                
            # 解析范围
            try:
                x_range = self.x_range.get().split(',')
                y_range = self.y_range.get().split(',')
                x_min, x_max = float(x_range[0]), float(x_range[1])
                y_min, y_max = float(y_range[0]), float(y_range[1])
            except Exception as e:
                print(f"解析范围时出错: {e}")
                x_min, x_max = -2, 2
                y_min, y_max = -2, 2
            
            # 解析函数并绘制
            x, y = sp.symbols('x y')
            expr = parse_expr(func_str, transformations=(standard_transformations + (implicit_multiplication_application,)))
            
            # 创建数值函数
            f = sp.lambdify((x, y), expr, modules=['numpy', {'log': np.log, 'sqrt': np.sqrt, 'exp': np.exp}])
            
            # 计算Hessian矩阵
            hessian_matrix = sp.hessian(expr, (x, y))
            hessian_func = sp.lambdify((x, y), hessian_matrix, modules=['numpy'])
            
            # 创建网格数据
            resolution = self.resolution.get()
            x_vals = np.linspace(x_min, x_max, resolution)
            y_vals = np.linspace(y_min, y_max, resolution)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # 计算Z值，处理无穷大和NaN
            Z = np.zeros_like(X)
            with np.errstate(divide='ignore', invalid='ignore'):
                Z = f(X, Y)
            Z[~np.isfinite(Z)] = np.nan  # 将非有限值替换为NaN
            
            # 获取颜色映射
            cmap_name = self.colormap.get()
            cmap = plt.cm.get_cmap(cmap_name)
            
            # 绘制曲面
            alpha = self.alpha.get()
            surf = self.ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha, 
                                      edgecolor='none', antialiased=True)
            
            # 存储当前曲面对象
            self.current_surf = surf
            
            # 创建颜色栏
            if hasattr(self, 'cbar') and self.cbar:
                try:
                    self.cbar.remove()
                except Exception as e:
                    print(f"移除颜色栏时出错: {e}")
                finally:
                    self.cbar = None
            
            self.cbar = self.fig.colorbar(surf, ax=self.ax, shrink=0.5, aspect=5, pad=0.15)
            self.cbar.set_label('函数值', rotation=270, labelpad=20)
            
            # 绘制Hessian特征点
            if self.show_hessian_points.get():
                point_size = self.point_size.get()
                step = max(1, self.point_density.get())  # 直接使用密度值作为步长
                
                convex_count, concave_count, saddle_count = 0, 0, 0
                
                for i in range(0, resolution, step):
                    for j in range(0, resolution, step):
                        try:
                            x_val, y_val = X[j, i], Y[j, i]
                            z_val = Z[j, i]
                            
                            # 跳过NaN值
                            if not np.isfinite(z_val):
                                continue
                                
                            hess = hessian_func(x_val, y_val)
                            if not np.all(np.isfinite(hess)):
                                continue
                                
                            eigenvalues = np.linalg.eigvals(hess)
                            eigenvalues = np.real(eigenvalues)  # 确保特征值是实数
                            
                            # 确定点类型
                            if all(eigenvalues > 1e-9):
                                color, convex_count = 'g', convex_count + 1  # 凸点
                            elif all(eigenvalues < -1e-9):
                                color, concave_count = 'r', concave_count + 1  # 凹点
                            else:
                                color, saddle_count = 'b', saddle_count + 1  # 鞍点
                                
                            self.ax.scatter(x_val, y_val, z_val, color=color, s=point_size,
                                          edgecolor='k', linewidth=0.5, alpha=0.9)
                        except Exception:
                            pass  # 忽略单个点的错误
                            
                # 存储点统计
                self._hessian_point_counts = (convex_count, concave_count, saddle_count)
            
            # 绘制等高线
            if self.show_contour.get():
                try:
                    z_valid = Z[np.isfinite(Z)]
                    if len(z_valid) > 0:
                        z_min = np.nanmin(z_valid)
                        z_max = np.nanmax(z_valid)
                        if np.isfinite(z_min) and np.isfinite(z_max) and z_max > z_min:
                            contour_offset = z_min - 0.1 * (z_max - z_min)
                            self.ax.contour(X, Y, Z, zdir='z', offset=contour_offset,
                                          cmap='coolwarm', levels=10)
                except Exception as e:
                    print(f"绘制等高线时出错: {e}")
            
            # 设置轴标签
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')
            self.ax.set_title(f'f(x,y) = {func_str}', fontsize=10)
            
            # 更新信息文本
            self.update_info_text(expr)
            
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制函数时出错: {str(e)}")
            print(f"DEBUG - 绘图错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_info_text(self, expr):
        """更新信息文本区域"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        if expr is None: # Handle initial call before first plot
            self.info_text.insert(tk.END, "Hessian矩阵可视化工具\n\n", ("bold",))
            self.info_text.insert(tk.END, "使用说明:\n", ("italic",))
            self.info_text.insert(tk.END, "  1. 输入或选择一个二元函数 f(x,y).\n")
            self.info_text.insert(tk.END, "  2. 设置X, Y, Z轴的范围和分辨率.\n")
            self.info_text.insert(tk.END, "  3. 调整可视化选项 (特征点, 等高线, 颜色, 透明度).\n")
            self.info_text.insert(tk.END, "  4. 点击 '绘制'.\n")
            self.info_text.insert(tk.END, "  5. 拖动鼠标左键旋转视角.\n\n")
            self.info_text.insert(tk.END, "注意:\n", ("italic",))
            self.info_text.insert(tk.END, "  - 使用 ", ("code",))
            self.info_text.insert(tk.END, "**", ("code", "bold"))
            self.info_text.insert(tk.END, " 表示幂运算 (e.g., ", ("code",))
            self.info_text.insert(tk.END, "x**2", ("code", "bold"))
            self.info_text.insert(tk.END, ").\n", ("code",))
            self.info_text.insert(tk.END, "  - 支持函数: ", ("code",))
            self.info_text.insert(tk.END, "sin, cos, exp, log, sqrt, pi, E", ("code", "bold"))
            self.info_text.insert(tk.END, ".\n\n", ("code",))
            self.info_text.insert(tk.END, "点颜色说明:\n", ("bold",))
            self.info_text.insert(tk.END, "  - ", None)
            self.info_text.insert(tk.END, "绿色:", ("bold",))
            self.info_text.insert(tk.END, " 凸点 (所有特征值 > 0)\n")
            self.info_text.insert(tk.END, "  - ", None)
            self.info_text.insert(tk.END, "红色:", ("bold",))
            self.info_text.insert(tk.END, " 凹点 (所有特征值 < 0)\n")
            self.info_text.insert(tk.END, "  - ", None)
            self.info_text.insert(tk.END, "蓝色:", ("bold",))
            self.info_text.insert(tk.END, " 鞍点 (特征值有正有负)\n")
            self.info_text.config(state=tk.DISABLED)
            return

        try:
            # --- 确保 expr 是字符串 ---
            expr_str_info = str(expr)

            x, y = sp.symbols('x y')
            local_dict = {'x': x, 'y': y, 'sin': sp.sin, 'cos': sp.cos, 'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi}
            transformations = standard_transformations + (implicit_multiplication_application,)
            parsed_expr = parse_expr(expr_str_info, local_dict=local_dict, transformations=transformations) # Parse the string

            # Calculate derivatives
            df_dx = sp.diff(parsed_expr, x)
            df_dy = sp.diff(parsed_expr, y)
            d2f_dx2 = sp.diff(df_dx, x)
            d2f_dy2 = sp.diff(df_dy, y)
            d2f_dxdy = sp.diff(df_dx, y)

            # --- Displaying the information ---
            self.info_text.insert(tk.END, "函数: ", ("bold",))
            self.info_text.insert(tk.END, f"f(x,y) = {expr_str_info}\n\n") # Use the ensured string

            self.info_text.insert(tk.END, "偏导数:\n", ("bold",))
            self.info_text.insert(tk.END, f"  ∂f/∂x = {df_dx}\n") # Implicit str() is usually safe here
            self.info_text.insert(tk.END, f"  ∂f/∂y = {df_dy}\n\n") # Implicit str()

            self.info_text.insert(tk.END, "Hessian矩阵:\n", ("bold",))
            self.info_text.insert(tk.END, f"  ∂²f/∂x²   = {d2f_dx2}\n") # Implicit str()
            self.info_text.insert(tk.END, f"  ∂²f/∂x∂y = {d2f_dxdy}\n") # Implicit str()
            self.info_text.insert(tk.END, f"  ∂²f/∂y²   = {d2f_dy2}\n\n") # Implicit str()

            # Add point statistics if available
            if hasattr(self, '_hessian_point_counts'):
                 convex, concave, saddle = self._hessian_point_counts
                 self.info_text.insert(tk.END, "\n当前视图点统计:\n", ("bold",))
                 self.info_text.insert(tk.END, f"  - 凸点: {convex}\n")
                 self.info_text.insert(tk.END, f"  - 凹点: {concave}\n")
                 self.info_text.insert(tk.END, f"  - 鞍点: {saddle}\n")

            # ... (rest of info text: color legend, point stats) ...

        except Exception as e_inner:
            # --- Refined Error Handling ---
            self.info_text.insert(tk.END, "\n错误:\n", ("bold", "error")) # Define 'error' tag if needed
            error_msg = f"  计算导数/Hessian时出错 ({type(e_inner).__name__}): {e_inner}\n"
            self.info_text.insert(tk.END, error_msg)
            print(f"Error in update_info_text: {error_msg}")
            import traceback
            traceback.print_exc()

        finally:
            self.info_text.config(state=tk.DISABLED)

    def draw_function_and_hessian(self, expr, x_min, x_max, y_min, y_max, view_angle=None):
        """绘制函数和Hessian矩阵的特征值信息"""
        try:
            # --- 解析和计算 ---
            # --- 关键修复：确保在解析前将expr转换为字符串 ---
            expr_str = str(expr)

            x, y = sp.symbols('x y')
            local_dict = {'x': x, 'y': y, 'sin': sp.sin, 'cos': sp.cos, 'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi}
            transformations = standard_transformations + (implicit_multiplication_application,)
            # --- 使用转换后的字符串进行解析 ---
            parsed_expr = parse_expr(expr_str, local_dict=local_dict, transformations=transformations)

            # 创建数值函数
            f = sp.lambdify((x, y), parsed_expr, modules=['numpy', {'log': np.log, 'sqrt': np.sqrt, 'exp': np.exp}])
            # 计算Hessian矩阵
            hessian_matrix = sp.hessian(parsed_expr, (x, y))
            hessian_func = sp.lambdify((x, y), hessian_matrix, modules=['numpy'])

            # 创建网格数据
            resolution = self.resolution.get()
            x_vals = np.linspace(x_min, x_max, resolution)
            y_vals = np.linspace(y_min, y_max, resolution)
            X, Y = np.meshgrid(x_vals, y_vals)

            # 计算Z值，处理无穷大和NaN
            Z = np.zeros_like(X)
            with np.errstate(divide='ignore', invalid='ignore'): # 忽略计算中的警告
                Z = f(X, Y)
            Z[~np.isfinite(Z)] = np.nan # 将非有限值替换为NaN

            # --- 清除旧的绘图元素，而不是整个轴 ---
            # 移除之前的曲面、散点图、等高线和文本（如果需要）
            # 注意：保留轴标签、标题和网格
            if hasattr(self, 'surf') and self.surf:
                self.surf.remove()
                del self.surf
            # 移除之前的散点图集合 (scatter返回PathCollection)
            for coll in self.ax.collections:
                 coll.remove()
            # 移除之前的等高线集合 (contour返回QuadContourSet)
            for cont in self.ax.findobj(match=lambda x: hasattr(x, 'collections')):
                 if hasattr(cont, 'collections'): # Check again just in case
                     for c in cont.collections:
                         c.remove()
                 try:
                     cont.remove() # Remove the contour set itself
                 except ValueError: pass # May already be removed if part of collections
            # 移除之前的颜色条
            if hasattr(self, 'colorbar'):
                try: self.colorbar.remove()
                except: pass
                delattr(self, 'colorbar')


            # 获取颜色映射
            cmap = self.custom_colormaps.get(self.colormap.get(), plt.cm.viridis)

            # --- 确定并应用Z Limits (逻辑保持不变) ---
            z_min_limit, z_max_limit = -1.0, 1.0
            valid_z_exists = False
            z_valid = Z[np.isfinite(Z)]

            if len(z_valid) > 0:
                valid_z_exists = True
                if self.z_auto_scale.get():
                    # ... (自动缩放逻辑不变) ...
                    z_min_calc = np.percentile(z_valid, 2)
                    z_max_calc = np.percentile(z_valid, 98)
                    if np.isclose(z_min_calc, z_max_calc):
                        median_z = np.median(z_valid); z_range = 1.0
                        z_min_calc = median_z - 0.5 * z_range; z_max_calc = median_z + 0.5 * z_range
                    else:
                        z_range = z_max_calc - z_min_calc; padding = 0.1 * max(z_range, 1e-6)
                        z_min_calc -= padding; z_max_calc += padding
                    z_min_limit, z_max_limit = z_min_calc, z_max_calc
                else:
                    # ... (手动缩放逻辑不变) ...
                    z_min_limit = self.z_min.get(); z_max_limit = self.z_max.get()
                    if z_min_limit >= z_max_limit:
                         messagebox.showwarning("范围警告", "Z最小值必须小于Z最大值。使用默认范围[-1, 1]。")
                         z_min_limit, z_max_limit = -1.0, 1.0
            else:
                 print("Warning: No finite Z values calculated for the surface.")

            # --- 确定是否首次绘制并设置/保持范围 ---
            initial_plot = view_angle is None or not self._limits_set
            final_zlim = (z_min_limit, z_max_limit)

            if initial_plot:
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min, y_max)
                self.ax.set_zlim(final_zlim)
                self._limits_set = True
                self.ax.autoscale(enable=False)
                # 设置初始视角
                self.ax.view_init(elev=30, azim=-60)
            else:
                # 保持现有范围 (因为没有clear, 理论上不需要重设, 但为了保险)
                final_xlim = self.ax.get_xlim()
                final_ylim = self.ax.get_ylim()
                final_zlim = self.ax.get_zlim() # 获取当前（固定的）Z范围
                self.ax.set_xlim(final_xlim)
                self.ax.set_ylim(final_ylim)
                self.ax.set_zlim(final_zlim)
                # --- 不需要恢复视角，因为它没有被清除 ---
                # if view_angle:
                #     try: self.ax.view_init(elev=view_angle[0], azim=view_angle[1])
                #     except: pass # Keep current view if restore fails

            # --- 重新绘制元素 ---
            # --- Plot Surface ---
            if valid_z_exists:
                 try:
                     self.surf = self.ax.plot_surface(X, Y, Z, cmap=cmap, alpha=self.alpha.get(),
                                                edgecolor='none', rstride=1, cstride=1,
                                                vmin=final_zlim[0], vmax=final_zlim[1],
                                                linewidth=0, antialiased=True)
                 except Exception as e:
                     print(f"Error plotting surface: {e}")
                     messagebox.showerror("绘图错误", f"绘制曲面时出错: {e}")
                     self.surf = None # Ensure self.surf is None if plotting failed
            else:
                 print("Skipping surface plot as no valid Z data exists.")
                 self.surf = None

            # --- Colorbar ---
            if self.surf: # 只有在成功绘制曲面后才添加颜色条
                try:
                    self.colorbar = self.fig.colorbar(self.surf, ax=self.ax, shrink=0.6, aspect=10, pad=0.1)
                    self.colorbar.set_label('函数值 f(x,y)', rotation=270, labelpad=15)
                except Exception as e:
                    print(f"Error creating colorbar: {e}")

            # --- Contours ---
            if self.show_contour.get() and valid_z_exists:
                # ... (等高线绘制逻辑不变, 确保不设置zlim) ...
                try:
                    z_min_finite = np.nanmin(z_valid)
                    z_max_finite = np.nanmax(z_valid)
                    if np.isfinite(z_min_finite) and np.isfinite(z_max_finite) and z_max_finite > z_min_finite:
                         contour_offset = z_min_finite - 0.1 * (z_max_finite - z_min_finite)
                         self.ax.contour(X, Y, Z, zdir='z', offset=contour_offset,
                                         cmap='coolwarm', levels=10)
                    else:
                         print("Warning: Cannot draw contours due to invalid Z range for offset calculation.")
                except Exception as e:
                    print(f"Error drawing contours: {e}")


            # --- Hessian Points ---
            # ... (Hessian点绘制逻辑不变, 包括计数器重置和存储) ...
            self._hessian_point_counts = (0, 0, 0)
            if self.show_hessian_points.get():
                point_size = self.point_size.get()
                step = max(1, self.point_density.get())  # 直接使用密度值作为步长
                convex_count, concave_count, saddle_count = 0, 0, 0

                # Iterate using steps based on density
                for i in range(0, resolution, step):
                    for j in range(0, resolution, step):
                        try:
                            x_val, y_val = X[j, i], Y[j, i]
                            z_val = Z[j, i] # Use already calculated Z

                            # Skip if Z is NaN or outside current Z limits
                            if not np.isfinite(z_val) or z_val < final_zlim[0] or z_val > final_zlim[1]:
                                continue

                            hess = hessian_func(x_val, y_val)
                            if not np.all(np.isfinite(hess)): continue

                            eigenvalues = np.linalg.eigvals(hess)
                            # Ensure eigenvalues are real (Hessian should be symmetric)
                            eigenvalues = np.real(eigenvalues)

                            # Determine point type
                            if all(eigenvalues > 1e-9): color, convex_count = 'g', convex_count + 1
                            elif all(eigenvalues < -1e-9): color, concave_count = 'r', concave_count + 1
                            else: color, saddle_count = 'b', saddle_count + 1 # Corrected indentation

                            self.ax.scatter(x_val, y_val, z_val, color=color, s=point_size,
                                           edgecolor='k', linewidth=0.5, alpha=0.9, depthshade=True)
                        except Exception:
                            # print(f"Error calculating/plotting point at ({i},{j}): {e}") # Optional debug
                            pass # Ignore errors for individual points
                # Store counts
                self._hessian_point_counts = (convex_count, concave_count, saddle_count)
            else:
                 # Clear counts if points are not shown
                 if hasattr(self, '_hessian_point_counts'):
                     del self._hessian_point_counts


            # --- 更新标签、标题、网格 (这些在clear时会丢失，所以需要重设) ---
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')
            # --- 使用转换后的字符串设置标题 ---
            self.ax.set_title(f'f(x,y) = {expr_str}', wrap=True, fontsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.6) # 重新应用网格

            # --- 更新信息文本 ---
            self.update_info_text(expr) # Pass the original expr

            # --- Final Draw ---
            self.canvas.draw_idle()

        except Exception as e:
            # --- 改进错误报告 ---
            error_type = type(e).__name__
            error_msg = f"处理函数或绘图时发生错误 ({error_type}):\n{e}"
            messagebox.showerror("绘图错误", error_msg)
            print(f"Error during plot creation ({error_type}): {e}")
            import traceback
            traceback.print_exc() # 打印详细错误信息到控制台


    def _bind_mouse_events(self):
        """绑定鼠标事件处理函数"""
        # 先清除旧的事件绑定
        if hasattr(self, '_event_cids') and self._event_cids:
            for cid in self._event_cids:
                try:
                    self.canvas.mpl_disconnect(cid)
                except Exception as e:
                    print(f"断开事件连接时出错: {e}")
            self._event_cids = []
            
        # 使用内置的旋转函数
        self.ax.mouse_init()
        
        # 只绑定点击事件用于显示信息
        try:
            cid = self.canvas.mpl_connect('button_press_event', self.on_click)
            self._event_cids.append(cid)
        except Exception as e:
            print(f"绑定鼠标事件时出错: {e}")
    
    def on_click(self, event):
        """处理鼠标点击事件，显示点信息"""
        if event.inaxes == self.ax and event.button == 3:  # 右键点击
            try:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    # 获取当前函数
                    func_str = self.current_function.get()
                    if not func_str:
                        return
                        
                    # 计算Z值
                    x_sym, y_sym = sp.symbols('x y')
                    expr = parse_expr(func_str, transformations=(standard_transformations + (implicit_multiplication_application,)))
                    f = sp.lambdify((x_sym, y_sym), expr, modules=['numpy'])
                    z = f(x, y)
                    
                    # 计算Hessian信息
                    hessian = sp.hessian(expr, (x_sym, y_sym))
                    hessian_func = sp.lambdify((x_sym, y_sym), hessian, modules=['numpy'])
                    
                    try:
                        hess_matrix = hessian_func(x, y)
                        eigenvalues = np.linalg.eigvals(hess_matrix)
                        eigenvalues = np.real(eigenvalues)
                        
                        if all(eigenvalues > 1e-9):
                            point_type = "凸点 (所有特征值 > 0)"
                        elif all(eigenvalues < -1e-9):
                            point_type = "凹点 (所有特征值 < 0)"
                        else:
                            point_type = "鞍点 (特征值有正有负)"
                            
                        hessian_info = f"\n特征值: [{eigenvalues[0]:.4f}, {eigenvalues[1]:.4f}]\n类型: {point_type}"
                    except:
                        hessian_info = "\n无法计算Hessian信息"
                    
                    info = f"坐标: ({x:.4f}, {y:.4f}, {z:.4f}){hessian_info}"
                    messagebox.showinfo("点信息", info)
            except Exception as e:
                print(f"点击事件处理错误: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    # Set a base font size for the application
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=10, family="Microsoft YaHei") # Or SimHei
    root.option_add("*Font", default_font)

    # Set style for specific widgets if needed
    style = ttk.Style()
    style.configure("TLabelframe.Label", font=("Microsoft YaHei", 11, "bold"))
    style.configure("TButton", padding=5)
    style.configure("TEntry", padding=3)
    style.configure("TCombobox", padding=3)

    app = HessianApp(root)
    root.mainloop()