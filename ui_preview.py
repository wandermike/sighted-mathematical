import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import sys

# --- Helper function to find resources ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Simple debug log function ---
def log(message):
    print(f"DEBUG: {message}")

class UIPreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数学可视化教学工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Colors exactly matching the screenshot
        self.bg_dark_blue = "#1A3665"    # Dark navy blue background
        self.bg_navy = "#223C6A"         # Navy blue for header/footer/cards
        self.accent_red = "#E74C3C"      # Red for card borders
        self.accent_orange = "#FF9933"   # Orange accent color
        self.accent_green = "#2ECC71"    # Green accent for middle school
        self.text_white = "#FFFFFF"      # White text
        self.text_light = "#D0D0D0"      # Light gray text
        
        # Current section (university or middle school)
        self.current_section = "university"
        
        # Configure base style to match screenshot
        self.root.config(bg=self.bg_dark_blue)
        
        # Set app icon if available
        try:
            self.root.iconbitmap(resource_path("tu.ico"))
        except Exception as e:
            log(f"Could not set app icon: {e}")
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg=self.bg_dark_blue)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header = tk.Frame(self.main_frame, bg=self.bg_navy, height=80)
        self.header.pack(fill=tk.X, side=tk.TOP)
        
        # Title
        self.title_label = tk.Label(
            self.header, 
            text="数学可视化教学工具",
            font=("SimHei", 24, "bold"),
            bg=self.bg_navy,
            fg=self.text_white
        )
        self.title_label.place(relx=0.24, rely=0.5, anchor="center")
        
        # Green indicator dot
        self.indicator = tk.Canvas(
            self.header, width=15, height=15, 
            bg=self.bg_navy, highlightthickness=0
        )
        self.indicator.place(relx=0.45, rely=0.5, anchor="center")
        self.indicator.create_oval(0, 0, 15, 15, fill="#00FF80", outline="")
        
        # Load the logo
        try:
            img = Image.open(resource_path("logo.ico"))
            img = img.resize((60, 60), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = tk.Label(
                self.header, 
                image=self.logo_image, 
                bg=self.bg_navy
            )
            logo_label.place(relx=0.95, rely=0.5, anchor="e")
        except Exception as e:
            log(f"Logo error: {e}")
            # Fallback to blue cube
            self.logo_canvas = tk.Canvas(
                self.header, width=60, height=60,
                bg=self.bg_navy, highlightthickness=0
            )
            self.logo_canvas.place(relx=0.95, rely=0.5, anchor="e")
            self.create_blue_cube_logo(self.logo_canvas)
        
        # Content area with section selector
        self.content_area = tk.Frame(self.main_frame, bg=self.bg_dark_blue)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 0))
        
        # Create section selector tabs
        self.create_section_selector()
        
        # Container for actual content (with some space below the tabs)
        self.content = tk.Frame(self.content_area, bg=self.bg_dark_blue)
        self.content.pack(fill=tk.BOTH, expand=True, pady=(15, 10))
        
        # Configure content grid
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        self.content.rowconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)
        
        # Load icons
        self.load_icons()
        
        # Create the university cards initially
        self.create_university_cards()
        
        # Footer
        self.footer = tk.Frame(self.main_frame, bg=self.bg_navy, height=40)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Copyright text
        copyright_label = tk.Label(
            self.footer, 
            text="© 2025 数学可视化教学平台", 
            font=("SimHei", 10), 
            bg=self.bg_navy,
            fg=self.text_light
        )
        copyright_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Footer logo
        try:
            img = Image.open(resource_path("logo.ico"))
            img = img.resize((30, 30), Image.LANCZOS)
            self.footer_logo_image = ImageTk.PhotoImage(img)
            footer_logo_label = tk.Label(
                self.footer, 
                image=self.footer_logo_image, 
                bg=self.bg_navy
            )
            footer_logo_label.pack(side=tk.LEFT, padx=20)
        except Exception as e:
            log(f"Footer logo error: {e}")
            # Fallback to blue cube
            self.footer_logo = tk.Canvas(
                self.footer, width=40, height=40,
                bg=self.bg_navy, highlightthickness=0
            )
            self.footer_logo.pack(side=tk.LEFT, padx=20)
            self.create_blue_cube_logo(self.footer_logo, size=30)

    def create_section_selector(self):
        """Create tabs to switch between university and middle school content"""
        # Selector frame
        self.selector_frame = tk.Frame(self.content_area, bg=self.bg_dark_blue)
        self.selector_frame.pack(fill=tk.X)
        
        # Tab dimensions exactly matching the screenshot
        tab_width = 135
        tab_height = 40
        tab_spacing = 10
        tab_font = ("SimHei", 16)
        
        # Container for centering tabs
        center_frame = tk.Frame(self.selector_frame, bg=self.bg_dark_blue)
        center_frame.pack(anchor="w", padx=40)
        
        # University tab (selected by default)
        self.university_tab = tk.Frame(
            center_frame,
            width=tab_width,
            height=tab_height,
            bg=self.bg_navy,
            highlightbackground=self.accent_red,
            highlightthickness=2,
            cursor="hand2"
        )
        self.university_tab.pack(side=tk.LEFT, padx=(0, tab_spacing))
        self.university_tab.pack_propagate(False)  # Maintain size
        
        self.university_label = tk.Label(
            self.university_tab,
            text="大学内容",
            font=tab_font,
            bg=self.bg_navy,
            fg=self.text_white,
            cursor="hand2"
        )
        self.university_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Middle school tab
        self.middle_school_tab = tk.Frame(
            center_frame,
            width=tab_width,
            height=tab_height,
            bg=self.bg_navy,
            highlightbackground=self.accent_green,
            highlightthickness=2,
            cursor="hand2"
        )
        self.middle_school_tab.pack(side=tk.LEFT)
        self.middle_school_tab.pack_propagate(False)  # Maintain size
        
        self.middle_school_label = tk.Label(
            self.middle_school_tab,
            text="中学内容",
            font=tab_font,
            bg=self.bg_navy,
            fg=self.text_white,
            cursor="hand2"
        )
        self.middle_school_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind click events to both tabs and their labels
        self.university_tab.bind("<Button-1>", lambda e: self.switch_section("university"))
        self.university_label.bind("<Button-1>", lambda e: self.switch_section("university"))
        self.middle_school_tab.bind("<Button-1>", lambda e: self.switch_section("middle_school"))
        self.middle_school_label.bind("<Button-1>", lambda e: self.switch_section("middle_school"))
        
        # Create hover effects
        self.create_tab_hover_effects()

    def create_tab_hover_effects(self):
        """Create hover effects for tabs"""
        def university_on_enter(e):
            if self.current_section != "university":
                self.university_tab.config(highlightbackground="#FF6B6B")  # Brighter red on hover
                
        def university_on_leave(e):
            if self.current_section != "university":
                self.university_tab.config(highlightbackground=self.accent_red)
                
        def middle_school_on_enter(e):
            if self.current_section != "middle_school":
                self.middle_school_tab.config(highlightbackground="#4EEC91")  # Brighter green on hover
                
        def middle_school_on_leave(e):
            if self.current_section != "middle_school":
                self.middle_school_tab.config(highlightbackground=self.accent_green)
        
        # Bind hover events for university tab and label
        self.university_tab.bind("<Enter>", university_on_enter)
        self.university_tab.bind("<Leave>", university_on_leave)
        self.university_label.bind("<Enter>", university_on_enter)
        self.university_label.bind("<Leave>", university_on_leave)
        
        # Bind hover events for middle school tab and label
        self.middle_school_tab.bind("<Enter>", middle_school_on_enter)
        self.middle_school_tab.bind("<Leave>", middle_school_on_leave)
        
    def switch_section(self, section):
        """Switch between university and middle school content"""
        if section == self.current_section:
            return
            
        self.current_section = section
        
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()
            
        # Update tab appearances
        if section == "university":
            # Make university tab appear active
            self.university_tab.config(highlightbackground=self.accent_red, highlightthickness=3)
            self.university_label.config(fg=self.text_white)
            # Make middle school tab appear inactive
            self.middle_school_tab.config(highlightbackground=self.accent_green, highlightthickness=2)
            self.middle_school_label.config(fg=self.text_white)
            # Create university cards
            self.create_university_cards()
        else:
            # Make university tab appear inactive
            self.university_tab.config(highlightbackground=self.accent_red, highlightthickness=2)
            self.university_label.config(fg=self.text_white)
            # Make middle school tab appear active
            self.middle_school_tab.config(highlightbackground=self.accent_green, highlightthickness=3)
            self.middle_school_label.config(fg=self.text_white)
            # Create middle school cards
            self.create_middle_school_cards()

    def create_blue_cube_logo(self, canvas, size=50):
        """Create a 3D blue cube logo as fallback"""
        canvas.create_polygon(
            size/2, 10, 
            size-10, size/2, 
            size/2, size-10, 
            10, size/2,
            fill="#3498DB", outline=""
        )
    
    def load_icons(self):
        """Load all icon images from files"""
        self.icons = {}
        
        # Load each icon with fallback to programmatically created ones
        icon_files = {
            "gaoshup": "gaoshup.ico",    # Advanced math
            "xiandaip": "xiandaip.ico",  # Linear algebra
            "gailvp": "gailvp.ico",      # Probability
            "aip": "AIP.ico"             # AI data analysis
        }
        
        # Try to load icons from files
        for key, filename in icon_files.items():
            try:
                img = Image.open(resource_path(filename))
                img = img.resize((64, 64), Image.LANCZOS)
                self.icons[key] = ImageTk.PhotoImage(img)
                log(f"Successfully loaded icon: {filename}")
            except Exception as e:
                log(f"Could not load icon {filename}: {e}")
                # Will create fallback icons in create_cards if needed

    def create_university_cards(self):
        """Create the university cards (four cards as in the original screenshot)"""
        # Card 1: 高等数学
        self.create_card(
            row=0, col=0,
            title="高等数学",
            desc="函数、微积分、微分方程等交互式可视化",
            icon=self.icons.get("gaoshup"),
            fallback_icon_type="math",
            border_color=self.accent_red
        )
        
        # Card 2: 线性代数
        self.create_card(
            row=0, col=1,
            title="线性代数",
            desc="矩阵运算、特征值分析等直观呈现",
            icon=self.icons.get("xiandaip"),
            fallback_icon_type="matrix",
            border_color=self.accent_red
        )
        
        # Card 3: 概率统计
        self.create_card(
            row=1, col=0,
            title="概率统计",
            desc="概率分布、统计分析可视化与模拟",
            icon=self.icons.get("gailvp"),
            fallback_icon_type="pie",
            border_color=self.accent_red
        )
        
        # Card 4: AI 数据分析
        self.create_card(
            row=1, col=1,
            title="AI 数据分析",
            desc="基于人工智能的数据分析与预测",
            icon=self.icons.get("aip"),
            fallback_icon_type="ai",
            border_color=self.accent_red
        )

    def create_middle_school_cards(self):
        """Create cards for middle school content"""
        # Card 1: 代数
        self.create_card(
            row=0, col=0,
            title="代数基础",
            desc="方程、不等式、函数与图像的可视化探索",
            icon=None,
            fallback_icon_type="algebra",
            border_color=self.accent_green
        )
        
        # Card 2: 几何
        self.create_card(
            row=0, col=1,
            title="几何图形",
            desc="平面与空间几何、图形变换的动态演示",
            icon=None,
            fallback_icon_type="geometry",
            border_color=self.accent_green
        )
        
        # Card 3: 初等统计
        self.create_card(
            row=1, col=0,
            title="初等统计",
            desc="数据分析、概率初步和统计图表制作",
            icon=None,
            fallback_icon_type="statistics",
            border_color=self.accent_green
        )
        
        # Card 4: 数学竞赛
        self.create_card(
            row=1, col=1,
            title="数学竞赛",
            desc="经典题型解析与解题思路训练",
            icon=None,
            fallback_icon_type="contest",
            border_color=self.accent_green
        )

    def create_card(self, row, col, title, desc, icon=None, fallback_icon_type=None, border_color=None):
        """Create a card with colored border"""
        # Use default border color if not specified
        if border_color is None:
            border_color = self.accent_red
            
        # Card frame with padding
        padding = 15
        card_frame = tk.Frame(self.content, bg=self.bg_dark_blue)
        card_frame.grid(row=row, column=col, padx=padding, pady=padding, sticky="nsew")
        
        # Card with colored border
        card = tk.Frame(
            card_frame, 
            bg=self.bg_navy,
            highlightbackground=border_color,
            highlightthickness=2
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            card, 
            text=title,
            font=("SimHei", 22, "bold"),
            bg=self.bg_navy,
            fg=self.text_white
        )
        title_label.pack(pady=(40, 20))
        
        # Icon (use provided icon or create fallback)
        if icon:
            icon_label = tk.Label(
                card,
                image=icon,
                bg=self.bg_navy
            )
            icon_label.pack(pady=10)
        elif fallback_icon_type:
            # Create fallback icon
            fallback_icon = self.create_fallback_icon(fallback_icon_type, border_color)
            icon_label = tk.Label(
                card,
                image=fallback_icon,
                bg=self.bg_navy
            )
            icon_label.pack(pady=10)
        
        # Description
        desc_label = tk.Label(
            card, 
            text=desc,
            font=("SimHei", 12),
            bg=self.bg_navy,
            fg=self.text_light
        )
        desc_label.pack(pady=20)

    def create_fallback_icon(self, icon_type, color=None):
        """Create a fallback icon if the file couldn't be loaded"""
        if color is None:
            color = self.accent_red
            
        # Create a new image for the icon
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # University content icons
        if icon_type == "math":
            # Math icon - coordinate system
            draw.ellipse((4, 4, 60, 60), fill="#421880")  # Purple circle
            draw.line((32, 4, 32, 60), fill="white", width=2)  # Vertical line
            draw.line((4, 32, 60, 32), fill="white", width=2)  # Horizontal line
            fallback = ImageTk.PhotoImage(img)
            self.icons["gaoshup"] = fallback
            return fallback
            
        elif icon_type == "matrix":
            # Matrix icon - grid of nodes
            for y in range(3):
                for x in range(3):
                    cx = 16 + x * 16
                    cy = 16 + y * 16
                    draw.ellipse((cx-4, cy-4, cx+4, cy+4), outline="black", fill="white")
                    
                    # Connect horizontally
                    if x < 2:
                        draw.line((cx+4, cy, cx+12, cy), fill="black", width=1)
            fallback = ImageTk.PhotoImage(img)
            self.icons["xiandaip"] = fallback
            return fallback
            
        elif icon_type == "pie":
            # Pie chart icon
            draw.ellipse((4, 4, 60, 60), fill="#2D3A47")  # Dark background
            draw.pieslice((4, 4, 60, 60), start=0, end=60, fill="#FF9933")  # Orange slice
            fallback = ImageTk.PhotoImage(img)
            self.icons["gailvp"] = fallback
            return fallback
            
        elif icon_type == "ai":
            # AI badge icon
            points = [(32, 4), (56, 16), (56, 48), (32, 60), (8, 48), (8, 16)]
            draw.polygon(points, fill="#FF9933")  # Orange badge
            
            # "Ai" text (simplified)
            draw.rectangle((24, 20, 40, 44), fill="white")  # A
            draw.rectangle((28, 24, 36, 40), fill="#FF9933")  # A cutout
            draw.rectangle((42, 20, 48, 44), fill="white")  # i
            fallback = ImageTk.PhotoImage(img)
            self.icons["aip"] = fallback
            return fallback
            
        # Middle school content icons
        elif icon_type == "algebra":
            # Algebra icon - equation
            draw.ellipse((4, 4, 60, 60), fill="#2ECC71")  # Green circle
            
            # Draw "x²" in white
            draw.line((20, 32, 40, 32), fill="white", width=2)  # Equal sign
            draw.line((20, 40, 40, 40), fill="white", width=2)  # Equal sign
            
            # x and y
            draw.line((25, 20, 35, 30), fill="white", width=2)  # x diagonal 1
            draw.line((25, 30, 35, 20), fill="white", width=2)  # x diagonal 2
            
            # 2 (superscript)
            draw.rectangle((40, 18, 45, 23), fill="white", outline="white")
            
            icon = ImageTk.PhotoImage(img)
            # Store it for reuse
            self.icons["algebra"] = icon
            return icon
            
        elif icon_type == "geometry":
            # Geometry icon - shapes
            background_color = "#2ECC71"  # Green
            
            # Circle background
            draw.ellipse((4, 4, 60, 60), fill=background_color)
            
            # Draw triangle in white
            draw.polygon([(20, 45), (32, 20), (44, 45)], fill=None, outline="white", width=2)
            
            # Draw circle
            draw.ellipse((25, 25, 39, 39), fill=None, outline="white", width=2)
            
            icon = ImageTk.PhotoImage(img)
            self.icons["geometry"] = icon
            return icon
            
        elif icon_type == "statistics":
            # Statistics icon - bar chart
            background_color = "#2ECC71"  # Green
            
            # Circle background
            draw.ellipse((4, 4, 60, 60), fill=background_color)
            
            # Draw bar chart in white
            bar_width = 8
            draw.rectangle((16, 40, 16+bar_width, 48), fill="white", outline="white")
            draw.rectangle((28, 30, 28+bar_width, 48), fill="white", outline="white")
            draw.rectangle((40, 20, 40+bar_width, 48), fill="white", outline="white")
            
            # X and Y axis
            draw.line((12, 48, 52, 48), fill="white", width=2)  # X-axis
            draw.line((12, 18, 12, 48), fill="white", width=2)  # Y-axis
            
            icon = ImageTk.PhotoImage(img)
            self.icons["statistics"] = icon
            return icon
            
        elif icon_type == "contest":
            # Math contest icon - trophy
            background_color = "#2ECC71"  # Green
            
            # Circle background
            draw.ellipse((4, 4, 60, 60), fill=background_color)
            
            # Draw trophy in white
            # Cup
            draw.rectangle((25, 15, 39, 30), fill=None, outline="white", width=2)
            # Base
            draw.rectangle((28, 40, 36, 45), fill="white", outline="white", width=1)
            # Stem
            draw.rectangle((30, 30, 34, 40), fill="white", outline="white", width=1)
            # Handles
            draw.arc([15, 15, 25, 30], start=270, end=90, fill="white", width=2)
            draw.arc([39, 15, 49, 30], start=90, end=270, fill="white", width=2)
            
            icon = ImageTk.PhotoImage(img)
            self.icons["contest"] = icon
            return icon
        
        # Default fallback
        draw.rectangle((10, 10, 54, 54), fill="#3498DB")
        default_icon = ImageTk.PhotoImage(img)
        return default_icon

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = UIPreviewApp(root)
    root.mainloop() 