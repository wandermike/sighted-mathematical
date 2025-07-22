import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import stats
import math

# 正确配置 Matplotlib 以显示中文
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'FangSong', 'KaiTi', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.family'] = 'sans-serif'

class ConfidenceIntervalApp:
    def __init__(self, master):
        self.master = master
        master.title("置信区间可视化工具")
        self.master.geometry("1200x800")

        # 创建主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标题 - 使用纯中文避免特殊字符问题
        title_label = ttk.Label(main_frame, text="置信区间可视化", font=("Microsoft YaHei", 18, "bold"))
        title_label.pack(pady=10)

        # --- Create layout frames *within* self.master ---
        # Left control panel
        self.control_frame = ttk.LabelFrame(self.master, text="参数设置")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right area
        right_frame = ttk.Frame(self.master)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Plotting area *within* right_frame
        plot_frame = ttk.Frame(right_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Result area *within* right_frame
        result_frame = ttk.LabelFrame(right_frame, text="计算结果")
        result_frame.pack(fill=tk.X, pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=6, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- Control panel content ---
        # Ensure widgets added here use self.control_frame as parent
        ttk.Label(self.control_frame, text="选择置信区间类型:").pack(anchor=tk.W, pady=(10, 2))
        self.ci_type_var = tk.StringVar(value="均值 (总体方差未知, t分布)")
        ci_combobox = ttk.Combobox(self.control_frame, textvariable=self.ci_type_var,
                                     values=[
                                         "均值 (总体方差未知, t分布)",
                                         "均值 (总体方差已知, Z分布)",
                                         "比例 (正态近似)",
                                         # "方差 (卡方分布)" # 待添加
                                     ], width=30)
        ci_combobox.pack(anchor=tk.W, pady=2, fill=tk.X)
        ci_combobox.bind("<<ComboboxSelected>>", self.on_ci_type_change)

        # 2. 置信区间参数框架 (动态生成)
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.X, pady=10)

        # 3. 置信水平 (1 - alpha)
        ttk.Label(self.control_frame, text="置信水平:").pack(anchor=tk.W, pady=(10, 2))
        self.confidence_var = tk.DoubleVar(value=0.95)
        confidence_scale = ttk.Scale(self.control_frame, from_=0.8, to=0.99, variable=self.confidence_var,
                                     orient=tk.HORIZONTAL, command=self.update_confidence_display_label_only)
        confidence_scale.pack(fill=tk.X)
        confidence_scale.bind("<ButtonRelease-1>", lambda event: self.calculate_and_plot())
        self.confidence_label = ttk.Label(self.control_frame, text=f"置信水平 = {self.confidence_var.get():.2f} ({(self.confidence_var.get()*100):.0f}%)")
        self.confidence_label.pack(anchor=tk.W)

        # 4. 锁定视图按钮
        self.lock_view_var = tk.BooleanVar(value=False)
        lock_button = ttk.Checkbutton(self.control_frame, text="锁定视图 (仅更新结果)",
                                      variable=self.lock_view_var, command=self.calculate_and_plot)
        lock_button.pack(anchor=tk.W, pady=(10, 5))

        # --- Initialization ---
        self.current_params = {}
        self._after_id = None
        self.create_ci_params()
        self.master.after(1, self.calculate_and_plot)

    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 添加理论知识按钮
        theory_button = ttk.Button(
            button_frame, 
            text="置信区间理论知识", 
            command=self.show_theory
        )
        theory_button.pack(fill=tk.X, pady=5)

    def update_confidence_display_label_only(self, value):
        """仅更新置信水平显示标签 (用于滑块拖动时)"""
        conf = self.confidence_var.get()
        self.confidence_label.config(text=f"置信水平 = {conf:.2f} ({(conf*100):.0f}%)")
        # DO NOT trigger full recalculation here

    def update_confidence_display(self, value):
        """更新置信水平显示标签并重新计算 (保留此方法以防其他地方调用)"""
        self.update_confidence_display_label_only(value)
        self.calculate_and_plot()

    def on_ci_type_change(self, event):
        """切换置信区间类型时，重新创建参数输入控件并计算"""
        self.create_ci_params()
        self.calculate_and_plot()

    def create_ci_params(self):
        """根据选择的置信区间类型动态创建参数输入控件"""
        # 清除旧控件和参数
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.current_params.clear()

        ci_type = self.ci_type_var.get()

        if ci_type == "均值 (总体方差未知, t分布)":
            self.add_param("样本均值 (x̄):", tk.DoubleVar(value=50.0), 0, 100)
            self.add_param("样本标准差 (s):", tk.DoubleVar(value=10.0), 0.1, 50)
            self.add_param("样本量 (n):", tk.IntVar(value=30), 2, 200, is_int=True)
        elif ci_type == "均值 (总体方差已知, Z分布)":
            self.add_param("样本均值 (x̄):", tk.DoubleVar(value=50.0), 0, 100)
            self.add_param("总体标准差 (σ):", tk.DoubleVar(value=10.0), 0.1, 50)
            self.add_param("样本量 (n):", tk.IntVar(value=30), 2, 200, is_int=True)
        elif ci_type == "比例 (正态近似)":
            self.add_param("样本成功次数 (x):", tk.IntVar(value=60), 0, 200, is_int=True)
            self.add_param("样本量 (n):", tk.IntVar(value=100), 1, 500, is_int=True)
            # 检查 np >= 10 和 n(1-p) >= 10 的条件可以在计算时进行

    def add_param(self, label_text, var, from_, to, is_int=False):
        """辅助函数：添加标签、滑块和输入框"""
        frame = ttk.Frame(self.param_frame)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)

        entry = ttk.Entry(frame, width=8, textvariable=var)
        entry.pack(side=tk.RIGHT, padx=5)
        entry.bind("<KeyRelease>", lambda event, v=var, e=entry: self.debounce_entry_update(v, e))

        scale = ttk.Scale(frame, from_=from_, to=to, variable=var,
                          orient=tk.HORIZONTAL,
                          command=lambda val, v=var, e=entry: self.update_entry_from_scale(v, e, val))
        scale.bind("<ButtonRelease-1>", lambda event: self.calculate_and_plot())
        scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        param_key = label_text.split('(')[0].strip()
        self.current_params[param_key] = var

    def update_entry_from_scale(self, var, entry_widget, value_str):
        """当滑块移动时，更新对应的输入框内容"""
        try:
            value = float(value_str)
            if isinstance(var, tk.IntVar):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(int(value)))
            else:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, f"{value:.2f}")
        except ValueError:
            pass

    def debounce_entry_update(self, var, entry_widget):
        """延迟更新，避免在输入过程中频繁触发计算"""
        if self._after_id:
            self.master.after_cancel(self._after_id)

        self._after_id = self.master.after(500, lambda v=var, e=entry_widget: self.update_var_from_entry_and_plot(v, e))

    def update_var_from_entry_and_plot(self, var, entry_widget):
        """从输入框更新变量并触发重新计算和绘图"""
        try:
            value_str = entry_widget.get()
            if isinstance(var, tk.IntVar):
                value = int(value_str)
            else:
                value = float(value_str)
            var.set(value)
            self.calculate_and_plot()
        except ValueError:
            print(f"Invalid input: {value_str}")

    def calculate_and_plot(self):
        """执行置信区间的计算和绘图"""
        is_locked = self.lock_view_var.get() # Get lock state

        try:
            # --- 获取参数 ---
            ci_type = self.ci_type_var.get()
            confidence = self.confidence_var.get()
            params = {key: var.get() for key, var in self.current_params.items()}

            # --- 初始化变量 ---
            lower_bound, upper_bound, center, margin_error = None, None, None, None
            dist = None
            df = None
            plot_center = None
            plot_scale = None
            dist_name = ""

            # --- 根据类型计算 ---
            if ci_type == "均值 (总体方差未知, t分布)":
                x_bar = params.get("样本均值")
                s = params.get("样本标准差")
                n = params.get("样本量")
                if n is None or s is None or x_bar is None or n < 2 or s <= 0:
                    # Clear plot only if not locked
                    if not is_locked:
                        self.clear_plot()
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "请提供有效的样本均值(x̄)、样本标准差(s > 0)和样本量(n ≥ 2)。")
                    return
                df = n - 1
                dist = stats.t(df)
                se = s / math.sqrt(n) # 标准误
                crit_val = dist.ppf((1 + confidence) / 2)
                margin_error = crit_val * se
                lower_bound = x_bar - margin_error
                upper_bound = x_bar + margin_error
                center = x_bar
                plot_center = 0 # t分布中心为0
                plot_scale = 1 # 标准t分布
                dist_name = f"t 分布 (df={df})"

            elif ci_type == "均值 (总体方差已知, Z分布)":
                x_bar = params.get("样本均值")
                sigma = params.get("总体标准差")
                n = params.get("样本量")
                if n is None or sigma is None or x_bar is None or n < 1 or sigma <= 0:
                    if not is_locked: self.clear_plot() # Respect lock
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "请提供有效的样本均值(x̄)、总体标准差(σ > 0)和样本量(n ≥ 1)。")
                    return
                dist = stats.norm()
                se = sigma / math.sqrt(n) # 标准误
                crit_val = dist.ppf((1 + confidence) / 2)
                margin_error = crit_val * se
                lower_bound = x_bar - margin_error
                upper_bound = x_bar + margin_error
                center = x_bar
                plot_center = 0 # 标准正态分布中心为0
                plot_scale = 1 # 标准正态分布
                dist_name = "标准正态分布 (Z)"

            elif ci_type == "比例 (正态近似)":
                x = params.get("样本成功次数")
                n = params.get("样本量")
                if n is None or x is None or n < 1 or x < 0 or x > n:
                    if not is_locked: self.clear_plot() # Respect lock
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "请提供有效的样本成功次数(0 ≤ x ≤ n)和样本量(n ≥ 1)。")
                    return
                p_hat = x / n
                if n * p_hat < 5 or n * (1 - p_hat) < 5:
                     print(f"警告: 正态近似条件可能不满足 (np̂={n*p_hat:.1f}, n(1-p̂)={n*(1-p_hat):.1f})")

                dist = stats.norm()
                if p_hat == 0 or p_hat == 1:
                     se = 0
                     print("警告: 样本比例为0或1，标准误计算可能不准确。")
                else:
                    se = math.sqrt(p_hat * (1 - p_hat) / n)

                crit_val = dist.ppf((1 + confidence) / 2)
                margin_error = crit_val * se
                lower_bound = p_hat - margin_error
                upper_bound = p_hat + margin_error
                center = p_hat
                dist_name = "标准正态分布 (Z, 近似)"
                lower_bound = max(0, lower_bound)
                upper_bound = min(1, upper_bound)


            # --- 绘图和显示结果 ---
            if lower_bound is not None and margin_error is not None: # Ensure calculation was successful
                # Only call the plotting function if the view is NOT locked
                if not is_locked:
                    self.plot_confidence_interval(dist, df, confidence, lower_bound, upper_bound, center, margin_error, dist_name, ci_type)
                # Always display results
                self.display_results(lower_bound, upper_bound, center, margin_error, confidence, ci_type, params)
            else:
                 # 处理其他未实现的类型或错误
                 # Only clear plot if view is not locked
                 if not is_locked:
                     self.clear_plot()
                 self.result_text.delete(1.0, tk.END)
                 self.result_text.insert(tk.END, f"计算 '{ci_type}' 类型的置信区间时出错或尚未实现。")


        except Exception as e:
            messagebox.showerror("计算错误", f"发生错误: {e}")
            # Only clear plot if view is not locked
            if not is_locked:
                self.clear_plot()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"计算时发生错误: {e}") # Display error in text box too

    def plot_confidence_interval(self, dist, df, confidence, lower_bound, upper_bound, center, margin_error, dist_name, ci_type):
        """绘制置信区间图"""
        # Check lock state at the very beginning
        if self.lock_view_var.get():
            return # Skip all plotting logic if locked

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        alpha = 1 - confidence
        if df: # t分布
            crit_val = dist.ppf(1 - alpha / 2) # t 分布的临界值
            x_min = -max(4, crit_val + 1)
            x_max = max(4, crit_val + 1)
            x = np.linspace(x_min, x_max, 500)
            y = dist.pdf(x)
            plot_xlabel = "t 值"
        else: # Z分布
            crit_val = dist.ppf(1 - alpha / 2) # Z 分布的临界值
            x_min = -max(3.5, crit_val + 0.5)
            x_max = max(3.5, crit_val + 0.5)
            x = np.linspace(x_min, x_max, 500)
            y = dist.pdf(x)
            plot_xlabel = "Z 值"

        ax.plot(x, y, 'b-', label=f'{dist_name} PDF')

        # 填充置信水平对应的区域
        x_fill = np.linspace(-crit_val, crit_val, 200)
        y_fill = dist.pdf(x_fill)
        ax.fill_between(x_fill, y_fill, color='lightblue', alpha=0.7, label=f'{confidence*100:.0f}% 置信水平区域')

        # 标记临界值
        ax.axvline(-crit_val, color='r', linestyle='--', lw=1)
        ax.axvline(crit_val, color='r', linestyle='--', lw=1)
        ax.text(-crit_val, ax.get_ylim()[1]*0.05, f'{-crit_val:.2f}', ha='right', color='red')
        ax.text(crit_val, ax.get_ylim()[1]*0.05, f'{crit_val:.2f}', ha='left', color='red')

        # 添加置信区间文本 (在图下方或标题中)
        ci_text = f"{confidence*100:.0f}% 置信区间: [{lower_bound:.4f}, {upper_bound:.4f}]"
        param_name = "均值 μ" if "均值" in ci_type else "比例 p"
        ax.set_title(f"{ci_type}\n对总体{param_name}的{ci_text}", fontsize=12)

        ax.set_xlabel(plot_xlabel)
        ax.set_ylabel("概率密度")
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.6)

        # 添加第二个坐标轴显示实际值
        ax2 = ax.twiny() # 共享 Y 轴
        # 计算实际值的刻度位置
        tick_function = lambda t: center + t * margin_error / crit_val if crit_val != 0 else center
        # 设置刻度
        t_ticks = ax.get_xticks()
        ax2.set_xticks(t_ticks) # 使用与下方相同的物理位置
        ax2.set_xbound(ax.get_xbound())
        ax2.set_xticklabels([f"{tick_function(t):.2f}" for t in t_ticks])
        ax2.set_xlabel(f"样本统计量 ({'x̄' if '均值' in ci_type else 'p̂'}) 及置信区间", fontsize=10)

        # 标记中心点和区间边界的实际值
        ax2.plot(0, dist.pdf(0), 'go', markersize=8, label=f"样本中心 = {center:.4f}") # 标记中心点 (t=0 或 Z=0)
        ax2.axvline(0, color='g', linestyle='-', lw=1.5)
        # 标记置信区间边界的实际值
        ax2.axvline(-crit_val, color='purple', linestyle=':', lw=1.5)
        ax2.axvline(crit_val, color='purple', linestyle=':', lw=1.5)
        ax2.text(-crit_val, ax.get_ylim()[1]*0.15, f'下限:{lower_bound:.3f}', ha='right', color='purple')
        ax2.text(crit_val, ax.get_ylim()[1]*0.15, f'上限:{upper_bound:.3f}', ha='left', color='purple')

        self.fig.tight_layout() # 调整布局防止标签重叠
        self.canvas.draw_idle() # Use draw_idle() for better responsiveness


    def display_results(self, lower_bound, upper_bound, center, margin_error, confidence, ci_type, params):
        """在文本框中显示计算结果"""
        self.result_text.delete(1.0, tk.END)
        result_text = f"置信区间类型: {ci_type}\n"
        result_text += f"置信水平: {confidence:.2f} ({(confidence*100):.0f}%)\n"
        result_text += "输入参数:\n"
        for key, val in params.items():
             result_text += f"  - {key}: {val}\n"
        result_text += "------------------------------------\n"

        param_symbol = "μ" if "均值" in ci_type else "p"
        stat_symbol = "x̄" if "均值" in ci_type else "p̂"

        result_text += f"样本统计量 ({stat_symbol}): {center:.4f}\n"
        result_text += f"边际误差 (Margin of Error): {margin_error:.4f}\n"
        result_text += f"{confidence*100:.0f}% 置信区间 ({param_symbol}): [{lower_bound:.4f}, {upper_bound:.4f}]\n"
        result_text += "------------------------------------\n"

        interpretation = f"解释: 我们有 {confidence*100:.0f}% 的信心认为，真实的总体{param_symbol}落在区间 [{lower_bound:.4f}, {upper_bound:.4f}] 之内。"
        if "比例" in ci_type:
            interpretation += f"\n(基于样本量 n={params.get('样本量')} 和成功次数 x={params.get('样本成功次数')})"
        elif "均值" in ci_type:
             interpretation += f"\n(基于样本量 n={params.get('样本量')} 和样本均值 x̄={params.get('样本均值')}"
             if "未知" in ci_type:
                 interpretation += f", 样本标准差 s={params.get('样本标准差')})"
             else:
                 interpretation += f", 总体标准差 σ={params.get('总体标准差')})"


        result_text += interpretation + "\n"

        self.result_text.insert(tk.END, result_text)

    def clear_plot(self):
        """清除图像 (if view is not locked)"""
        # Check lock state at the very beginning
        if self.lock_view_var.get():
            return # Skip clearing if locked

        self.fig.clear()
        # 需要重新添加 subplot 否则会报错
        try:
            self.fig.add_subplot(111)
        except ValueError: 
            pass
        self.canvas.draw_idle()

    def show_theory(self):
        """显示置信区间理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 置信区间知识点内容
            sections = {
                "基本概念": """
定义：
置信区间是指由样本统计量所构造的总体参数的估计区间。在重复抽样的情况下，包含总体参数真值的区间所占的比例称为置信水平。通常用(1−α)×100%表示，其中α是显著性水平，常见的置信水平有90%、95%和99%。

例如：
对于总体均值μ的95%置信区间(a,b)，可以理解为如果从总体中重复抽取大量相同样本量的样本，并计算每个样本的置信区间，那么大约有95%的区间会包含总体均值μ的真实值。
""",
                "影响因素": """
1.样本量：
样本量越大，置信区间越窄，估计的精度越高。因为大样本能更准确地反映总体特征，减少抽样误差。

2.置信水平：
置信水平越高，置信区间越宽。这是因为要提高包含总体参数真值的概率，就需要扩大区间范围。

3.总体方差：
总体方差越大，说明数据的离散程度越大，抽样误差也越大，从而导致置信区间变宽。
""",
                "应用": """
1.参数估计：
在实际问题中，往往无法直接知道总体参数的真实值，通过抽取样本并计算置信区间，可以对总体参数进行估计。例如，在市场调研中，要估计某产品的平均满意度，通过抽取一定数量的消费者进行调查，计算出满意度的置信区间，就可以大致了解该产品在总体消费者中的平均满意度范围。

2.假设检验：
置信区间与假设检验有密切联系。可以通过置信区间来判断原假设是否成立。如果原假设中所设定的参数值不在置信区间内，那么在相应的显著性水平下，可以拒绝原假设。例如，要检验某工厂生产的零件平均长度是否为10厘米，通过样本数据计算出平均长度的置信区间为(9.8,9.9)，由于10不在该区间内，所以在相应的置信水平下，可以认为该工厂生产的零件平均长度不是10厘米。

3.质量控制：
在工业生产中，通过对产品质量指标的置信区间进行监控，可以及时发现生产过程是否出现异常。如果质量指标的置信区间超出了预设的范围，可能意味着生产设备出现故障或生产工艺需要调整。
"""
        
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "置信区间理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建置信区间理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("置信区间理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="置信区间理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")

        # 影响因素选项卡
        geometric_frame = ttk.Frame(notebook, padding=10)
        notebook.add(geometric_frame, text="影响因素")
        
        # 应用选项卡
        application_frame = ttk.Frame(notebook, padding=10)
        notebook.add(application_frame, text="应用")
        
        # 填充内容(可以复用上面sections中的内容)
        # ...此处省略内容填充代码，与之前相同...
        
        # 底部的确定按钮
        close_button = ttk.Button(main_frame, text="关闭", 
                               command=theory_window.destroy)
        close_button.pack(pady=10) 
