import os
import queue
import threading
import time
from typing import Literal
import wave
import json
import numpy as np
import whisper
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import audioSegmentation as aS
import pyaudio
from .general import SpeechRecogType

class VoiceRecognitionSystem:
    def __init__(self, model_size="base", silence_threshold=-40, min_silence_duration=0.5, sample_rate=16000):
        # 初始化参数
        self.silence_threshold = silence_threshold
        self.min_silence_duration = min_silence_duration
        self.sample_rate = sample_rate
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        
        # 初始化队列
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # 加载模型
        self.whisper_model = whisper.load_model(model_size)
        
        # 说话人数据库
        self.speaker_db_file = "speaker_db.json"
        self.speaker_db = self.load_speaker_db()
        self.next_speaker_id = max(self.speaker_db.keys(), default=0) + 1
        
        # 线程控制
        self.is_running = False
        self.processing_thread = None
        self.recording_thread = None
        
        # 音频缓冲区
        self.audio_buffer = np.array([], dtype=np.int16)
        self.silence_counter = 0
        self.last_active_time = time.time()

    def load_speaker_db(self):
        """加载说话人数据库"""
        if os.path.exists(self.speaker_db_file):
            with open(self.speaker_db_file, 'r') as f:
                return {int(k): v for k, v in json.load(f).items()}
        return {}

    def save_speaker_db(self):
        """保存说话人数据库"""
        with open(self.speaker_db_file, 'w') as f:
            json.dump(self.speaker_db, f)

    def extract_voice_features(self, audio_data):
        """提取声音特征（简化版，实际应用中应使用更复杂的声纹特征）"""
        with wave.open('temp.wav', 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # 使用pyAudioAnalysis提取基本特征
        [fs, x] = aIO.read_audio_file('temp.wav')
        f, f_names = aS.mid_feature_extraction(x, fs, 1, 1)
        return np.mean(f, axis=1)

    def identify_speaker(self, audio_segment):
        """识别说话人并返回ID"""
        features = self.extract_voice_features(audio_segment)
        
        # 如果没有注册的说话人，创建新ID
        if not self.speaker_db:
            speaker_id = self.next_speaker_id
            self.speaker_db[speaker_id] = features.tolist()
            self.next_speaker_id += 1
            self.save_speaker_db()
            return speaker_id
        
        # 计算与已注册说话人的相似度
        best_match_id = None
        best_similarity = -np.inf
        
        for speaker_id, db_features in self.speaker_db.items():
            similarity = np.dot(features, np.array(db_features))
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = speaker_id
        
        # 设置相似度阈值，低于阈值则视为新说话人
        if best_similarity < 0.7:  # 调整此阈值
            best_match_id = self.next_speaker_id
            self.speaker_db[best_match_id] = features.tolist()
            self.next_speaker_id += 1
            self.save_speaker_db()
        
        return best_match_id

    def recording_worker(self):
        """录音线程，持续从麦克风捕获音频"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.audio_format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
        
        print("Recording started...")
        while self.is_running:
            # 读取音频数据
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.int16)
            
            # 检测当前块是否为静音
            rms = np.sqrt(np.mean(audio_chunk**2))
            db = 20 * np.log10(rms) if rms > 0 else -100
            
            if db < self.silence_threshold:
                self.silence_counter += self.chunk_size / self.sample_rate
            else:
                self.silence_counter = 0
                self.last_active_time = time.time()
            
            # 添加到缓冲区
            self.audio_buffer = np.append(self.audio_buffer, audio_chunk)
            
            # 检测到静音时间超过阈值，分割音频
            if self.silence_counter >= self.min_silence_duration and len(self.audio_buffer) > 0:
                # 保留静音前的1秒音频用于平滑
                keep_samples = int(1 * self.sample_rate)
                if len(self.audio_buffer) > keep_samples:
                    segment = self.audio_buffer[:-keep_samples]
                    self.audio_buffer = self.audio_buffer[-keep_samples:]
                else:
                    segment = self.audio_buffer.copy()
                    self.audio_buffer = np.array([], dtype=np.int16)
                
                # 将音频段放入队列
                if len(segment) > 0:
                    self.audio_queue.put(segment)
                
                self.silence_counter = 0
        
        # 清理
        stream.stop_stream()
        stream.close()
        p.terminate()

    def processing_worker(self):
        """处理线程，从队列中取出音频进行识别"""
        while self.is_running or not self.audio_queue.empty():
            try:
                # 从队列获取音频段
                audio_segment = self.audio_queue.get(timeout=1.0)
                
                # 识别说话人
                speaker_id = self.identify_speaker(audio_segment)
                
                # 使用Whisper进行语音识别
                audio = audio_segment.astype(np.float32) / 32768.0
                result = self.whisper_model.transcribe(audio, language="zh")
                text = result["text"].strip()
                
                if text:
                    # 将结果放入输出队列
                    self.result_queue.put({
                        "text": text,
                        "speaker_id": speaker_id,
                        "timestamp": time.time()
                    })
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")

    def start(self):
        """启动语音识别系统"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动录音线程
        self.recording_thread = threading.Thread(target=self.recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # 启动处理线程
        self.processing_thread = threading.Thread(target=self.processing_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        print("Voice recognition system started")

    def stop(self):
        """停止语音识别系统"""
        self.is_running = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        
        # 处理缓冲区中剩余的音频
        if len(self.audio_buffer) > int(0.5 * self.sample_rate):
            speaker_id = self.identify_speaker(self.audio_buffer)
            audio = self.audio_buffer.astype(np.float32) / 32768.0
            result = self.whisper_model.transcribe(audio, language="zh")
            text = result["text"].strip()
            
            if text:
                self.result_queue.put({
                    "text": text,
                    "speaker_id": speaker_id,
                    "timestamp": time.time()
                })
        
        print("Voice recognition system stopped")

    def get_results(self):
        """从结果队列获取识别结果"""
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results

@SpeechRecogType("wisper")
class wisper_VoiceRec:
    def __init__(self, type: Literal["wisper"] = "wisper", model_size: str = "base", silence_threshold: int = -40, min_silence_duration: float = 0.5, sample_rate: int = 16000, **kwargs):
        # 初始化Whisper模型
        self.whisper_model = VoiceRecognitionSystem(
            model_size=model_size,
            silence_threshold=silence_threshold,  # 静音阈值 (dB)
            min_silence_duration=min_silence_duration,  # 最小静音持续时间 (秒)
            sample_rate=sample_rate  # 采样率 (Hz)
        )
        self.whisper_model.start()

    def transcribe(self):
        # 使用Whisper进行转录
        result = self.whisper_model.get_results()
        return result

# 使用示例
if __name__ == "__main__":
    # 初始化语音识别系统
    recognizer = VoiceRecognitionSystem(
        model_size="base",
        silence_threshold=-40,  # 静音阈值 (dB)
        min_silence_duration=0.5  # 最小静音持续时间 (秒)
    )
    
    # 启动系统
    recognizer.start()
    
    try:
        # 主循环 - 在实际应用中，这里可以是你程序的主逻辑
        while True:
            # 获取并处理识别结果
            results = recognizer.get_results()
            for result in results:
                print(f"Speaker {result['speaker_id']}: {result['text']}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        # 用户按下Ctrl+C时停止
        recognizer.stop()
        print("Program stopped by user")