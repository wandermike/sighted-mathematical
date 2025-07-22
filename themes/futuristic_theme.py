import tkinter as tk

# 主题颜色定义 - 使用HSL色彩系统确保协调性
COLORS = {
    # 基础颜色
    "bg_dark": "#0F2544",          # 主背景 - 深蓝色（调亮）
    "bg_medium": "#1A3056",        # 卡片/面板背景 - 中深蓝（调亮）
    "bg_light": "#254575",         # 高亮区域 - 浅蓝色（调亮）
    "bg_darker": "#0A1829",        # 底部/顶部栏 - 更深的蓝色（调亮）
    
    # 文本颜色
    "text_primary": "#FFFFFF",     # 主要文本 - 纯白色（调亮）
    "text_secondary": "#A0A8C0",   # 次要文本 - 灰蓝色（调亮）
    "text_tertiary": "#7282A0",    # 第三级文本 - 更暗的灰蓝（调亮）
    "text_disabled": "#4D5675",    # 禁用文本 - 深灰蓝（调亮）
    
    # 强调色
    "accent_primary": "#72FFDE",   # 主强调 - 亮青色（调亮）
    "accent_secondary": "#30C5FF", # 次强调 - 亮蓝色（调亮）
    "accent_primary_transparent": "#72FFDE50",  # 透明主强调色（调亮）
    "accent_tertiary": "#8E7FFF",  # 第三强调 - 紫色（调亮）
    
    # 功能色
    "success": "#30FFAA",          # 成功提示 - 绿色（调亮）
    "warning": "#FFDF30",          # 警告提示 - 金色（调亮）
    "error": "#FF6969",            # 错误提示 - 红色（调亮）
    "info": "#66C5FF",             # 信息提示 - 蓝色（调亮）
    
    # 特效色
    "glow": "#72FFDE50",           # 发光效果 - 半透明青色（调亮）
    "shadow": "#00000070",         # 阴影效果 - 半透明黑色（调整透明度）
    "overlay": "#0F2544A0",        # 遮罩层 - 半透明背景色（调亮）
    
    # 渐变色
    "gradient_start": "#0F2544",   # 渐变起始 - 深蓝（调亮）
    "gradient_end": "#1A3056",     # 渐变结束 - 中蓝（调亮）
    "bg_card": "#2F4D7A"           # 新增卡片背景浅色
}

# 字体系统 - 使用比例关系确保统一性
FONTS = {
    "title": ("Arial", 24, "bold"),       # 主标题
    "subtitle": ("Arial", 18, "bold"),    # 子标题
    "section": ("Arial", 16, "bold"),     # 分区标题
    "button": ("Arial", 12),              # 按钮文本
    "text": ("Arial", 11),                # 正文
    "small": ("Arial", 9),                # 小文本
    "tiny": ("Arial", 8)                  # 极小文本
}

# 边框样式 - 标准化边框粗细和颜色
BORDERS = {
    "normal": {"width": 1, "color": COLORS["accent_primary"]},
    "highlight": {"width": 2, "color": COLORS["accent_secondary"]},
    "active": {"width": 2, "color": COLORS["success"]},
    "container": {"width": 1, "color": COLORS["bg_light"]},
    "subtle": {"width": 1, "color": COLORS["text_tertiary"]}
}

# 间距系统 - 基于8像素网格确保视觉一致性
SPACING = {
    "xxs": 4,    # 极小间距
    "xs": 8,     # 小间距
    "sm": 16,    # 中小间距
    "md": 24,    # 中间距
    "lg": 32,    # 大间距
    "xl": 48,    # 特大间距
    "xxl": 64    # 极大间距
}

# 圆角系统 - 统一的圆角半径
RADII = {
    "none": 0,    # 无圆角
    "sm": 4,      # 小圆角
    "md": 8,      # 中圆角
    "lg": 12,     # 大圆角
    "xl": 20,     # 特大圆角
    "round": 1000  # 圆形（大值确保完全圆形）
}

# 阴影系统 - 统一的阴影效果
SHADOWS = {
    "none": "",  # 无阴影
    "sm": "#00000022 0px 2px 4px",  # 小阴影
    "md": "#00000033 0px 4px 8px",  # 中阴影
    "lg": "#00000044 0px 8px 16px"  # 大阴影
}

# 动画时间 - 统一的动画持续时间
ANIMATION = {
    "instant": 50,   # 瞬时 (50ms)
    "fast": 150,     # 快速 (150ms)
    "normal": 300,   # 标准 (300ms)
    "slow": 500,     # 缓慢 (500ms)
    "vslow": 800     # 很慢 (800ms)
}

# 卡片设计标准 - 确保视觉一致性
CARD_STYLES = {
    "standard": {
        "bg": COLORS["bg_medium"],
        "border_color": COLORS["bg_light"],
        "border_width": 0,
        "padding": SPACING["sm"],
        "radius": RADII["md"]
    },
    "highlighted": {
        "bg": COLORS["bg_medium"],
        "border_color": COLORS["accent_primary"],
        "border_width": 2,
        "padding": SPACING["sm"],
        "radius": RADII["md"]
    },
    "elevated": {
        "bg": COLORS["bg_medium"],
        "border_color": COLORS["bg_light"],
        "border_width": 0,
        "padding": SPACING["sm"],
        "radius": RADII["md"],
        "shadow": SHADOWS["md"]
    },
    "clickable": {
        "bg": COLORS["bg_medium"],
        "border_color": COLORS["bg_light"],
        "border_width": 1,
        "padding": SPACING["sm"],
        "radius": RADII["md"],
        "hover_bg": COLORS["bg_light"],
        "active_bg": COLORS["accent_primary_transparent"]
    }
}

# 样式配置函数
def apply_theme(widget, widget_type="default"):
    """为组件应用未来科技风格"""
    
    if widget_type == "default" or widget_type == "frame":
        widget.configure(bg=COLORS["bg_dark"])
    
    elif widget_type == "card":
        widget.configure(
            bg=COLORS["bg_medium"],
            highlightbackground=COLORS["bg_light"],
            highlightthickness=1,
            bd=0
        )
    
    elif widget_type == "button":
        widget.configure(
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent_primary"],
            activeforeground=COLORS["bg_dark"],
            font=FONTS["button"],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING["sm"],
            pady=SPACING["xs"],
            cursor="hand2"
        )
    
    elif widget_type == "label":
        widget.configure(
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            font=FONTS["text"]
        )
    
    elif widget_type == "title_label":
        widget.configure(
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            font=FONTS["title"]
        )
    
    elif widget_type == "subtitle_label":
        widget.configure(
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            font=FONTS["subtitle"]
        )
    
    elif widget_type == "entry":
        widget.configure(
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["accent_primary"],  # 光标颜色
            selectbackground=COLORS["accent_secondary"],
            selectforeground=COLORS["text_primary"],
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor=COLORS["accent_primary"],
            highlightbackground=COLORS["bg_medium"],
            font=FONTS["text"]
        )
    
    elif widget_type == "header":
        widget.configure(
            bg=COLORS["bg_darker"],
            highlightbackground=COLORS["accent_primary"],
            highlightthickness=1
        )
    
    elif widget_type == "footer":
        widget.configure(
            bg=COLORS["bg_darker"],
            highlightbackground=COLORS["bg_light"],
            highlightthickness=1
        )
        
    return widget  # 返回组件以便链式调用
