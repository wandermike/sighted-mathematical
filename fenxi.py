import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re
import scipy.stats as stats
import os

# 配置 Matplotlib，使中文正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# Default data to show on startup
DEFAULT_DATA = "10.5 12.1 9.8 11.5 13.2 10.9 11.8 12.5 10.1 11.3\n" \
               "14.0 8.9 11.0 12.8 10.7 11.9 13.5 9.5 12.2 11.6"

class AnalysisApp:
    def __init__(self, master):
        self.master = master
        master.title("统计分析工具")
        self.master.geometry("1200x800")

        # --- State ---
        self.data = np.array([])
        self.last_loaded_file = None

        # --- Main Layout ---
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="统计分析", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Top Control Area (Data Input + Action Buttons)
        control_frame = ttk.LabelFrame(main_frame, text="数据输入与操作")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="输入数据 (数值，用空格、逗号或换行分隔) 或从文件加载:").pack(anchor=tk.W, padx=5, pady=(5,2))
        self.data_input_text = scrolledtext.ScrolledText(control_frame, height=8, width=80, wrap=tk.WORD) # Reduced height slightly
        self.data_input_text.pack(fill=tk.X, padx=5, pady=2)
        self.data_input_text.insert("1.0", DEFAULT_DATA)

        # File format info label
        file_info_label = ttk.Label(control_frame,
                                    text="可加载 .txt 或 .csv 文件。文件应包含数值，用空格、逗号或换行分隔。\n所有数值将被视为单个数据集。",
                                    font=("Arial", 8), foreground="grey")
        file_info_label.pack(anchor=tk.W, padx=5, pady=(0, 5))


        # --- Action Buttons Frame ---
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=5) # Reduced padding

        self.load_button = ttk.Button(button_frame, text="从文件加载", command=self.load_data_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = ttk.Button(button_frame, text="生成随机数据", command=self.generate_random_data)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.clear_input_button = ttk.Button(button_frame, text="清空输入", command=self.clear_input_data)
        self.clear_input_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = ttk.Button(button_frame, text="计算并绘图", command=self.perform_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        # 添加理论知识按钮
        self.theory_button = ttk.Button(
            button_frame, 
            text="统计分析理论知识", 
            command=self.show_theory
        )
        self.theory_button.pack(side=tk.LEFT, padx=5)

        # Bottom Area (Results + Plot)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Results Area (Using Treeview)
        result_frame = ttk.LabelFrame(bottom_frame, text="描述性统计结果")
        result_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=5)

        # Create Treeview
        self.result_tree = ttk.Treeview(result_frame, columns=("Statistic", "Value"), show="headings", height=15)
        self.result_tree.heading("Statistic", text="统计量")
        self.result_tree.heading("Value", text="值")
        self.result_tree.column("Statistic", anchor=tk.W, width=150)
        self.result_tree.column("Value", anchor=tk.E, width=150) # Align values to the right

        # Add Scrollbar to Treeview
        tree_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=tree_scrollbar.set)

        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


        # Plot Area (using subplots for histogram and boxplot)
        plot_frame = ttk.Frame(bottom_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Use subplots for two plots
        self.fig = Figure(figsize=(8, 8))
        self.ax_hist = self.fig.add_subplot(2, 1, 1) # Top plot: Histogram
        self.ax_box = self.fig.add_subplot(2, 1, 2) # Bottom plot: Box Plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Initial Setup ---
        self.perform_analysis() # Analyze default data at startup

    def load_data_from_file(self):
        """Opens a file dialog and loads numerical data from a text or CSV file."""
        filepath = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("文本文件", "*.txt"), ("CSV 文件", "*.csv"), ("所有文件", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read the whole file content, assuming numbers are separated
                # by typical delimiters (space, comma, newline).
                # This simple approach works for single-column files or
                # files where all values are meant to be treated as one dataset.
                content = f.read()

            self.data_input_text.delete("1.0", tk.END)
            self.data_input_text.insert("1.0", content)
            self.last_loaded_file = filepath
            messagebox.showinfo("加载成功", f"已从 {os.path.basename(filepath)} 加载数据。\n请点击 '计算并绘图' 进行分析。")

        except Exception as e:
            messagebox.showerror("文件读取错误", f"无法读取文件 '{os.path.basename(filepath)}':\n{e}")
            self.last_loaded_file = None

    def generate_random_data(self):
        """Generates random normal data and puts it in the input box."""
        try:
            # Parameters for random data (can be made configurable later)
            num_samples = 50
            mean = 15.0
            std_dev = 2.5

            # Generate data
            random_data = np.random.normal(loc=mean, scale=std_dev, size=num_samples)

            # Format data as string (space-separated, rounded)
            data_string = " ".join([f"{x:.2f}" for x in random_data])

            # Update input text widget
            self.data_input_text.delete("1.0", tk.END)
            self.data_input_text.insert("1.0", data_string)
            self.last_loaded_file = None # Clear loaded file tracker

            # Optionally, trigger analysis immediately
            self.perform_analysis()
            messagebox.showinfo("生成成功", f"已生成 {num_samples} 个正态分布 (μ={mean}, σ={std_dev}) 的随机数。")

        except Exception as e:
            messagebox.showerror("生成错误", f"生成随机数据时出错: {e}")

    def clear_input_data(self):
        """Clears the data input text widget."""
        self.data_input_text.delete("1.0", tk.END)
        self.data = np.array([])
        self.last_loaded_file = None
        # Clear results/plot when clearing input
        self.clear_results_and_plot()

    def parse_data(self):
        """Parses numerical data from the input text widget."""
        raw_text = self.data_input_text.get("1.0", tk.END).strip()
        if not raw_text:
            self.data = np.array([])
            self.clear_results_and_plot()
            return False

        # Split by spaces, commas, or newlines, filter out empty strings
        potential_numbers = re.split(r'[\s,]+', raw_text)
        numbers = [item for item in potential_numbers if item]

        try:
            self.data = np.array([float(num) for num in numbers])
            if self.data.size == 0:
                 messagebox.showwarning("输入警告", "未找到有效的数值数据。")
                 self.clear_results_and_plot()
                 return False
            return True
        except ValueError:
            messagebox.showerror("输入错误", "数据包含非数值内容，请检查输入。")
            self.data = np.array([])
            self.clear_results_and_plot()
            return False

    def calculate_descriptive_stats(self):
        """Calculates basic descriptive statistics for the stored data."""
        if self.data.size == 0:
            return None

        stats_dict = {}
        try:
            stats_dict['样本量'] = len(self.data)
            stats_dict['均值'] = np.mean(self.data)
            stats_dict['中位数'] = np.median(self.data)
            stats_dict['标准差'] = np.std(self.data, ddof=1) # Sample standard deviation
            stats_dict['方差'] = np.var(self.data, ddof=1)   # Sample variance
            stats_dict['最小值'] = np.min(self.data)
            stats_dict['最大值'] = np.max(self.data)
            stats_dict['范围'] = np.ptp(self.data) # Range (max - min)
            q1, q2, q3 = np.percentile(self.data, [25, 50, 75])
            stats_dict['第一四分位数 (Q1)'] = q1
            stats_dict['第二四分位数 (中位数)'] = q2
            stats_dict['第三四分位数 (Q3)'] = q3
            stats_dict['四分位距 (IQR)'] = q3 - q1
            # Optional: Skewness and Kurtosis
            stats_dict['偏度'] = stats.skew(self.data)
            stats_dict['峰度'] = stats.kurtosis(self.data) # Fisher's definition (normal=0)

            return stats_dict
        except Exception as e:
            messagebox.showerror("计算错误", f"计算统计量时出错: {e}")
            return None

    def display_stats(self, stats_dict):
        """Displays the calculated statistics in the result Treeview."""
        # Clear previous results
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        if stats_dict:
            # Add file source if available
            if self.last_loaded_file:
                 self.result_tree.insert("", tk.END, values=("数据来源", os.path.basename(self.last_loaded_file)))
                 self.result_tree.insert("", tk.END, values=("-"*15, "-"*15)) # Separator

            # Display count first
            count = stats_dict.pop('样本量')
            self.result_tree.insert("", tk.END, values=("样本量 (N)", f"{int(count)}")) # Format as integer
            self.result_tree.insert("", tk.END, values=("-"*15, "-"*15)) # Separator

            # Add remaining stats
            for key, value in stats_dict.items():
                # Format based on magnitude or type if needed
                if abs(value) > 1e4 or (abs(value) < 1e-3 and value != 0):
                    formatted_value = f"{value:.4e}"
                else:
                    formatted_value = f"{value:.4f}"
                self.result_tree.insert("", tk.END, values=(key, formatted_value))
        else:
            self.result_tree.insert("", tk.END, values=("状态", "无数据或计算失败"))

    def plot_data(self):
        """Plots histogram and box plot for the stored data."""
        self.ax_hist.clear()
        self.ax_box.clear()

        if self.data.size == 0:
            self.ax_hist.set_title("直方图 (无数据)")
            self.ax_box.set_title("箱线图 (无数据)")
            self.canvas.draw_idle()
            return

        try:
            # Histogram
            self.ax_hist.hist(self.data, bins='auto', color='skyblue', edgecolor='black', alpha=0.7)
            self.ax_hist.set_title(f"数据直方图 (N={len(self.data)})")
            self.ax_hist.set_xlabel("值")
            self.ax_hist.set_ylabel("频数")
            self.ax_hist.grid(axis='y', linestyle='--', alpha=0.7)

            # Box Plot
            self.ax_box.boxplot(self.data, vert=False, patch_artist=True, showmeans=True) # Horizontal box plot
            self.ax_box.set_title("数据箱线图")
            self.ax_box.set_xlabel("值")
            self.ax_box.set_yticks([]) # Hide y-axis ticks for horizontal box plot
            self.ax_box.grid(axis='x', linestyle='--', alpha=0.7)

            self.fig.tight_layout() # Adjust layout to prevent overlap
            self.canvas.draw_idle()

        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制图表时出错: {e}")
            self.ax_hist.set_title("直方图 (错误)")
            self.ax_box.set_title("箱线图 (错误)")
            self.canvas.draw_idle()

    def perform_analysis(self):
        """Parses data, calculates stats, displays results, and plots."""
        if self.parse_data():
            stats_dict = self.calculate_descriptive_stats()
            self.display_stats(stats_dict)
            self.plot_data()

    def clear_results_and_plot(self):
        """Clears the results Treeview and the plots."""
        # Clear Treeview
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # Clear plots
        self.ax_hist.clear()
        self.ax_box.clear()
        self.ax_hist.set_title("直方图")
        self.ax_box.set_title("箱线图")
        self.ax_hist.text(0.5, 0.5, '输入数据或加载文件后点击 "计算并绘图"', ha='center', va='center', transform=self.ax_hist.transAxes, color='grey')
        self.ax_box.text(0.5, 0.5, '', ha='center', va='center', transform=self.ax_box.transAxes)
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def show_theory(self):
        """显示统计分析理论知识"""
        try:
            # 如果已经创建了knowledge_framework.py模块
            from knowledge_framework import KnowledgeFrame
            
            # 统计分析知识点内容
            sections = {
                "基本概念": """
总体与样本
1.总体：
是研究对象的整个集合，包含了所有感兴趣的个体或观测值。例如，要研究某城市所有居民的收入情况，那么该城市的所有居民就构成了总体。
2.样本：
是从总体中抽取的一部分用于代表总体的子集。通过对样本的观察和分析来推断总体的特征。比如，从该城市中随机抽取1000名居民的收入数据，这1000名居民的收入信息就组成了样本。

概率分布
1.离散型概率分布：
用于描述离散型随机变量的概率分布情况，常见的有二项分布、泊松分布等。例如，二项分布可用于计算在n次独立重复试验中，事件发生k次的概率。
2.连续型概率分布：
用于描述连续型随机变量的概率分布，如正态分布、均匀分布等。正态分布是最常见的分布之一，其概率密度函数呈钟形曲线，具有许多良好的性质，在自然和社会现象中广泛存在。
""",
                "统计推断": """
参数估计：通过样本数据来估计总体参数的值。有点估计和区间估计两种方式。
1.点估计：
用样本统计量直接作为总体参数的估计值，如用样本均值估计总体均值μ。
2.区间估计：
给出一个区间范围，并以一定的置信水平认为该区间包含总体参数的真实值，如前面提到的置信区间。

假设检验：
先对总体参数提出某种假设，然后根据样本数据来判断该假设是否成立，这是数据统计分析中常用的方法，前面已有详细介绍。
""",
                "应用": """
1.市场调研：
企业在推出新产品或进入新市场前，会通过问卷调查、访谈等方式收集消费者的相关数据，如消费者的需求、购买意愿、对产品价格的接受程度等。通过对这些数据的统计分析，了解市场需求和消费者行为特征，为企业的决策提供依据，如确定产品的定位、价格策略、营销方案等。

2.医疗研究：
在医学研究中，统计分析用于评估药物疗效、研究疾病的发生规律等。例如，通过对临床试验数据的分析，判断新药是否比现有药物更有效，或者研究某种生活方式与疾病发生风险之间的关系。

3.教育评估：
学校和教育机构可以通过对学生考试成绩、学习行为等数据的统计分析，评估教学效果，了解学生的学习情况，发现教学过程中存在的问题，以便采取相应的改进措施，如调整教学方法、优化课程设置等。

4.质量控制：
在工业生产中，通过对产品质量数据的统计分析，监控生产过程的稳定性，及时发现生产中的异常情况，采取措施进行调整，以保证产品质量的一致性和稳定性，降低次品率。
"""
            }
            
            # 创建知识框架
            KnowledgeFrame(self.master, "统计分析理论知识", sections)
            
        except ImportError:
            # 如果没有创建knowledge_framework.py，可以直接在这里实现
            self.create_theory_window()

    def create_theory_window(self):
        """备选方案：直接创建统计分析理论知识窗口"""
        theory_window = tk.Toplevel(self.master)
        theory_window.title("统计分析理论知识")
        theory_window.geometry("750x600")
        theory_window.configure(bg="#f0f0f0")
        
        # 创建主框架
        main_frame = ttk.Frame(theory_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="统计分析理论知识", 
                             font=("SimHei", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本概念选项卡
        concept_frame = ttk.Frame(notebook, padding=10)
        notebook.add(concept_frame, text="基本概念")
        
        # 统计推断选项卡
        calculation_frame = ttk.Frame(notebook, padding=10)
        notebook.add(calculation_frame, text="统计推断")
        
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
    app = AnalysisApp(root)
    root.mainloop()
