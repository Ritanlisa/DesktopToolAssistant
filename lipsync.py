#!/usr/bin/env python3
import queue
import threading
from typing import Callable

class LipSyncInterface:
    def __init__(self):
        self.rms_queue = queue.Queue()
        self.callback = None
        self.running = False
        self.thread = None
        self.sensitivity = 3.0  # 口型同步灵敏度系数
    
    def register_callback(self, callback: Callable[[float], None]):
        """注册口型同步回调函数"""
        self.callback = callback
    
    def start(self):
        """启动口型同步处理线程"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_rms)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """停止口型同步处理"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def put_rms(self, rms_value: float):
        """添加新的RMS值到队列"""
        self.rms_queue.put(rms_value)
    
    def _process_rms(self):
        """处理RMS队列中的值并调用回调"""
        while self.running:
            try:
                rms = self.rms_queue.get(timeout=0.1)
                if self.callback:
                    # 应用灵敏度系数并调用回调
                    self.callback(rms * self.sensitivity)
            except queue.Empty:
                continue
    
    def set_sensitivity(self, sensitivity: float):
        """设置口型同步灵敏度"""
        self.sensitivity = max(0.1, min(sensitivity, 10.0))
