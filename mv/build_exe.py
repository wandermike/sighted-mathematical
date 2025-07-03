import PyInstaller.__main__
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建图标路径
icon_path = os.path.join(current_dir, 'tu.ico')

# 需要添加的数据文件
datas = [
    (os.path.join(current_dir, 'tu.ico'), '.'),
]

# 查找 logo.png 并添加
logo_path = os.path.join(current_dir, 'logo.png')
if os.path.exists(logo_path):
    datas.append((logo_path, '.'))

# 获取目录中所有的 py 文件
py_files = []
for file in os.listdir(current_dir):
    if file.endswith(".py") and file != "build_exe.py" and file != "main.py":
        py_files.append(os.path.join(current_dir, file))

# PyInstaller 命令行参数
args = [
    'main.py',  # 主脚本
    '--name=MathVisualization',  # EXE名称
    f'--icon={icon_path}',  # 图标
    '--noconfirm',  # 不询问确认
    '--clean',  # 清理之前的构建
    '--windowed',  # 无控制台窗口
    '--uac-admin',  # 请求管理员权限
    '--add-data=tu.ico;.',  # 添加图标作为数据文件
    '--log-level=ERROR',  # 减少日志输出
]

# 添加所有 Python 模块
for py_file in py_files:
    args.append(f'--hidden-import={os.path.basename(py_file)[:-3]}')

# 添加额外的数据文件
for src, dst in datas:
    if os.path.exists(src):
        args.append(f'--add-data={src};{dst}')

# 添加必要的第三方模块
hidden_imports = [
    'numpy', 'pandas', 'matplotlib', 'PIL', 'seaborn', 'requests', 
    'pandasai', 'ttkthemes', 'tkinter', 'json', 'datetime', 'openpyxl',
    'sympy', 'matplotlib.backends.backend_tkagg', 'matplotlib.figure', 
    'matplotlib.animation', 'matplotlib.font_manager', 'functools', 
    'warnings', 'math', 'threading', 'types', 'importlib', 'logging',
    'scipy', 'sympy.parsing.sympy_parser'
]
for module in hidden_imports:
    args.append(f'--hidden-import={module}')

# 设置环境变量，避免生成日志文件
os.environ["PANDASAI_SKIP_LOGGING_CONFIG"] = "true"
os.environ["PANDASAI_LOG_LEVEL"] = "CRITICAL"

# 执行 PyInstaller
PyInstaller.__main__.run(args)

print("打包完成！可执行文件位于 dist/MathVisualization 文件夹中。")
