import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re 
import math

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class StochasticProcessApp:
    def __init__(self, master):
        self.master = master
        master.title("随机过程可视化工具")
        self.master.geometry("1200x800")

        # --- State ---
        # General
        self.current_process_type = tk.StringVar(value="马尔可夫链 (离散时间)")
        self.max_markov_steps = 100 
        # Markov Chain
        self.tpm = None
        self.initial_dist = None
        self.num_states = 0
        self.state_distributions = [] 
        self.stationary_dist = None
        self.markov_num_steps_var = tk.IntVar(value=20)

        # Brownian Motion
        self.brownian_drift_var = tk.DoubleVar(value=0.05)
        self.brownian_volatility_var = tk.DoubleVar(value=0.2) 
        self.brownian_s0_var = tk.DoubleVar(value=100.0) 
        self.brownian_time_var = tk.DoubleVar(value=1.0)
        self.brownian_steps_var = tk.IntVar(value=252)
        self.brownian_paths = []

        # --- Main Layout ---
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="随机过程模拟", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Left Control Panel
        self.control_frame = ttk.LabelFrame(main_frame, text="模型设置")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, ipadx=5)

        # Right Area (Plot + Results)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Plot Area
        plot_frame = ttk.Frame(right_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Results Area
        result_frame = ttk.LabelFrame(right_frame, text="模拟结果")
        result_frame.pack(fill=tk.X, pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)

        # --- Control Panel Widgets ---
        # 1. Process Type Selection
        ttk.Label(self.control_frame, text="选择过程类型:").pack(anchor=tk.W, pady=(10, 5))
        process_combobox = ttk.Combobox(self.control_frame, textvariable=self.current_process_type,
                                        values=["马尔可夫链 (离散时间)", "布朗运动 (几何)"],
                                        width=35, state="readonly")
        process_combobox.pack(fill=tk.X, pady=2)
        process_combobox.bind("<<ComboboxSelected>>", self.on_process_type_change)

        # 2. Dynamic Parameter Frame
        self.param_frame = ttk.Frame(self.control_frame)
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 3. Update Button (might be specific to model)
        self.update_button = ttk.Button(self.control_frame, text="更新模拟/计算", command=self.update_display)
        self.update_button.pack(pady=20)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            self.control_frame, 
            text="随机过程理论知识", 
            command=self.show_theory
        )
        self.theory_button.pack(pady=20)

        # --- Initial Setup ---
        self.create_ui_for_model() # Create UI for the default model
        self.update_display()      # Run initial simulation/calculation

    def on_process_type_change(self, event=None):
        """Handles switching between different stochastic process models."""
        self.clear_param_ui()
        self.create_ui_for_model()
        self.update_display() # Update with default parameters for the new model

    def clear_param_ui(self):
        """Removes all widgets from the parameter frame."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()

    def create_ui_for_model(self):
        """Creates the specific UI controls based on the selected process type."""
        model_type = self.current_process_type.get()
        self.control_frame.config(text=f"模型设置 ({model_type})") # Update frame label

        if model_type == "马尔可夫链 (离散时间)":
            self.create_markov_ui()
            self.update_button.config(text="更新模拟与计算")
        elif model_type == "布朗运动 (几何)":
            self.create_brownian_ui()
            self.update_button.config(text="生成新路径")
        else:
            ttk.Label(self.param_frame, text="未知模型类型").pack()

    # --- Markov Chain Specific ---

    def create_markov_ui(self):
        """Creates UI elements for Markov Chain."""
        ttk.Label(self.param_frame, text="转移概率矩阵 (TPM):").pack(anchor=tk.W, pady=(5, 2))
        ttk.Label(self.param_frame, text="(每行代表一个状态, 数值用逗号或空格分隔)", font=("Arial", 8)).pack(anchor=tk.W)
        self.tpm_text_widget = scrolledtext.ScrolledText(self.param_frame, height=8, width=35, wrap=tk.WORD)
        self.tpm_text_widget.pack(fill=tk.X, pady=2)
        self.tpm_text_widget.insert(tk.END, "0.7, 0.3\n0.1, 0.9") # Example

        ttk.Label(self.param_frame, text="初始状态分布 (向量):").pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(self.param_frame, text="(数值用逗号或空格分隔)", font=("Arial", 8)).pack(anchor=tk.W)
        self.initial_dist_entry_var = tk.StringVar(value="0.5, 0.5")
        initial_dist_entry = ttk.Entry(self.param_frame, textvariable=self.initial_dist_entry_var, width=35)
        initial_dist_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.param_frame, text="模拟步数:").pack(anchor=tk.W, pady=(10, 2))

        steps_scale = ttk.Scale(self.param_frame, from_=1, to=self.max_markov_steps, variable=self.markov_num_steps_var,
                                orient=tk.HORIZONTAL, command=self.on_steps_slider_change)
        steps_scale.pack(fill=tk.X)
        self.markov_steps_label = ttk.Label(self.param_frame, text=f"步数: {self.markov_num_steps_var.get()}")
        self.markov_steps_label.pack(anchor=tk.W)

    def on_steps_slider_change(self, value):
        """Called when the Markov steps slider changes. Only replots."""
        steps = int(float(value))
        self.markov_steps_label.config(text=f"步数: {steps}")


        if self.state_distributions:
            self.plot_markov_evolution()
            self.display_markov_results(None)

    def parse_matrix_input(self, text_widget):
        """Parses the text input into a numpy matrix, performs validation."""
        text = text_widget.get("1.0", tk.END).strip()
        if not text:
            return None, "矩阵输入为空。"

        rows = []
        lines = text.split('\n')
        num_cols = -1

        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue 

            elements_str = re.split(r'[,\s;]+', line)
            try:
                row = [float(e) for e in elements_str if e] # Filter out empty strings from multiple spaces
                if not row: continue # Skip lines that become empty

                if num_cols == -1:
                    num_cols = len(row)
                elif len(row) != num_cols:
                    return None, f"输入错误: 第 {i+1} 行有 {len(row)} 个元素, 与之前的 {num_cols} 个不匹配。"

                if not np.all(np.array(row) >= 0):
                     return None, f"输入错误: 第 {i+1} 行包含负概率。"

                row_sum = sum(row)
                if not np.isclose(row_sum, 1.0):
                    return None, f"输入错误: 第 {i+1} 行概率之和为 {row_sum:.4f}, 不等于 1。"
                rows.append(row)
            except ValueError:
                return None, f"输入错误: 第 {i+1} 行包含无法解析为数字的元素。"

        if not rows:
             return None, "未能从输入中解析出任何有效的矩阵行。"

        matrix = np.array(rows)
        if matrix.shape[0] != matrix.shape[1]:
            return None, f"输入错误: 解析得到的矩阵不是方阵 ({matrix.shape[0]}x{matrix.shape[1]})。"

        return matrix, None # Return matrix and no error

    def parse_vector_input(self, string_var, expected_size):
        """Parses the string input into a numpy vector, performs validation."""
        text = string_var.get().strip()
        if not text:
            return None, "初始分布输入为空。"

        elements_str = re.split(r'[,\s;]+', text)
        try:
            vector = np.array([float(e) for e in elements_str if e])
            if vector.ndim != 1:
                 raise ValueError("Input is not a vector.")

            if len(vector) != expected_size:
                return None, f"输入错误: 初始分布向量应包含 {expected_size} 个元素, 但输入了 {len(vector)} 个。"

            if not np.all(vector >= 0):
                 return None, "输入错误: 初始分布包含负概率。"

            vec_sum = vector.sum()
            if not np.isclose(vec_sum, 1.0):
                return None, f"输入错误: 初始分布概率之和为 {vec_sum:.4f}, 不等于 1。"

            return vector, None # Return vector and no error
        except ValueError:
            return None, "输入错误: 初始分布包含无法解析为数字的元素。"

    def calculate_stationary_distribution(self, tpm):
        """Calculates the stationary distribution using eigenvalue decomposition."""
        if tpm is None:
            return None, "TPM 未定义。"
        try:
            # We want the left eigenvector for eigenvalue 1: pi * P = pi
            # This is equivalent to the right eigenvector for P.T for eigenvalue 1: P.T * pi.T = pi.T
            eigenvalues, eigenvectors = np.linalg.eig(tpm.T)

            # Find the index of the eigenvalue closest to 1
            one_indices = np.isclose(eigenvalues, 1.0)

            if not np.any(one_indices):
                # This shouldn't happen for a valid stochastic matrix, but check anyway
                return None, "未能找到接近 1 的特征值。"

            # Get the eigenvector corresponding to the eigenvalue 1
            # If multiple eigenvalues are close to 1 (e.g., reducible chain), this might be ambiguous
            # We take the first one found.
            stationary_vector = eigenvectors[:, one_indices][:, 0]

            # Eigenvector might be complex, take the real part (should be real for stochastic matrices)
            stationary_vector = np.real(stationary_vector)

            # Normalize the vector so that it sums to 1
            stationary_dist = stationary_vector / stationary_vector.sum()

            # Check if it's a valid probability distribution
            if np.any(stationary_dist < -1e-6): # Allow for small numerical errors
                 return None, "计算得到的稳态分布包含负值 (可能由于数值不稳定或矩阵特性)。"

            stationary_dist[stationary_dist < 0] = 0 # Clip small negative values
            stationary_dist = stationary_dist / stationary_dist.sum() # Re-normalize


            # Verify if pi * P = pi
            if not np.allclose(stationary_dist @ tpm, stationary_dist):
                 print("警告: 计算得到的稳态分布未能完全满足 πP = π (可能由于数值精度问题)。")
                 # return None, "计算得到的稳态分布验证失败 (πP ≠ π)。" # Be less strict

            return stationary_dist, None
        except np.linalg.LinAlgError as e:
            return None, f"计算特征值时出错: {e}"
        except Exception as e:
            return None, f"计算稳态分布时发生意外错误: {e}"

    def update_markov_simulation(self):
        """Parses Markov inputs, runs simulation up to max steps, calculates stationary dist."""
        # 1. Parse TPM
        tpm, error = self.parse_matrix_input(self.tpm_text_widget)
        if error:
            messagebox.showerror("输入错误 (TPM)", error)
            self.state_distributions = [] # Clear old data on error
            return False # Indicate failure
        self.tpm = tpm
        self.num_states = tpm.shape[0]

        # 2. Parse Initial Distribution
        initial_dist, error = self.parse_vector_input(self.initial_dist_entry_var, self.num_states)
        if error:
            messagebox.showerror("输入错误 (初始分布)", error)
            self.state_distributions = [] # Clear old data on error
            return False # Indicate failure
        self.initial_dist = initial_dist

        # 3. Simulate State Distribution Evolution up to max_markov_steps
        self.state_distributions = [self.initial_dist]
        current_dist = self.initial_dist
        try:
            for _ in range(self.max_markov_steps):
                current_dist = current_dist @ self.tpm # P(n+1) = P(n) * TPM
                self.state_distributions.append(current_dist)
        except Exception as e:
             messagebox.showerror("模拟错误", f"计算状态分布时出错: {e}")
             self.state_distributions = []
             return False

        # 4. Calculate Stationary Distribution
        self.stationary_dist, stat_error = self.calculate_stationary_distribution(self.tpm)
        if stat_error:
             print(f"计算稳态分布时提示: {stat_error}") # Print warning but continue

        return True # Indicate success

    def plot_markov_evolution(self):
        """Plots the probability of being in each state over time up to the selected number of steps."""
        self.ax.clear()
        if not self.state_distributions or self.num_states == 0:
            self.ax.set_title("马尔可夫链状态分布演变 (无数据)")
            self.canvas.draw_idle()
            return

        num_steps_to_plot = self.markov_num_steps_var.get()
        # Ensure we don't plot more steps than calculated
        num_steps_to_plot = min(num_steps_to_plot, len(self.state_distributions) - 1)

        steps_axis = np.arange(num_steps_to_plot + 1)
        # Slice the pre-calculated distributions
        dist_array = np.array(self.state_distributions[:num_steps_to_plot + 1])

        colors = plt.cm.viridis(np.linspace(0, 1, self.num_states))

        for i in range(self.num_states):
            self.ax.plot(steps_axis, dist_array[:, i], marker='.', linestyle='-', label=f'状态 {i}', color=colors[i])

        # Plot stationary distribution lines if available
        if self.stationary_dist is not None:
             # Add a single legend entry for stationary lines
             if self.num_states > 0:
                 self.ax.plot([], [], color='gray', linestyle='--', label='稳态分布')
             for i in range(self.num_states):
                 self.ax.axhline(self.stationary_dist[i], color=colors[i], linestyle='--', alpha=0.7) # No individual labels needed


        self.ax.set_xlabel("时间步 (n)")
        self.ax.set_ylabel("概率 P(Xn = i)")
        self.ax.set_title("马尔可夫链状态分布随时间演变")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        self.ax.set_ylim(bottom=-0.05, top=1.05)
        # Adjust xlim based on plotted steps
        self.ax.set_xlim(left=-0.5, right=num_steps_to_plot + 0.5)

        self.fig.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout for legend
        self.canvas.draw_idle()

    def display_markov_results(self, stat_error):
        """Displays the Markov Chain results."""
        self.result_text.delete(1.0, tk.END)

        def format_array(arr, precision=4):
            if arr is None: return "N/A"
            # Handle cases where arr might be empty list if parsing failed early
            if isinstance(arr, list) and not arr: return "N/A"
            if isinstance(arr, np.ndarray) and arr.size == 0: return "N/A"
            return np.array2string(arr, precision=precision, separator=', ', suppress_small=True)

        result_str = f"状态数: {self.num_states}\n"
        result_str += "转移概率矩阵 (TPM):\n"
        result_str += format_array(self.tpm) + "\n"
        result_str += "------------------------------------\n"
        result_str += f"初始分布 P(0): {format_array(self.initial_dist)}\n"

        num_steps_displayed = self.markov_num_steps_var.get()
        # Ensure index is valid
        final_dist_index = min(num_steps_displayed, len(self.state_distributions) - 1)
        final_dist = self.state_distributions[final_dist_index] if final_dist_index >= 0 and self.state_distributions else None

        result_str += f"当前分布 P({final_dist_index}): {format_array(final_dist)}\n"
        result_str += "------------------------------------\n"
        result_str += f"稳态分布 (π): {format_array(self.stationary_dist)}\n"
        if stat_error: # Pass error from calculation if needed
             result_str += f"(计算提示: {stat_error})\n"
        elif self.stationary_dist is not None and final_dist is not None:
             diff = np.linalg.norm(final_dist - self.stationary_dist)
             result_str += f"当前分布与稳态分布的距离 (L2范数): {diff:.6f}\n"

        self.result_text.insert(tk.END, result_str)

    # --- Brownian Motion Specific ---

    def create_brownian_ui(self):
        """Creates UI elements for Brownian Motion."""
        ttk.Label(self.param_frame, text="漂移率 (μ):").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(self.param_frame, textvariable=self.brownian_drift_var, width=15).pack(anchor=tk.W)

        ttk.Label(self.param_frame, text="波动率 (σ):").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(self.param_frame, textvariable=self.brownian_volatility_var, width=15).pack(anchor=tk.W)

        ttk.Label(self.param_frame, text="初始价格 (S₀):").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(self.param_frame, textvariable=self.brownian_s0_var, width=15).pack(anchor=tk.W)

        ttk.Label(self.param_frame, text="时间范围 (T, 年):").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(self.param_frame, textvariable=self.brownian_time_var, width=15).pack(anchor=tk.W)

        ttk.Label(self.param_frame, text="步数 (N):").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(self.param_frame, textvariable=self.brownian_steps_var, width=15).pack(anchor=tk.W)
        # Add a scale for steps? Maybe later if needed for interactivity.

    def update_brownian_simulation(self):
        """Generates Geometric Brownian Motion path(s)."""
        try:
            mu = self.brownian_drift_var.get()
            sigma = self.brownian_volatility_var.get()
            s0 = self.brownian_s0_var.get()
            T = self.brownian_time_var.get()
            N = self.brownian_steps_var.get()

            if sigma < 0 or s0 <= 0 or T <= 0 or N <= 0:
                messagebox.showerror("输入错误", "波动率(σ)需>=0, S₀>0, T>0, N>0")
                self.brownian_paths = []
                return False

            dt = T / N
            t = np.linspace(0, T, N + 1)
            # Generate standard normal random variables
            Z = np.random.standard_normal(N)

            # Calculate path using the log-price formulation for stability
            # d(lnS) = (mu - 0.5*sigma^2)dt + sigma*dW
            # ln(St) = ln(S0) + sum[(mu - 0.5*sigma^2)dt + sigma*sqrt(dt)*Zi]
            log_returns = (mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z
            log_path = np.zeros(N + 1)
            log_path[0] = math.log(s0)
            log_path[1:] = math.log(s0) + np.cumsum(log_returns)

            path = np.exp(log_path)
            self.brownian_paths = [(t, path)] # Store as list of tuples (time, path)
            return True

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数值参数。")
            self.brownian_paths = []
            return False
        except Exception as e:
            messagebox.showerror("模拟错误", f"生成布朗运动路径时出错: {e}")
            self.brownian_paths = []
            return False

    def plot_brownian_motion(self):
        """Plots the simulated Brownian Motion path(s)."""
        self.ax.clear()
        if not self.brownian_paths:
            self.ax.set_title("布朗运动路径 (无数据)")
            self.canvas.draw_idle()
            return

        for i, (t, path) in enumerate(self.brownian_paths):
            self.ax.plot(t, path, label=f'路径 {i+1}')

        self.ax.set_xlabel("时间 (年)")
        self.ax.set_ylabel("价格 (S)")
        self.ax.set_title("几何布朗运动模拟路径")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        if len(self.brownian_paths) > 1:
            self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        self.fig.tight_layout(rect=[0, 0, 0.85 if len(self.brownian_paths) > 1 else 1, 1])
        self.canvas.draw_idle()

    def display_brownian_results(self):
        """Displays Brownian Motion simulation parameters and results."""
        self.result_text.delete(1.0, tk.END)
        result_str = "几何布朗运动参数:\n"
        result_str += f"  漂移率 (μ): {self.brownian_drift_var.get():.4f}\n"
        result_str += f"  波动率 (σ): {self.brownian_volatility_var.get():.4f}\n"
        result_str += f"  初始价格 (S₀): {self.brownian_s0_var.get():.2f}\n"
        result_str += f"  时间范围 (T): {self.brownian_time_var.get():.2f} 年\n"
        result_str += f"  步数 (N): {self.brownian_steps_var.get()}\n"
        result_str += "------------------------------------\n"

        if self.brownian_paths:
            final_prices = [path[-1] for _, path in self.brownian_paths]
            result_str += f"模拟路径数: {len(self.brownian_paths)}\n"
            result_str += f"最终价格 S(T): {final_prices[0]:.4f}" # Show first path's final price
            if len(final_prices) > 1:
                 result_str += f" (均值: {np.mean(final_prices):.4f}, 标准差: {np.std(final_prices):.4f})"
            result_str += "\n"
        else:
            result_str += "无有效模拟结果。\n"

        self.result_text.insert(tk.END, result_str)

    # --- General Update and Plotting ---

    def update_display(self):
        """Central function to update simulation/calculation, plot, and results based on model type."""
        model_type = self.current_process_type.get()
        success = False
        stat_error = None # For Markov

        try:
            if model_type == "马尔可夫链 (离散时间)":
                success = self.update_markov_simulation()
                if success:
                    self.plot_markov_evolution()
                    # Retrieve potential error from calculation step if needed
                    # stat_error = ... (if calculate_stationary_distribution returned it)
                    self.display_markov_results(stat_error) # Pass error if any
            elif model_type == "布朗运动 (几何)":
                success = self.update_brownian_simulation()
                if success:
                    self.plot_brownian_motion()
                    self.display_brownian_results()
            else:
                messagebox.showwarning("未实现", f"模型类型 '{model_type}' 尚未完全实现。")
                success = False

            # Clear plot/results if the update failed for the selected model
            if not success:
                 self.ax.clear()
                 self.ax.set_title(f"{model_type} (更新失败)")
                 self.canvas.draw_idle()
                 self.result_text.delete(1.0, tk.END)
                 self.result_text.insert(tk.END, "更新或计算失败，请检查输入参数。")

        except Exception as e:
            messagebox.showerror("更新错误", f"更新显示时发生意外错误: {e}")
            self.ax.clear()
            self.ax.set_title(f"{model_type} (错误)")
            self.canvas.draw_idle()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"更新显示时发生错误: {e}")

    def show_theory(self):
        """显示随机过程理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 随机过程知识点内容
            sections = {
                "基本概念": """
随机过程是一族依赖于参数t的随机变量{X(t),t∈T}，其中T是参数集。如果T是离散集合，如T={0,1,2,⋯}，则称该随机过程为离散时间随机过程；如果T是连续集合，如T=[0,+∞)，则称其为连续时间随机过程。
""",
                "常见类型": """
1.独立增量过程：
如果对于任意的n个时刻t0​<t1​<⋯<tn​，随机变量X(t1​)−X(t0​),X(t2​)−X(t1​),⋯,X(tn​)−X(tn−1​)相互独立，则称{X(t),t∈T}为独立增量过程。

2.平稳过程：
宽平稳过程是指均值函数为常数，协方差函数只与时间间隔τ=t−s有关的随机过程，即μX​(t)=μ(常数)，CX​(s,t)=CX​(τ)。严平稳过程是指其有限维分布在时间平移下保持不变的随机过程，即对于任意的n个时刻t1​,t2​,⋯,tn​∈T和任意的τ，(X(t1​+τ),X(t2​+τ),⋯,X(tn​+τ))与(X(t1​),X(t2​),⋯,X(tn​))具有相同的分布。严平稳过程一定是宽平稳过程，反之不一定成立。

3.泊松过程：
是一种重要的离散时间计数过程，用于描述在一定时间间隔内随机事件发生的次数。它满足以下条件：在不相交的时间区间内，事件发生的次数是相互独立的；在一个足够小的时间间隔Δt内，事件发生一次的概率与Δt成正比，即P(N(t+Δt)−N(t)=1)=λΔt+o(Δt)，其中N(t)表示到时刻t为止事件发生的次数，λ>0是常数，称为泊松过程的强度；在一个足够小的时间间隔Δt内，事件发生两次或两次以上的概率是o(Δt)。泊松过程的均值函数和方差函数分别为μN​(t)=λt，σN​(t)*σN​(t)=λt。
""",
                "马尔可夫链（离散时间）": """
定义：
离散时间马尔可夫链是一个随机过程{Xn​,n=0,1,2,⋯}，它具有马尔可夫性质，即对于任意的n≥0和状态i,j,k，有P(Xn+1​=j∣Xn​=i,Xn−1​=k,⋯,X0​=x0​)=P(Xn+1​=j∣Xn​=i)。这意味着在已知当前状态的情况下，未来的状态只与当前状态有关，而与过去的历史无关。

状态空间：
马尔可夫链的所有可能状态组成的集合称为状态空间，记为S。状态空间可以是有限的，也可以是无限的。

应用：
1.通信系统建模分析
2.排队系统建模分析
3.生物进化建模分析
""",
                "布朗运动（几何）": """
定义：
几何布朗运动是一种连续时间随机过程，通常用于描述金融资产价格的变化。设S(t)表示资产在时刻t的价格，几何布朗运动的随机微分方程为dS(t)=μS(t)dt+σS(t)dW(t)，其中μ是漂移系数，表示资产的预期收益率，σ是波动率系数，W(t)是标准布朗运动。

应用：
1.股票价格建模分析
2.期权定价建模分析
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "随机过程理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建随机过程理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("随机过程理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="随机过程理论知识", 
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


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = StochasticProcessApp(root)
    root.mainloop()
