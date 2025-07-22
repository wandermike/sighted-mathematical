"""
MathVision 2.0 演示版本
展示新的单窗口多页面架构和优化功能
"""

import tkinter as tk
from tkinter import messagebox
import logging

# 配置基本日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入主题
from themes.futuristic_theme import COLORS, FONTS

class DemoPageManager:
    """简化的页面管理器演示"""
    
    def __init__(self, root):
        self.root = root
        self.pages = {}
        self.current_page = None
        self.page_history = []
        
        # 创建主容器
        self.container = tk.Frame(root, bg=COLORS["bg_light"])
        self.container.pack(fill=tk.BOTH, expand=True)
    
    def add_page(self, name, page_widget):
        """添加页面"""
        self.pages[name] = page_widget
        page_widget.pack_forget()  # 初始隐藏
    
    def show_page(self, name):
        """显示页面"""
        if name not in self.pages:
            logger.error(f"页面不存在: {name}")
            return
        
        # 隐藏当前页面
        if self.current_page:
            self.current_page.pack_forget()
            if hasattr(self, 'current_page_name'):
                self.page_history.append(self.current_page_name)
        
        # 显示新页面
        new_page = self.pages[name]
        new_page.pack(fill=tk.BOTH, expand=True)
        self.current_page = new_page
        self.current_page_name = name
        
        logger.info(f"切换到页面: {name}")
    
    def go_back(self):
        """返回上一页"""
        if self.page_history:
            previous_page = self.page_history.pop()
            self.show_page(previous_page)


class DemoSearchWidget:
    """简化的搜索组件演示"""
    
    def __init__(self, parent, page_manager):
        self.parent = parent
        self.page_manager = page_manager
        self.search_items = []
        
        self._create_ui()
    
    def _create_ui(self):
        """创建搜索界面"""
        search_frame = tk.Frame(self.parent, bg=COLORS["bg_medium"], relief=tk.RAISED, bd=1)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 搜索标签
        search_label = tk.Label(
            search_frame,
            text="🔍 快速搜索:",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["accent_primary"]
        )
        search_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 搜索按钮
        search_btn = tk.Button(
            search_frame,
            text="搜索",
            font=FONTS["button"],
            bg=COLORS["accent_primary"],
            fg=COLORS["bg_dark"],
            command=self._perform_search,
            bd=0,
            cursor="hand2"
        )
        search_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 绑定回车键
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
    
    def register_search_item(self, title, page_name, keywords):
        """注册搜索项"""
        self.search_items.append({
            'title': title,
            'page_name': page_name,
            'keywords': keywords
        })
    
    def _perform_search(self):
        """执行搜索"""
        query = self.search_var.get().strip().lower()
        if not query:
            return
        
        # 简单的搜索匹配
        for item in self.search_items:
            if (query in item['title'].lower() or 
                any(query in keyword.lower() for keyword in item['keywords'])):
                self.page_manager.show_page(item['page_name'])
                self.search_var.set("")  # 清空搜索框
                return
        
        # 未找到结果
        messagebox.showinfo("搜索结果", f"未找到匹配 '{query}' 的内容")


class ProgressDemo:
    """进度条演示"""
    
    def __init__(self, parent):
        self.parent = parent
        self.is_running = False
    
    def show_progress(self, message="处理中..."):
        """显示进度条"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 创建进度窗口
        self.progress_window = tk.Toplevel(self.parent)
        self.progress_window.title("请稍候")
        self.progress_window.geometry("300x150")
        self.progress_window.configure(bg=COLORS["bg_medium"])
        self.progress_window.resizable(False, False)
        
        # 居中显示
        self.progress_window.transient(self.parent)
        self.progress_window.grab_set()
        
        # 消息标签
        msg_label = tk.Label(
            self.progress_window,
            text=message,
            font=FONTS["subtitle"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        msg_label.pack(pady=20)
        
        # 进度条
        import tkinter.ttk as ttk
        progress = ttk.Progressbar(
            self.progress_window,
            mode='indeterminate',
            length=200
        )
        progress.pack(pady=10)
        progress.start(10)
        
        # 模拟处理时间
        self.parent.after(2000, self.hide_progress)
    
    def hide_progress(self):
        """隐藏进度条"""
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
        self.is_running = False


class DemoApp:
    """演示应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.page_manager = None
        self.search_widget = None
        self.progress_demo = None
        
        self._setup_window()
        self._create_navbar()
        self._create_pages()
        self._setup_search()
        self._setup_shortcuts()
    
    def _setup_window(self):
        """设置窗口"""
        self.root.title("MathVision 2.0 - 架构演示")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["bg_light"])
        
        # 设置最小尺寸
        self.root.minsize(800, 600)
    
    def _create_navbar(self):
        """创建导航栏"""
        navbar = tk.Frame(self.root, bg=COLORS["bg_medium"], height=60)
        navbar.pack(side=tk.TOP, fill=tk.X)
        navbar.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(
            navbar,
            text="MathVision 2.0 架构演示",
            font=FONTS["title"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 导航按钮
        nav_buttons = [
            ("主页", "main"),
            ("数学模块", "math"), 
            ("设置", "settings"),
            ("帮助", "help")
        ]
        
        for text, page_id in nav_buttons:
            btn = tk.Button(
                navbar,
                text=text,
                font=FONTS["button"],
                bg=COLORS["accent_primary"],
                fg=COLORS["bg_dark"],
                activebackground=COLORS["accent_secondary"],
                bd=0,
                padx=15,
                pady=5,
                cursor="hand2",
                command=lambda p=page_id: self.page_manager.show_page(p)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=15)
        
        # 返回按钮
        back_btn = tk.Button(
            navbar,
            text="← 返回",
            font=FONTS["button"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.page_manager.go_back
        )
        back_btn.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def _create_pages(self):
        """创建页面"""
        # 初始化页面管理器
        self.page_manager = DemoPageManager(self.root)
        self.progress_demo = ProgressDemo(self.root)
        
        # 主页
        main_page = self._create_main_page()
        self.page_manager.add_page("main", main_page)
        
        # 数学模块页
        math_page = self._create_math_page()
        self.page_manager.add_page("math", math_page)
        
        # 设置页
        settings_page = self._create_settings_page()
        self.page_manager.add_page("settings", settings_page)
        
        # 帮助页
        help_page = self._create_help_page()
        self.page_manager.add_page("help", help_page)
        
        # 显示主页
        self.page_manager.show_page("main")
    
    def _create_main_page(self):
        """创建主页"""
        page = tk.Frame(self.page_manager.container, bg=COLORS["bg_light"])
        
        # 欢迎标题
        welcome_label = tk.Label(
            page,
            text="欢迎使用 MathVision 2.0",
            font=("Arial", 28, "bold"),
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        welcome_label.pack(pady=40)
        
        # 副标题
        subtitle_label = tk.Label(
            page,
            text="全新的单窗口多页面架构",
            font=FONTS["subtitle"],
            bg=COLORS["bg_light"],
            fg=COLORS["accent_primary"]
        )
        subtitle_label.pack(pady=10)
        
        # 功能特性
        features_frame = tk.Frame(page, bg=COLORS["bg_light"])
        features_frame.pack(pady=30)
        
        features = [
            "✓ 流畅的页面切换体验",
            "✓ 智能搜索和快速定位", 
            "✓ 异步任务处理",
            "✓ 统一的主题管理",
            "✓ 键盘快捷键支持"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=FONTS["text"],
                bg=COLORS["bg_light"],
                fg=COLORS["text_secondary"],
                anchor=tk.W
            )
            feature_label.pack(pady=5, fill=tk.X)
        
        # 快速开始按钮
        start_btn = tk.Button(
            page,
            text="开始探索 →",
            font=FONTS["subtitle"],
            bg=COLORS["accent_secondary"],
            fg=COLORS["bg_dark"],
            bd=0,
            padx=30,
            pady=15,
            cursor="hand2",
            command=lambda: self.page_manager.show_page("math")
        )
        start_btn.pack(pady=20)
        
        return page
    
    def _create_math_page(self):
        """创建数学模块页"""
        page = tk.Frame(self.page_manager.container, bg=COLORS["bg_light"])
        
        # 页面标题
        title_label = tk.Label(
            page,
            text="数学模块",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 模块网格
        modules_frame = tk.Frame(page, bg=COLORS["bg_light"])
        modules_frame.pack(expand=True, padx=40)
        
        # 配置网格权重
        for i in range(2):
            modules_frame.grid_rowconfigure(i, weight=1)
            modules_frame.grid_columnconfigure(i, weight=1)
        
        # 模块卡片
        modules = [
            ("高等数学", "函数、微积分、微分方程"),
            ("线性代数", "矩阵运算、特征值分析"), 
            ("概率统计", "分布、假设检验、回归"),
            ("数值计算", "数值积分、优化算法")
        ]
        
        for i, (title, desc) in enumerate(modules):
            row = i // 2
            col = i % 2
            
            # 创建模块卡片
            card = tk.Frame(
                modules_frame,
                bg=COLORS["bg_medium"],
                relief=tk.RAISED,
                bd=2,
                width=200,
                height=150
            )
            card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            card.pack_propagate(False)
            
            # 卡片标题
            card_title = tk.Label(
                card,
                text=title,
                font=FONTS["subtitle"],
                bg=COLORS["bg_medium"],
                fg=COLORS["accent_primary"]
            )
            card_title.pack(pady=(20, 5))
            
            # 卡片描述
            card_desc = tk.Label(
                card,
                text=desc,
                font=FONTS["text"],
                bg=COLORS["bg_medium"],
                fg=COLORS["text_secondary"],
                wraplength=150,
                justify=tk.CENTER
            )
            card_desc.pack(pady=5)
            
            # 演示按钮
            demo_btn = tk.Button(
                card,
                text="演示加载",
                font=FONTS["small"],
                bg=COLORS["accent_primary"],
                fg=COLORS["bg_dark"],
                bd=0,
                padx=10,
                pady=5,
                cursor="hand2",
                command=lambda t=title: self._demo_loading(t)
            )
            demo_btn.pack(pady=(10, 0))
        
        return page
    
    def _create_settings_page(self):
        """创建设置页"""
        page = tk.Frame(self.page_manager.container, bg=COLORS["bg_light"])
        
        title_label = tk.Label(
            page,
            text="应用设置",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 设置选项
        settings_frame = tk.Frame(page, bg=COLORS["bg_medium"], relief=tk.RAISED, bd=2)
        settings_frame.pack(padx=40, pady=20, fill=tk.X)
        
        # 主题设置
        theme_frame = tk.Frame(settings_frame, bg=COLORS["bg_medium"])
        theme_frame.pack(fill=tk.X, padx=20, pady=15)
        
        theme_label = tk.Label(
            theme_frame,
            text="主题:",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        theme_label.pack(side=tk.LEFT)
        
        # 主题变量
        self.theme_var = tk.StringVar(value="未来科技")
        theme_combo = tk.OptionMenu(
            theme_frame,
            self.theme_var,
            "未来科技", "经典深色", "清新浅色"
        )
        theme_combo.configure(
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            bd=0
        )
        theme_combo.pack(side=tk.LEFT, padx=10)
        
        # 性能设置
        perf_frame = tk.Frame(settings_frame, bg=COLORS["bg_medium"])
        perf_frame.pack(fill=tk.X, padx=20, pady=15)
        
        perf_label = tk.Label(
            perf_frame,
            text="性能模式:",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        perf_label.pack(side=tk.LEFT)
        
        self.perf_var = tk.StringVar(value="平衡")
        perf_combo = tk.OptionMenu(
            perf_frame,
            self.perf_var,
            "高性能", "平衡", "节能"
        )
        perf_combo.configure(
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            bd=0
        )
        perf_combo.pack(side=tk.LEFT, padx=10)
        
        # 应用按钮
        apply_btn = tk.Button(
            settings_frame,
            text="应用设置",
            font=FONTS["button"],
            bg=COLORS["accent_primary"],
            fg=COLORS["bg_dark"],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._apply_settings
        )
        apply_btn.pack(pady=20)
        
        return page
    
    def _create_help_page(self):
        """创建帮助页"""
        page = tk.Frame(self.page_manager.container, bg=COLORS["bg_light"])
        
        title_label = tk.Label(
            page,
            text="使用帮助",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        # 帮助内容
        help_text = """
快捷键说明:
• Ctrl+1: 切换到主页
• Ctrl+2: 切换到数学模块  
• Ctrl+3: 切换到设置页面
• Ctrl+4: 切换到帮助页面
• Alt+Left: 返回上一页
• Escape: 返回主页

搜索功能:
• 在搜索框中输入关键字
• 支持模糊匹配和智能提示
• 按回车键快速跳转

新特性:
• 单窗口多页面架构
• 流畅的页面切换动画
• 异步任务处理，避免界面卡顿
• 统一的主题和配置管理
        """
        
        help_label = tk.Label(
            page,
            text=help_text,
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT,
            anchor=tk.NW
        )
        help_label.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        return page
    
    def _setup_search(self):
        """设置搜索功能"""
        self.search_widget = DemoSearchWidget(self.root, self.page_manager)
        
        # 注册搜索项
        self.search_widget.register_search_item("主页", "main", ["主页", "首页", "欢迎"])
        self.search_widget.register_search_item("数学模块", "math", ["数学", "计算", "函数", "矩阵"])
        self.search_widget.register_search_item("设置", "settings", ["设置", "配置", "主题"])
        self.search_widget.register_search_item("帮助", "help", ["帮助", "说明", "快捷键"])
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        self.root.bind("<Control-Key-1>", lambda e: self.page_manager.show_page("main"))
        self.root.bind("<Control-Key-2>", lambda e: self.page_manager.show_page("math"))
        self.root.bind("<Control-Key-3>", lambda e: self.page_manager.show_page("settings"))
        self.root.bind("<Control-Key-4>", lambda e: self.page_manager.show_page("help"))
        self.root.bind("<Alt-Left>", lambda e: self.page_manager.go_back())
        self.root.bind("<Escape>", lambda e: self.page_manager.show_page("main"))
        
        # 焦点设置
        self.root.focus_set()
    
    def _demo_loading(self, module_name):
        """演示加载功能"""
        self.progress_demo.show_progress(f"正在加载 {module_name} 模块...")
    
    def _apply_settings(self):
        """应用设置"""
        theme = self.theme_var.get()
        performance = self.perf_var.get()
        
        messagebox.showinfo(
            "设置已保存",
            f"主题: {theme}\n性能模式: {performance}\n\n重启应用后生效"
        )
    
    def run(self):
        """运行应用"""
        logger.info("MathVision 2.0 演示启动")
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"应用运行错误: {e}")
        finally:
            logger.info("MathVision 2.0 演示关闭")


def main():
    """主函数"""
    try:
        app = DemoApp()
        app.run()
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 