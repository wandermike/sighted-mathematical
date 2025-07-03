import tkinter as tk
import time
import math
import random
from themes.futuristic_theme import COLORS

def fade_in(widget, duration=500):
    """将控件以淡入效果显示"""
    if not hasattr(widget.winfo_toplevel(), 'attributes'):
        # 对于不支持透明度的控件，直接显示
        widget.pack(fill=tk.BOTH, expand=True)
        return
        
    # 保存原始透明度值
    try:
        original_alpha = widget.winfo_toplevel().attributes('-alpha')
    except:
        original_alpha = 1.0
    
    # 设置初始透明度为0
    widget.winfo_toplevel().attributes('-alpha', 0.0)
    widget.update()
    
    # 显示组件
    widget.pack(fill=tk.BOTH, expand=True)
    
    # 动画效果
    steps = 20
    step_time = duration / steps
    for i in range(steps + 1):
        alpha = i / steps * original_alpha
        try:
            widget.winfo_toplevel().attributes('-alpha', alpha)
            widget.update()
            time.sleep(step_time / 1000)
        except:
            pass

def slide_in(widget, direction="left", duration=300):
    """将控件以滑入效果显示
    
    参数:
        widget: 要显示的控件
        direction: 滑入方向，可以是 "left", "right", "up", "down"
        duration: 动画持续时间（毫秒）
    """
    # 获取父容器
    parent = widget.master
    width = parent.winfo_width()
    height = parent.winfo_height()
    
    # 设置初始位置
    if direction == "left":
        widget.place(x=width, y=0, width=width, height=height)
    elif direction == "right":
        widget.place(x=-width, y=0, width=width, height=height)
    elif direction == "up":
        widget.place(x=0, y=height, width=width, height=height)
    elif direction == "down":
        widget.place(x=0, y=-height, width=width, height=height)
    
    # 开始动画
    steps = 20
    step_time = duration / steps
    
    for i in range(steps + 1):
        progress = i / steps
        
        if direction == "left":
            x = width * (1 - progress)
            y = 0
        elif direction == "right":
            x = -width * (1 - progress)
            y = 0
        elif direction == "up":
            x = 0
            y = height * (1 - progress)
        elif direction == "down":
            x = 0
            y = -height * (1 - progress)
        
        widget.place(x=x, y=y, width=width, height=height)
        parent.update()
        time.sleep(step_time / 1000)
    
    # 完成动画，使用pack替代place
    widget.place_forget()
    widget.pack(fill=tk.BOTH, expand=True)

class ParticleSystem:
    """粒子系统，用于创建背景动画效果"""
    def __init__(self, canvas, num_particles=30, particle_size=3, 
                 colors=[COLORS["accent_primary"], COLORS["accent_secondary"]]):
        self.canvas = canvas
        self.particles = []
        self.colors = colors
        
        # 创建粒子
        for _ in range(num_particles):
            x = random.randint(0, self.canvas.winfo_width() or 800)
            y = random.randint(0, self.canvas.winfo_height() or 600)
            size = random.randint(1, particle_size)
            speed = random.uniform(0.2, 1.0)
            angle = random.uniform(0, 2 * math.pi)
            color = random.choice(colors)
            
            particle = {
                "id": self.canvas.create_oval(x, y, x+size, y+size, 
                                            fill=color, outline=""),
                "x": x,
                "y": y,
                "size": size,
                "speed": speed,
                "angle": angle,
                "color": color
            }
            self.particles.append(particle)
    
    def update(self):
        """更新粒子位置和状态"""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 600
        
        for particle in self.particles:
            # 计算新位置
            dx = math.cos(particle["angle"]) * particle["speed"]
            dy = math.sin(particle["angle"]) * particle["speed"]
            
            particle["x"] += dx
            particle["y"] += dy
            
            # 检查边界
            if (particle["x"] < -particle["size"] or 
                particle["x"] > width + particle["size"] or
                particle["y"] < -particle["size"] or 
                particle["y"] > height + particle["size"]):
                # 重置位置
                if random.choice([True, False]):
                    # 从左右边界重新进入
                    particle["x"] = -particle["size"] if dx > 0 else width + particle["size"]
                    particle["y"] = random.randint(0, height)
                else:
                    # 从上下边界重新进入
                    particle["x"] = random.randint(0, width)
                    particle["y"] = -particle["size"] if dy > 0 else height + particle["size"]
                
                # 更新速度和角度
                particle["speed"] = random.uniform(0.2, 1.0)
                particle["angle"] = random.uniform(0, 2 * math.pi)
            
            # 更新Canvas上的粒子
            x, y = particle["x"], particle["y"]
            size = particle["size"]
            self.canvas.coords(particle["id"], x, y, x+size, y+size)
        
        # 30毫秒后再次调用
        self.canvas.after(30, self.update)
