import tkinter as tk
from themes.futuristic_theme import COLORS, FONTS

class FuturisticButton(tk.Frame):
    """增强的基于Frame的自定义按钮，支持平滑过渡和高效状态管理"""
    def __init__(self, parent, text, command=None, width=200, height=50, 
                 bg_color=COLORS["bg_medium"], fg_color=COLORS["accent_primary"], 
                 hover_color=COLORS["accent_secondary"], **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        # 按钮属性
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.callback = command
        self.text = text
        self.button_width = width
        self.button_height = height
        self.button_state = "normal"
        self.animation_in_progress = False
        self.animation_id = None
        
        # 确保Frame使用特定尺寸
        self.pack_propagate(False)
        self.config(width=width, height=height, bg=COLORS["bg_dark"])
        
        # 创建画布用于绘制按钮
        self.canvas = tk.Canvas(self, width=width, height=height, 
                             bg=COLORS["bg_dark"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 初始绘制按钮(只绘制一次基本形状)
        self._initialize_button()
        
        # 事件管理器 - 使用统一接口注册所有事件
        self._event_handlers = {}
        self._register_default_handlers()
        
        # 鼠标指针设置
        self.config(cursor="hand2")
        self.canvas.config(cursor="hand2")
    
    def _register_default_handlers(self):
        """注册默认的事件处理器，确保事件不被其他组件拦截"""
        # 将事件绑定到所有相关元素，并使用stopPropagation以阻止事件冒泡
        for element in [self, self.canvas]:
            element.bind("<Enter>", lambda e: self._handle_event("enter", e), add="+")
            element.bind("<Leave>", lambda e: self._handle_event("leave", e), add="+")
            element.bind("<ButtonPress-1>", lambda e: self._handle_event("press", e), add="+")
            element.bind("<ButtonRelease-1>", lambda e: self._handle_event("release", e), add="+")
            # 添加点击事件响应器 - 确保直接捕获点击
            element.bind("<Button-1>", self._on_direct_click, add="+")
        
        # 绑定事件到按钮元素
        self.tag_bind("button_bg", "<Button-1>", self._on_direct_click)
        self.tag_bind("button_text", "<Button-1>", self._on_direct_click)
    
    def _on_direct_click(self, event):
        """直接处理点击事件，不等待释放"""
        # 阻止事件继续传播
        event.widget.focus_set()  # 设置焦点到当前按钮
        return "break"  # 阻止冒泡
    
    def _handle_event(self, event_type, event):
        """增强的事件处理器阻止事件冒泡"""
        # 防抖动处理 - 如果动画正在进行，跳过不必要的状态改变
        if self.animation_in_progress and event_type in ["enter", "leave"]:
            return "break"
            
        if event_type == "enter" and self.button_state != "pressed":
            self.update_state("hover")
        elif event_type == "leave" and self.button_state != "pressed":
            self.update_state("normal")
        elif event_type == "press":
            self.update_state("pressed")
            # 立即将焦点设置到按钮，确保按钮获得释放事件
            self.focus_set()
        elif event_type == "release":
            if self.button_state == "pressed":
                self.update_state("hover")
                # 状态处于按下时才触发回调
                if self.callback:
                    # 添加延迟确保视觉反馈
                    self.after(10, self.callback)
        
        # 阻止事件继续冒泡
        return "break"
    
    def tag_bind(self, tag, sequence, callback):
        """为按钮添加事件绑定功能"""
        self.canvas.tag_bind(tag, sequence, callback)
    
    def _initialize_button(self):
        """初始化按钮的基本形状和元素"""
        # 绘制背景
        self._create_rounded_rectangle(10, 5, self.button_width-10, self.button_height-5, 
                                      radius=10, fill=self.bg_color, tags="button_bg")
        
        # 预先创建边框(默认隐藏)
        self._create_rounded_rectangle(10, 5, self.button_width-10, self.button_height-5, 
                                     radius=10, outline=self.fg_color, width=0, tags="button_border")
        
        # 添加文本
        self.canvas.create_text(self.button_width/2, self.button_height/2, 
                               text=self.text, fill=self.fg_color, font=FONTS["button"], tags="button_text")
    
    def update_state(self, new_state):
        """增量更新按钮状态，只修改变化的部分"""
        if self.button_state == new_state:
            return  # 避免不必要的更新
            
        old_state = self.button_state
        self.button_state = new_state
        
        # 取消任何正在进行的动画
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        
        # 根据状态转换应用不同的动画效果
        if new_state == "hover" and old_state == "normal":
            self._animate_hover_in()
        elif new_state == "normal" and old_state == "hover":
            self._animate_hover_out()
        elif new_state == "pressed":
            self._animate_press()
        elif new_state == "hover" and old_state == "pressed":
            self._animate_release()
    
    def _animate_hover_in(self):
        """平滑过渡到悬停状态"""
        self.animation_in_progress = True
        steps = 8
        duration = 200  # 总持续时间(毫秒)
        step_time = duration // steps
        current_step = 0
        
        # 获取初始和目标颜色
        bg_start = self.bg_color
        bg_end = self.hover_color
        text_start = self.fg_color
        text_end = COLORS["text_primary"]
        
        def animate_step():
            nonlocal current_step
            if current_step >= steps:
                # 设置最终状态
                self.canvas.itemconfig("button_bg", fill=bg_end)
                self.canvas.itemconfig("button_text", fill=text_end)
                self.canvas.itemconfig("button_border", width=2)
                self.animation_in_progress = False
                self.animation_id = None
                return
                
            # 计算当前步骤的插值
            progress = current_step / steps
            
            # 插值计算当前颜色
            bg_current = self._interpolate_color(bg_start, bg_end, progress)
            text_current = self._interpolate_color(text_start, text_end, progress)
            border_width = 2 * progress
            
            # 应用当前值
            self.canvas.itemconfig("button_bg", fill=bg_current)
            self.canvas.itemconfig("button_text", fill=text_current)
            self.canvas.itemconfig("button_border", width=border_width)
            
            current_step += 1
            self.animation_id = self.after(step_time, animate_step)
        
        # 启动动画
        animate_step()
    
    def _animate_hover_out(self):
        """平滑过渡回正常状态"""
        self.animation_in_progress = True
        steps = 8
        duration = 200
        step_time = duration // steps
        current_step = 0
        
        # 获取初始和目标颜色
        bg_start = self.hover_color
        bg_end = self.bg_color
        text_start = COLORS["text_primary"]
        text_end = self.fg_color
        
        def animate_step():
            nonlocal current_step
            if current_step >= steps:
                # 设置最终状态
                self.canvas.itemconfig("button_bg", fill=bg_end)
                self.canvas.itemconfig("button_text", fill=text_end)
                self.canvas.itemconfig("button_border", width=0)
                self.animation_in_progress = False
                self.animation_id = None
                return
                
            # 计算当前步骤的插值
            progress = current_step / steps
            
            # 插值计算当前颜色
            bg_current = self._interpolate_color(bg_start, bg_end, progress)
            text_current = self._interpolate_color(text_start, text_end, progress)
            border_width = 2 * (1 - progress)
            
            # 应用当前值
            self.canvas.itemconfig("button_bg", fill=bg_current)
            self.canvas.itemconfig("button_text", fill=text_current)
            self.canvas.itemconfig("button_border", width=border_width)
            
            current_step += 1
            self.animation_id = self.after(step_time, animate_step)
        
        # 启动动画
        animate_step()
    
    def _animate_press(self):
        """按下动画效果"""
        # 立即应用按下状态 - 这应该感觉很迅速
        self.canvas.itemconfig("button_bg", fill=self.fg_color)
        self.canvas.itemconfig("button_text", fill=COLORS["bg_dark"])
        self.canvas.itemconfig("button_border", width=0)
    
    def _animate_release(self):
        """释放动画效果"""
        # 立即返回到悬停状态
        self.canvas.itemconfig("button_bg", fill=self.hover_color)
        self.canvas.itemconfig("button_text", fill=COLORS["text_primary"])
        self.canvas.itemconfig("button_border", width=2)
    
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)
    
    def _interpolate_color(self, start_color, end_color, progress):
        """在两个颜色之间插值"""
        # 解析颜色
        r1, g1, b1 = self._hex_to_rgb(start_color)
        r2, g2, b2 = self._hex_to_rgb(end_color)
        
        # 计算插值
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)
        
        # 返回HEX格式
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color):
        """将HEX颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class IconButton(tk.Canvas):
    """带图标的按钮"""
    def __init__(self, parent, icon_path, command=None, tooltip="", 
                 size=40, **kwargs):
        super().__init__(parent, width=size, height=size, 
                         bg=COLORS["bg_dark"], highlightthickness=0, **kwargs)
        
        self.command = command
        self.tooltip = tooltip
        self.size = size
        self.tooltip_window = None
        
        # 加载图标
        try:
            from PIL import Image, ImageTk
            self.img = Image.open(icon_path)
            self.img = self.img.resize((size-10, size-10), Image.LANCZOS)
            self.icon = ImageTk.PhotoImage(self.img)
            self.has_icon = True
        except Exception:
            self.has_icon = False
        
        # 绘制按钮
        self.draw_button()
        
        # 绑定事件
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def draw_button(self, state="normal"):
        self.delete("all")
        
        # 绘制圆形背景
        if state == "normal":
            bg_color = COLORS["bg_medium"]
            fg_color = COLORS["accent_primary"]
        elif state == "hover":
            bg_color = COLORS["accent_secondary"]
            fg_color = COLORS["text_primary"]
        else:  # pressed
            bg_color = COLORS["accent_primary"]
            fg_color = COLORS["bg_dark"]
        
        # 绘制圆形
        self.create_oval(5, 5, self.size-5, self.size-5, 
                          fill=bg_color, outline=fg_color, width=1)
        
        # 绘制图标或占位符
        if self.has_icon:
            self.create_image(self.size/2, self.size/2, image=self.icon)
        else:
            # 绘制一个简单的图形作为占位符
            self.create_line(15, self.size/2, self.size-15, self.size/2, 
                            fill=fg_color, width=2)
            self.create_line(self.size/2, 15, self.size/2, self.size-15, 
                            fill=fg_color, width=2)
    
    def on_enter(self, event):
        self.draw_button("hover")
        
        # 显示工具提示
        if self.tooltip:
            x, y, _, _ = self.bbox("all")
            x = x + self.winfo_rootx() + 20
            y = y + self.winfo_rooty() + 20
            
            self.tooltip_window = tk.Toplevel(self)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip_window, text=self.tooltip, 
                           bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
                           font=FONTS["small"], padx=5, pady=2)
            label.pack()
    
    def on_leave(self, event):
        self.draw_button("normal")
        
        # 隐藏工具提示
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def on_press(self, event):
        self.draw_button("pressed")
    
    def on_release(self, event):
        self.draw_button("hover")
        if self.command:
            self.command()
