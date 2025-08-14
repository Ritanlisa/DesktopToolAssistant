#!/usr/bin/env python3
import os
import pygame
import threading
import queue
from typing import Literal
from pygame.locals import *
from OpenGL.GL import *

import live2d.v2 as live2dv2
from live2d.v2 import StandardParams as StandardParamsv2
from live2d.v2 import MotionPriority as MotionPriorityv2

import live2d.v3 as live2dv3
from live2d.v3 import StandardParams as StandardParamsv3
from live2d.v3 import MotionPriority as MotionPriorityv3

import ctypes
from .general import DisplayerType
from log import log

class Live2DModel:
    """封装 Live2D 模型的加载、渲染和逻辑。"""

    def __init__(
        self, model_path: str, canvas_width: int = 800, canvas_height: int = 600, model_type: Literal["v2", "v3"] = "v3"
    ):
        self.model_type = model_type
        
        if model_type == "v2":
            self.model = live2dv2.LAppModel()
        elif model_type == "v3":
            display = (800,600)
            pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
            live2dv3.glewInit()
            self.model = live2dv3.LAppModel()
        else:
            raise ValueError("Unsupported model type. Use 'v2' or 'v3'.")

        
        log("INFO", "Live2D", f"Loading model from {model_path}")
        self.model.LoadModelJson(model_path)
        self.model.Resize(canvas_width, canvas_height)
        self.model.SetAutoBlinkEnable(True)
        self.model.SetAutoBreathEnable(True)
        self.model.StartRandomMotion()

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.dx = 0.0
        self.dy = 0.0
        self.scale = 1.0
        self.lip_sync_value = 0.0  # 当前口型值

    def update(self, delta_time: float):
        """更新模型状态"""
        self.model.Update()

    def draw(self):
        """绘制模型"""
        self.model.Draw()

    def set_lip_sync_value(self, value: float):
        """设置口型同步值"""
        self.lip_sync_value = value
        if self.model_type == "v2":
            self.model.SetParameterValue(StandardParamsv2.ParamMouthOpenY, value)
        elif self.model_type == "v3":
            self.model.SetParameterValue(StandardParamsv3.ParamMouthOpenY, value)
        else:
            raise ValueError("Unsupported model type.")

    def play_motion(self, group: str, no: int):
        """播放指定动作"""
        if self.model_type == "v2":
            self.model.StartMotion(group, no, MotionPriorityv2.FORCE, None, None)
        elif self.model_type == "v3":
            self.model.StartMotion(group, no, MotionPriorityv3.FORCE, None, None)
        else:
            raise ValueError("Unsupported model type.")

    def set_offset(self, dx: float, dy: float):
        """设置模型偏移量"""
        self.model.SetOffset(dx, dy)

    def set_scale(self, scale: float):
        """设置模型缩放比例"""
        self.model.SetScale(scale)


@DisplayerType("live2D")
class live2D_displayer:
    def __init__(
        self,
        model_path: str,
        canvas_width: int = 800,
        canvas_height: int = 600,
        window_pos: tuple = (100, 100),
        type: Literal["live2D", "Live2D"] = "Live2D",
        model_version: Literal["v2", "v3"] = "v3",
        **kwargs
    ):
        self.model_path = model_path
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.window_pos = window_pos
        self.lip_sync_value = 0.0
        self.running = True
        self.model_version = model_version

        # 注册口型同步回调
        self.lip_sync_interface = kwargs.get("lip_sync_interface", None)
        if self.lip_sync_interface:
            self.lip_sync_interface.register_callback(self.set_lip_sync_value)

        # 创建窗口线程
        self.thread = threading.Thread(target=self._run_window)
        self.thread.start()

        # 命令队列
        self.command_queue = queue.Queue()

    def __del__(self):
        if self.thread:
            self.thread.join(timeout=5)

    def set_lip_sync_value(self, value: float):
        """设置口型同步值（线程安全）"""
        self.command_queue.put(("lip_sync", value))

    def play_motion(self, group: str, no: int):
        """播放指定动作（线程安全）"""
        self.command_queue.put(("motion", group, no))

    def close(self):
        """关闭窗口"""
        self.command_queue.put(("quit",))
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run_window(self):
        """窗口主循环"""
        # 初始化Pygame和OpenGL
        pygame.init()
        if self.model_version == "v2":
            live2dv2.init()
            live2dv2.setLogEnable(False)
        elif self.model_version == "v3":
            live2dv3.init()
            live2dv3.setLogEnable(False)
        else:
            raise ValueError("Unsupported model version. Use 'v2' or 'v3'.")

        log("INFO", "Live2D", "Live2D Initialized.")

        # 创建无边框透明窗口
        self.screen = pygame.display.set_mode(
            (self.canvas_width, self.canvas_height),
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.NOFRAME,
        )

        log("INFO", "Live2D", "Live2D Windows Created.")

        # 设置窗口位置
        user32 = ctypes.windll.user32
        hwnd = pygame.display.get_wm_info()["window"]
        user32.SetWindowPos(
            hwnd, -1, self.window_pos[0], self.window_pos[1], 0, 0, 0x0001
        )

        log("INFO", "Live2D", "Live2D Windows Settled.")

        # 设置透明背景
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 0.0)

        log("INFO", "Live2D", "Live2D Windows Background Settled.")

        # 加载模型
        if os.path.exists(self.model_path):
            log("WARNING", "Live2D", f"Loading Live2D model from {self.model_path}")
            self.model = Live2DModel(self.model_path, self.canvas_width, self.canvas_height, self.model_version)
        else:
            log("ERROR", "Live2D", f"Model file not found: {self.model_path}")
            return

        # 窗口拖动状态
        dragging = False
        last_mouse_pos = (0, 0)

        clock = pygame.time.Clock()

        log("INFO", "Live2D", "Live2D display Started.")

        while self.running:
            delta_time = clock.tick(60) / 1000.0

            # 处理命令队列
            while not self.command_queue.empty():
                command, *args = self.command_queue.get()
                if command == "lip_sync":
                    self.lip_sync_value = args[0]
                elif command == "motion":
                    self.model.play_motion(args[0], args[1])
                elif command == "quit":
                    self.running = False

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    current_pos = pygame.mouse.get_pos()
                    dx = current_pos[0] - last_mouse_pos[0]
                    dy = current_pos[1] - last_mouse_pos[1]
                    x, y = self.screen.get_window_position()
                    self.screen.set_window_position(x + dx, y + dy)
                    last_mouse_pos = current_pos

            # 更新模型口型
            self.model.set_lip_sync_value(self.lip_sync_value)
            self.model.update(delta_time)

            # 渲染
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.model.draw()
            pygame.display.flip()

        log("INFO", "Live2D", "Live2D display closed.")
        # 清理资源
        if self.model_version == "v2":
            live2dv2.dispose()
        elif self.model_version == "v3":
            live2dv3.dispose()
        else:
            raise ValueError("Unsupported model version. Use 'v2' or 'v3'.")
        pygame.quit()
