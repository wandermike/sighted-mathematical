"""
页面管理器 - 实现单窗口多页面架构
替代原有的多Toplevel窗口设计，提供流畅的页面切换体验
"""

import tkinter as tk
from typing import Dict, Type, Optional
import logging
from themes.futuristic_theme import COLORS, FONTS


class BasePage(tk.Frame):
    """页面基类，所有应用页面都应继承此类"""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=COLORS["bg_light"], **kwargs)
        self.controller = controller
        self.page_name = self.__class__.__name__
        
        # 页面状态
        self.is_active = False
        self.is_initialized = False
        
        # 配置页面网格权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def on_show(self):
        """页面显示时的回调，子类可以重写"""
        self.is_active = True
        if not self.is_initialized:
            self.initialize()
            self.is_initialized = True
    
    def on_hide(self):
        """页面隐藏时的回调，子类可以重写"""
        self.is_active = False
    
    def initialize(self):
        """页面初始化，子类应该重写此方法"""
    
    def cleanup(self):
        """页面清理，子类可以重写"""


class PageManager:
    """页面管理器 - 管理应用的所有页面并提供流畅切换"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.pages: Dict[str, BasePage] = {}
        self.current_page: Optional[str] = None
        self.page_history = []
        
        # 创建主容器
        self.container = tk.Frame(root, bg=COLORS["bg_light"])
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
    def register_page(self, name: str, page_class: Type[BasePage], **kwargs) -> BasePage:
        """注册页面类"""
        try:
            # 创建页面实例
            page = page_class(self.container, controller=self, **kwargs)
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()  # 初始隐藏
            
            self.pages[name] = page
            self.logger.info(f"页面已注册: {name}")
            return page
            
        except Exception as e:
            self.logger.error(f"注册页面失败 {name}: {e}")
            raise
    
    def show_page(self, name: str, animation: str = "fade", **kwargs) -> bool:
        """显示指定页面"""
        if name not in self.pages:
            self.logger.error(f"页面未找到: {name}")
            return False
        
        # 隐藏当前页面
        if self.current_page:
            old_page = self.pages[self.current_page]
            old_page.on_hide()
            old_page.grid_remove()
            
            # 添加到历史记录
            if self.current_page != name:
                self.page_history.append(self.current_page)
                # 限制历史记录长度
                if len(self.page_history) > 10:
                    self.page_history.pop(0)
        
        # 显示新页面
        new_page = self.pages[name]
        new_page.grid(row=0, column=0, sticky="nsew")
        new_page.on_show()
        
        # 执行动画
        self._animate_page_transition(new_page, animation)
        
        self.current_page = name
        self.logger.info(f"切换到页面: {name}")
        return True
    
    def go_back(self) -> bool:
        """返回上一页面"""
        if not self.page_history:
            return False
        
        previous_page = self.page_history.pop()
        return self.show_page(previous_page, animation="slide_right")
    
    def get_current_page(self) -> Optional[BasePage]:
        """获取当前页面实例"""
        if self.current_page:
            return self.pages[self.current_page]
        return None
    
    def get_page(self, name: str) -> Optional[BasePage]:
        """获取指定页面实例"""
        return self.pages.get(name)
    
    def clear_history(self):
        """清空页面历史"""
        self.page_history.clear()
    
    def _animate_page_transition(self, page: BasePage, animation: str):
        """执行页面切换动画"""
        try:
            if animation == "fade":
                # 设置初始透明度
                page.configure(bg=COLORS["bg_light"])
                self.root.update()
                # 执行淡入动画（简化版）
                page.after(50, lambda: page.configure(bg=COLORS["bg_light"]))
                
            elif animation == "slide_left":
                # 从右侧滑入
                original_x = page.winfo_x()
                page.place(x=self.root.winfo_width(), y=0)
                self._slide_to_position(page, original_x, 0, 300)
                
            elif animation == "slide_right":
                # 从左侧滑入
                original_x = page.winfo_x()
                page.place(x=-self.root.winfo_width(), y=0)
                self._slide_to_position(page, original_x, 0, 300)
                
        except Exception as e:
            self.logger.warning(f"页面动画执行失败: {e}")
    
    def _slide_to_position(self, widget, target_x, target_y, duration):
        """滑动到指定位置"""
        current_x = widget.winfo_x()
        current_y = widget.winfo_y()
        
        steps = 20
        step_time = duration // steps
        
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps
        
        def animate_step(step):
            if step >= steps:
                widget.place(x=target_x, y=target_y)
                # 动画完成后切换回grid布局
                widget.place_forget()
                widget.grid(row=0, column=0, sticky="nsew")
                return
            
            new_x = current_x + dx * step
            new_y = current_y + dy * step
            widget.place(x=int(new_x), y=int(new_y))
            
            widget.after(step_time, lambda: animate_step(step + 1))
        
        animate_step(0)


class NavigationBar(tk.Frame):
    """导航栏组件"""
    
    def __init__(self, parent, page_manager: PageManager, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], height=60, **kwargs)
        self.page_manager = page_manager
        
        # 配置导航栏
        self.pack_propagate(False)
        
        self._create_navigation_elements()
    
    def _create_navigation_elements(self):
        """创建导航元素"""
        # 返回按钮
        self.back_button = tk.Button(
            self,
            text="← 返回",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["accent_primary"],
            activebackground=COLORS["accent_primary"],
            activeforeground=COLORS["bg_medium"],
            bd=0,
            command=self.page_manager.go_back,
            cursor="hand2"
        )
        self.back_button.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 主页按钮
        self.home_button = tk.Button(
            self,
            text="🏠 主页",
            font=FONTS["button"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent_secondary"],
            activeforeground=COLORS["bg_medium"],
            bd=0,
            command=lambda: self.page_manager.show_page("MainPage"),
            cursor="hand2"
        )
        self.home_button.pack(side=tk.LEFT, padx=10, pady=15)
        
        # 页面标题
        self.title_label = tk.Label(
            self,
            text="数学可视化教学工具",
            font=FONTS["title"],
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"]
        )
        self.title_label.pack(side=tk.LEFT, padx=20)
    
    def update_title(self, title: str):
        """更新导航栏标题"""
        self.title_label.config(text=title) 