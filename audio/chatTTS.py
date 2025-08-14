#!/usr/bin/env python3
import numpy as np
import pyaudio
import threading
import queue
from typing import Literal, Optional
import ChatTTS
from ChatTTS.utils.io import FileLike
import torch
from .general import AudioGenType
from lipsync import LipSyncInterface

@AudioGenType("ChatTTS")
class ChatTTS_VoiceGen:
    def __init__(self,
                 lip_sync_interface: LipSyncInterface,
                 type: Literal["chatTTS", "ChatTTS"] = "ChatTTS",
                 audio_seed: int = 300,
                 temperature: float = 0.3,
                 top_P: float = 0.7,
                 top_K: int = 40,
                 source: Literal["huggingface", "local", "custom"] = "local",
                 force_redownload: bool = False,
                 compile: bool = True,
                 custom_path: Optional[FileLike] = None, # type: ignore
                 device: Optional[torch.device] = None,
                 coef: Optional[torch.Tensor] = None,
                 use_flash_attn: bool = False,
                 use_vllm: bool = False,
                 experimental: bool = False,
                 **kwargs):
        
        self.chat = ChatTTS.Chat()
        self.chat.load(source=source, force_redownload=force_redownload, compile=compile, custom_path=custom_path, device=device, coef=coef, use_flash_attn=use_flash_attn, use_vllm=use_vllm, experimental=experimental, **kwargs)
        self.lip_sync_interface = lip_sync_interface
        self.temperature = temperature
        self.top_P = top_P
        self.top_K = top_K
        self.audio_seed = audio_seed

    def speak(self, text: str):
        """生成并播放语音，同时计算实时RMS值"""
        # 创建音频队列
        audio_queue = queue.Queue()
        
        # 启动播放线程
        playback_thread = threading.Thread(target=self._audio_playback_thread, args=(audio_queue,))
        playback_thread.daemon = True
        playback_thread.start()
        
        # 生成参数
        params_infer_code = ChatTTS.Chat.InferCodeParams(
            spk_emb=text,
            temperature=self.temperature,
            top_P=self.top_P,
            top_K=self.top_K,
            manual_seed=self.audio_seed,
        )
        
        params_refine_text = ChatTTS.Chat.RefineTextParams(
            prompt="[oral_2][laugh_0][break_6]"
        )
        
        # 生成音频流
        print("[ChatTTS] 开始生成音频...")
        generator = self.chat.infer(
            text,
            stream=True,
            params_infer_code=params_infer_code,
            params_refine_text=params_refine_text
        )
        
        # 处理音频流
        for chunk in generator:
            if isinstance(chunk, tuple) and len(chunk) >= 2:
                status, data = chunk[:2]
                
                if status == 'wav' and isinstance(data, np.ndarray):
                    # 确保数据类型正确
                    if data.dtype != np.float32:
                        data = data.astype(np.float32)
                    
                    # 计算RMS值并发送到口型同步接口
                    if self.lip_sync_interface:
                        rms = self._calculate_rms(data)
                        self.lip_sync_interface.put_rms(rms)
                    
                    # 添加到音频队列
                    audio_queue.put(data)
        
        # 发送结束信号
        audio_queue.put(None)
        playback_thread.join()
        print("[ChatTTS] 音频播放结束")
    
    def _audio_playback_thread(self, audio_queue: queue.Queue):
        """音频播放线程"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=24000,
            output=True,
            frames_per_buffer=2048
        )
        
        while True:
            audio_chunk = audio_queue.get()
            if audio_chunk is None:  # 结束信号
                break
            stream.write(audio_chunk.tobytes())
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def _calculate_rms(self, audio_data: np.ndarray) -> float:
        """计算音频片段的RMS值"""
        # 使用均方根公式计算音量
        return np.sqrt(np.mean(np.square(audio_data)))
