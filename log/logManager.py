#!/usr/bin/env python3
from datetime import datetime
from typing import Literal, Optional, Union, TextIO
import sys

# 图标和颜色配置
ICONS = {
    "DEBUG": "🐛",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
}

# 跨平台颜色支持
if sys.platform == "win32":
    try:
        import colorama
        colorama.init()
        COLORS = {
            "DEBUG": colorama.Fore.BLUE,
            "INFO": colorama.Fore.GREEN,
            "WARNING": colorama.Fore.YELLOW,
            "ERROR": colorama.Fore.RED,
            "RESET": colorama.Style.RESET_ALL,
        }
    except ImportError:
        # 回退到无颜色模式
        COLORS = {level: "" for level in ICONS}
        COLORS["RESET"] = ""
else:
    # Linux/macOS ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[94m",  # 亮蓝色
        "INFO": "\033[92m",   # 亮绿色
        "WARNING": "\033[93m",  # 亮黄色
        "ERROR": "\033[91m",  # 亮红色
        "RESET": "\033[0m",   # 重置样式
    }

log_file = "./log.log"

def log(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"],
    source: str,
    message: str,
):
    """
    记录带颜色和图标的日志信息，支持输出到文件
    
    :param level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    :param source: 日志来源
    :param message: 日志内容
    :param log_file: 可选的日志文件路径或文件对象
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = ICONS.get(level, "")
    color = COLORS.get(level, "")
    reset = COLORS["RESET"]
    
    # 构建日志条目
    log_entry = f"[{timestamp}] [{level}] [{source}] {message}"
    colored_entry = f"{color}{icon} {log_entry}{reset}"
    
    # 输出到控制台
    print(colored_entry)
    
    # 输出到文件（如果需要）
    if log_file is not None:
        try:
            if isinstance(log_file, str):
                # 如果是文件路径，以追加模式打开
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")
            else:
                # 如果是文件对象，直接写入
                log_file.write(log_entry + "\n")
        except Exception as e:
            # 文件写入错误处理
            error_msg = f"日志写入失败: {str(e)}"
            print(f"{COLORS['ERROR']}❌ {error_msg}{COLORS['RESET']}")