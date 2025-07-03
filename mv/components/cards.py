import tkinter as tk
from PIL import Image, ImageTk
import os
import math
from themes.futuristic_theme import COLORS, FONTS, SPACING, RADII, CARD_STYLES, ANIMATION
from components.buttons import FuturisticButton

class InteractiveCard(tk.Frame):
    """增强的交互式卡片组件，提供标准化的视觉和交互体验"""
    
    def __init__(self, parent, title, description, icon_path=None, 
                 color=COLORS["accent_primary"], command=None,
                 width=240, height=300, style="standard", **kwargs):
        """
        创建一个视觉对称的交互式卡片
        
        参数:
            parent: 父容器
            title: 卡片标题
            description: 卡片描述文本
            icon_path: 图标路径（可选）
            color: 卡片主色调 (强调色)
            command: 点击卡片时执行的回调函数
            width: 卡片宽度
            height: 卡片高度
            style: 卡片样式，可选 "standard", "highlighted", "elevated"
        """
        # 选择卡片样式
        self.card_style = CARD_STYLES.get(style, CARD_STYLES["standard"])
        
        # 初始化Frame
        super().__init__(
            parent, 
            width=width, 
            height=height, 
            bg=self.card_style["bg"],
            highlightbackground=self.card_style["border_color"],
            highlightthickness=self.card_style["border_width"],
            bd=0,
            **kwargs
        )
        
        # 保存核心属性
        self.title = title
        self.description = description
        self.icon_path = icon_path
        self.accent_color = color  # 强调色
        self.callback = command
        self.card_width = width
        self.card_height = height
        
        # 状态管理
        self.highlight_state = False
        self.hover_state = False
        self.animation_in_progress = False
        self.animation_id = None
        
        # UI元素存储
        self.elements = {}
        
        # 确保卡片保持固定大小
        self.grid_propagate(False)
        
        # 构建卡片UI，使用精确的对称布局
        self._build_card()
        
        # 注册统一的交互事件
        self._setup_interactions()
    
    def _build_card(self):
        """重构卡片UI元素，确保美观对称和免事件冲突"""
        # 设置卡片边框效果
        self.config(highlightbackground=self.card_style["border_color"],
                   highlightthickness=self.card_style["border_width"],
                   relief=tk.FLAT,  # 起始为平面效果
                   borderwidth=0)
        
        # 使用网格布局替代place，更好控制对称性
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 使用单一内容框架替代多层嵌套
        self.content_frame = tk.Frame(
            self,
            bg=self.card_style["bg"],
            bd=0,
            highlightthickness=0,
        )
        self.content_frame.grid(row=0, column=0, padx=SPACING["sm"], pady=SPACING["sm"], sticky="nsew")
        self.elements["content_frame"] = self.content_frame
        
        # 设置内容框架的行列布局
        # 1 - 顶部装饰条
        # 2 - 标题
        # 3 - 图标
        # 4 - 描述文本
        # 5 - 按钮 (可选，仅在style不是clickable时显示)
        rows = 5 if self.card_style != CARD_STYLES.get("clickable", {}) else 4
        for i in range(rows):
            self.content_frame.grid_rowconfigure(i, weight=1 if i == 3 else 0)  # 描述区域可伸缩
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # 1. 顶部装饰条 - 采用电影效果的设计
        decoration_height = 6
        decoration_canvas = tk.Canvas(
            self.content_frame, 
            height=decoration_height,
            bg=self.card_style["bg"], 
            highlightthickness=0
        )
        decoration_canvas.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xs"]))
        
        # 使用带阴影效果的渐变装饰条
        decoration_width = self.card_width - 2*SPACING["sm"]
        # 设置画布大小
        decoration_canvas.config(width=decoration_width)
        
        # 对称渐变条 - 中心发亮
        gradient_colors = []
        for i in range(decoration_width):
            # 计算对称渐变
            position = i / decoration_width
            intensity = 1.0 - 2 * abs(position - 0.5)  # 中心位置应为最亮
            color = self._interpolate_color(self.card_style["bg"], self.accent_color, intensity**0.8)  # 指数增强对比度
            gradient_colors.append(color)
        
        # 绘制渐变条及其阴影
        # 阴影效果
        for i in range(decoration_width):
            shadow_color = self._adjust_color_brightness(gradient_colors[i], 0.3)  # 暗色阴影
            decoration_canvas.create_line(i, 2, i, decoration_height, fill=shadow_color, width=1)
        
        # 主渐变条
        for i in range(decoration_width):
            decoration_canvas.create_line(i, 0, i, decoration_height-2, fill=gradient_colors[i], width=1)
            
        self.elements["decoration"] = decoration_canvas
        
        # 2. 标题 - 使用漂亮的字体和颜色
        title_label = tk.Label(
            self.content_frame, 
            text=self.title, 
            font=FONTS["subtitle"], 
            bg=self.card_style["bg"], 
            fg=COLORS["text_primary"],
            justify=tk.CENTER,  # 确保居中对齐
        )
        title_label.grid(row=1, column=0, pady=(SPACING["sm"], SPACING["xs"]))
        self.elements["title"] = title_label
        
        # 3. 图标区域 - 使用固定大小的框架确保对称
        icon_frame = tk.Frame(
            self.content_frame, 
            width=80, 
            height=80, 
            bg=self.card_style["bg"]
        )
        icon_frame.grid(row=2, column=0, pady=SPACING["xs"])
        icon_frame.pack_propagate(False)  # 禁用自动调整确保固定大小
        self.elements["icon_frame"] = icon_frame
        
        # 加载图标或创建精美的占位图标
        self.icon_label = None
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                img = Image.open(self.icon_path)
                # 加入缩放图标的判断逻辑，确保最佳表现
                size = min(img.width, img.height, 64)  # 取原始分辨率和目标尺寸的最小值
                img = img.resize((size, size), Image.LANCZOS)
                self.icon = ImageTk.PhotoImage(img)
                
                # 创建图标容器
                icon_inner_frame = tk.Frame(icon_frame, bg=self.card_style["bg"])
                icon_inner_frame.pack(expand=True, fill=tk.BOTH)
                
                # 更精美的图标展示
                icon_label = tk.Label(
                    icon_inner_frame, 
                    image=self.icon, 
                    bg=self.card_style["bg"],
                    bd=0
                )
                icon_label.pack(expand=True)
                self.elements["icon"] = icon_label
                self.icon_label = icon_label
            except Exception as e:
                print(f"无法加载图标 {self.icon_path}: {e}")
                self._create_placeholder_icon(icon_frame)
        else:
            self._create_placeholder_icon(icon_frame)
        
        # 4. 描述文本 - 使用更优雅的字体和对称布局
        desc_container = tk.Frame(self.content_frame, bg=self.card_style["bg"])
        desc_container.grid(row=3, column=0, sticky="nsew", padx=SPACING["sm"])
        desc_container.grid_rowconfigure(0, weight=1)
        desc_container.grid_columnconfigure(0, weight=1)
        
        desc_label = tk.Label(
            desc_container, 
            text=self.description, 
            font=FONTS["text"], 
            bg=self.card_style["bg"], 
            fg=COLORS["text_secondary"],
            wraplength=self.card_width - 2*SPACING["md"],  # 留出更大的边距提高可读性
            justify=tk.CENTER  # 居中对齐提升对称性
        )
        desc_label.grid(row=0, column=0)
        self.elements["description"] = desc_label
        
        # 5. 按钮区域 - 仅在非clickable样式时显示
        if self.card_style != CARD_STYLES.get("clickable", {}):
            button_container = tk.Frame(self.content_frame, bg=self.card_style["bg"])
            button_container.grid(row=4, column=0, pady=SPACING["md"])
            self.elements["button_container"] = button_container
            
            # 创建更宽、更美观的按钮
            button = FuturisticButton(
                button_container, 
                text="打开", 
                command=self.callback,  # 直接传递回调函数
                width=130,  # 更宽一点的按钮
                height=36,
                bg_color=self.card_style["bg"],  # 确保背景颜色一致
                fg_color=self.accent_color
            )
            button.pack()
            self.elements["button"] = button
        else:
            # 如果是clickable样式，将整个卡片设置为可点击状态
            self.config(cursor="hand2")  # 设置手型光标
            # 为整个卡片绑定点击事件
            self.bind("<Button-1>", lambda e: self.callback() if self.callback else None)
            
            # 为所有子组件绑定点击事件，确保点击任何位置都能触发回调
            for widget in [self.content_frame] + list(self.elements.values()):
                if isinstance(widget, (tk.Frame, tk.Label, tk.Canvas)):
                    widget.config(cursor="hand2")  # 统一设置手型光标
                    widget.bind("<Button-1>", lambda e, cmd=self.callback: cmd() if cmd else None)
                    
                    # 递归绑定嵌套组件
                    if isinstance(widget, tk.Frame):
                        self._bind_recursive(widget)
    
    def _create_placeholder_icon(self, parent_frame):
        """创建一个视觉对称的占位图标"""
        placeholder = tk.Canvas(
            parent_frame, 
            width=64, 
            height=64, 
            bg=self.card_style["bg"], 
            highlightthickness=0
        )
        placeholder.pack(expand=True)
        
        # 创建一个视觉更有趣的几何形占位图标
        # 中心圆
        placeholder.create_oval(14, 14, 50, 50, 
                                fill=self.accent_color, outline="", tags="icon")
        
        # 引入视觉元素增强设计感
        # 外圈环
        placeholder.create_oval(10, 10, 54, 54, 
                                outline=self._adjust_color_brightness(self.accent_color, 1.3),
                                width=1, tags="ring")
        
        # 点缀
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            r = 28  # 半径
            x = 32 + r * math.cos(angle)  # 中心点x=32
            y = 32 + r * math.sin(angle)  # 中心点y=32
            size = 3
            placeholder.create_oval(x-size, y-size, x+size, y+size,
                                  fill=self._adjust_color_brightness(self.accent_color, 1.2),
                                  outline="", tags=f"dot_{i}")
        
        # 添加简单的旋转动画
        self._animate_placeholder(placeholder)
        
        self.elements["icon_placeholder"] = placeholder
        return placeholder
    
    def _animate_placeholder(self, canvas):
        """为占位图标添加旋转动画"""
        def rotate():
            # 旋转外圈
            canvas.itemconfig("ring", width=1.5)  # 稍微加粗外环
            canvas.itemconfig("icon", fill=self._adjust_color_brightness(self.accent_color, 0.9))  # 调整中心圆颜色
            
            # 如果卡片被销毁，停止动画
            if not canvas.winfo_exists():
                return
                
            # 继续动画
            canvas.after(3000, rotate)  # 3秒后再次执行
        
        # 启动动画
        canvas.after(1000, rotate)  # 1秒后开始
    
    def _adjust_color_brightness(self, hex_color, factor):
        """调整颜色的亮度"""
        # 转换为RGB
        r, g, b = self._hex_to_rgb(hex_color)
        
        # 亮度调整
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        
        # 转回十六进制
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color):
        """将十六进制颜色代码转换为RGB值"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _interpolate_color(self, start_color, end_color, factor):
        """在两个颜色之间插值"""
        # 解析颜色
        r1, g1, b1 = self._hex_to_rgb(start_color)
        r2, g2, b2 = self._hex_to_rgb(end_color)
        
        # 计算插值
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        # 返回HEX颜色
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _setup_interactions(self):
        """完全重构卡片的交互机制，确保按钮可独立交互"""
        # 首先解绑所有现有事件
        for sequence in ("<Enter>", "<Leave>", "<Button-1>", "<ButtonRelease-1>", "<Motion>"):
            self.unbind(sequence)
        
        # 1. 仅为主卡片框架本身绑定事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        # 2. 明确不进行事件委托的区域
        button_elements = [
            self.elements.get("button", None),
            self.elements.get("button_container", None)
        ]
        
        # 3. 设置点击区域的鼠标样式以增强可见性
        # 卡片可点击区域使用手型光标
        self.config(cursor="hand2")
        self.content_frame.config(cursor="hand2")
        
        # 4. 为卡片内的非交互元素设置透明事件层
        for name, element in self.elements.items():
            # 跳过按钮相关元素
            if element in button_elements or self._is_button_related(element):
                continue
                
            # 设置手形光标并绑定透明事件
            if isinstance(element, tk.Label) or isinstance(element, tk.Canvas):
                element.config(cursor="hand2")
                self._bind_transparent_events(element)
            
            # 为子容器封锁额外的交互区域
            if isinstance(element, tk.Frame) and not self._is_button_container(element):
                element.config(cursor="hand2")
                self._bind_transparent_events(element)
                
                # 递归处理子元素
                self._process_container_children(element, button_elements)
    
    def _process_container_children(self, container, excluded_elements):
        """递归处理容器内所有子元素，设置透明事件层"""
        for child in container.winfo_children():
            if child in excluded_elements or isinstance(child, FuturisticButton):
                continue
                
            # 设置手形光标并设置透明事件
            child.config(cursor="hand2")
            self._bind_transparent_events(child)
            
            # 如果是容器，递归处理
            if isinstance(child, tk.Frame) and not self._is_button_container(child):
                self._process_container_children(child, excluded_elements)
    
    def _bind_transparent_events(self, widget):
        """绑定透明事件处理器，将事件传递给主卡片"""
        # 定义事件处理函数，注意使用独一的引用避免闭包问题
        def create_handler(event_name, card=self):
            return lambda e: card.event_generate(event_name)
            
        # 重置原有绑定
        for seq in ("<Enter>", "<Leave>", "<Button-1>", "<ButtonRelease-1>"):
            widget.unbind(seq)
        
        # 重新绑定事件
        widget.bind("<Enter>", create_handler("<Enter>"))
        widget.bind("<Leave>", create_handler("<Leave>"))
        widget.bind("<Button-1>", create_handler("<Button-1>"))
        widget.bind("<ButtonRelease-1>", create_handler("<ButtonRelease-1>"))
    
    def _is_button_related(self, widget):
        """详细检测元素是否与按钮相关"""
        # 如果是按钮本身或按钮的容器
        if isinstance(widget, FuturisticButton) or widget == self.elements.get("button_container"):
            return True
            
        # 如果是按钮的子元素
        if hasattr(widget, "master"):
            parent = widget.master
            if isinstance(parent, FuturisticButton):
                return True
            # 检查是否在按钮容器内
            if parent == self.elements.get("button_container"):
                return True
                
        return False
    
    def _is_button_container(self, container):
        """检查容器是否与按钮相关"""
        # 如果是按钮容器
        if container == self.elements.get("button_container"):
            return True
            
        # 检查是否包含按钮
        for child in container.winfo_children():
            if isinstance(child, FuturisticButton):
                return True
            if hasattr(child, "children"):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, FuturisticButton):
                        return True
                        
        return False
    
    def _on_press(self, event):
        """按下事件处理"""
        # 应用按下效果
        self.config(relief=tk.SUNKEN)
    
    def _on_release(self, event):
        """释放事件处理"""
        # 恢复高亮状态
        self.config(relief=tk.RAISED if self.hover_state else tk.FLAT)
        
        # 仅在鼠标仍在卡片上时触发点击事件
        # 获取鼠标当前位置
        x, y = event.x_root, event.y_root
        card_x, card_y = self.winfo_rootx(), self.winfo_rooty()
        card_width, card_height = self.winfo_width(), self.winfo_height()
        
        # 检查鼠标是否在卡片范围内
        if (card_x <= x <= card_x + card_width and 
            card_y <= y <= card_y + card_height):
            if self.callback:
                self.callback()
    
    def _on_enter(self, event):
        """鼠标进入事件处理"""
        self.hover_state = True
        self.highlight_card()
    
    def _on_leave(self, event):
        """鼠标离开事件处理"""
        self.hover_state = False
        self.unhighlight_card()
    
    def highlight_card(self):
        """应用卡片高亮效果"""
        # 如果已经高亮，不重复处理
        if self.highlight_state:
            return
            
        self.highlight_state = True
        
        # 取消任何正在进行的动画
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        
        # 使用动画过渡
        self._animate_highlight(True)
    
    def unhighlight_card(self):
        """取消卡片高亮效果"""
        # 如果未高亮，不重复处理
        if not self.highlight_state:
            return
            
        self.highlight_state = False
        
        # 取消任何正在进行的动画
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        
        # 使用动画过渡
        self._animate_highlight(False)
    
    def _animate_highlight(self, highlight):
        """动画卡片高亮/取消高亮效果"""
        self.animation_in_progress = True
        duration = ANIMATION["fast"]  # 使用标准动画时间
        steps = 8
        step_time = duration // steps
        
        # 初始和目标强调色
        if highlight:
            border_start = self.card_style["border_color"]
            border_end = self.accent_color
            title_start = COLORS["text_primary"]
            title_end = self.accent_color
        else:
            border_start = self.accent_color
            border_end = self.card_style["border_color"]
            title_start = self.accent_color
            title_end = COLORS["text_primary"]
        
        def animate_step(step):
            if step >= steps:
                # 动画结束，设置最终状态
                self.config(
                    relief=tk.RAISED if highlight else tk.FLAT,
                    highlightbackground=border_end,
                    highlightthickness=2 if highlight else self.card_style["border_width"],
                )
                self.elements["title"].config(fg=title_end)
                self.animation_in_progress = False
                self.animation_id = None
                return
            
            # 计算当前进度
            progress = step / steps
            
            # 插值计算当前颜色
            current_border = self._interpolate_color(border_start, border_end, progress)
            current_title = self._interpolate_color(title_start, title_end, progress)
            
            # 更新视觉元素
            self.config(
                relief=tk.RAISED if highlight else tk.FLAT,
                highlightbackground=current_border,
                highlightthickness=max(1, int(2 * progress)) if highlight else 
                               max(1, int(2 * (1 - progress)))
            )
            self.elements["title"].config(fg=current_title)
            
            # 计划下一步
            self.animation_id = self.after(step_time, lambda: animate_step(step + 1))
        
        # 开始动画
        animate_step(0)

    def _bind_recursive(self, container):
        """递归绑定嵌套组件"""
        for child in container.winfo_children():
            if isinstance(child, tk.Frame):
                self._bind_recursive(child)
            elif isinstance(child, (tk.Label, tk.Canvas)):
                child.config(cursor="hand2")
                child.bind("<Button-1>", lambda e, cmd=self.callback: cmd() if cmd else None)
