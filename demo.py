"""
MathVision 2.0 演示版本
展示新的单窗口多页面架构和优化功能
"""

import tkinter as tk
import logging

# 配置基本日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入主题
from themes.futuristic_theme import COLORS, FONTS

class DemoApp:
    """演示应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.pages = {}
        self.current_page = None
        
        self._setup_window()
        self._create_navbar()
        self._create_pages()
        self._setup_shortcuts()
    
    def _setup_window(self):
        """设置窗口"""
        self.root.title("MathVision 2.0 - 架构演示")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["bg_light"])
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
                command=lambda p=page_id: self.show_page(p)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=15)
    
    def _create_pages(self):
        """创建页面"""
        # 主容器
        self.container = tk.Frame(self.root, bg=COLORS["bg_light"])
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个页面
        self._create_main_page()
        self._create_math_page()
        self._create_settings_page()
        self._create_help_page()
        
        # 显示主页
        self.show_page("main")
    
    def _create_main_page(self):
        """创建主页"""
        page = tk.Frame(self.container, bg=COLORS["bg_light"])
        
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
            command=lambda: self.show_page("math")
        )
        start_btn.pack(pady=20)
        
        self.pages["main"] = page
    
    def _create_math_page(self):
        """创建数学模块页"""
        page = tk.Frame(self.container, bg=COLORS["bg_light"])
        
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
            card.grid(row=row, column=col, padx=20, pady=20)
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
        
        self.pages["math"] = page
    
    def _create_settings_page(self):
        """创建设置页"""
        page = tk.Frame(self.container, bg=COLORS["bg_light"])
        
        title_label = tk.Label(
            page,
            text="应用设置",
            font=FONTS["title"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"]
        )
        title_label.pack(pady=20)
        
        info_label = tk.Label(
            page,
            text="主题、性能、界面等设置选项",
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"]
        )
        info_label.pack(pady=10)
        
        self.pages["settings"] = page
    
    def _create_help_page(self):
        """创建帮助页"""
        page = tk.Frame(self.container, bg=COLORS["bg_light"])
        
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

新特性:
• 单窗口多页面架构
• 流畅的页面切换
• 统一的主题管理
        """
        
        help_label = tk.Label(
            page,
            text=help_text,
            font=FONTS["text"],
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT
        )
        help_label.pack(padx=40, pady=20)
        
        self.pages["help"] = page
    
    def show_page(self, page_id):
        """显示页面"""
        # 隐藏当前页面
        if self.current_page:
            self.current_page.pack_forget()
        
        # 显示新页面
        if page_id in self.pages:
            page = self.pages[page_id]
            page.pack(fill=tk.BOTH, expand=True)
            self.current_page = page
            logger.info(f"切换到页面: {page_id}")
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        self.root.bind("<Control-Key-1>", lambda e: self.show_page("main"))
        self.root.bind("<Control-Key-2>", lambda e: self.show_page("math"))
        self.root.bind("<Control-Key-3>", lambda e: self.show_page("settings"))
        self.root.bind("<Control-Key-4>", lambda e: self.show_page("help"))
        self.root.focus_set()
    
    def run(self):
        """运行应用"""
        logger.info("演示应用启动")
        self.root.mainloop()


def main():
    """主函数"""
    app = DemoApp()
    app.run()


if __name__ == "__main__":
    main() 