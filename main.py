#!/usr/bin/env python

# Factory Classes
from audio.general import AudioGen
from display.general import Displayer
from LLM.general import TextGen
from speechRecognize.general import SpeechRecog

from memory.AmpliGraph import MemoryManager
from Characteristic.Avatar import Avatar
from lipsync import LipSyncInterface
from log import log, log_file
import time

from config import *

# 1. initialize: Display Live2D model, run subthreads, load memory

# 创建口型同步接口
lip_sync = LipSyncInterface()
lip_sync.start()

# 创建显示组件
displayer = Displayer(lip_sync_interface=lip_sync, **Display_Args)

# ***************************************************************************************************

# 创建语音生成器
voice_gen = AudioGen(lip_sync_interface=lip_sync, **Audio_Args)
# 创建语音识别器
speech_recog = SpeechRecog(**SpeechRecog_Args)
# 创建文本生成器
text_gen = TextGen(**LLM_Full_Args)
text_gen_mini = TextGen(**LLM_Small_Args)
# 创建记忆管理器
memory_manager = MemoryManager(**MM_Args)
memory_manager.load_from_file(Common_Args.get("MemoryFile", "memory/memory_graph"))
# 加载人格
avatar = Avatar(Character)

log("INFO", "System", "Components initialized successfully.")

log("INFO", "System", f"Loaded character: \n\n{avatar.get_summary()}\n")

# # generating Prompts:
# Avatar_prompt = text_gen.generate(
#     messages=[
#         {
#             "role": "system",
#             "content": Prompts.get(
#                 "Avatar_Gen",
#                 "You need to summon a prompt for a virtual character(do not mention this), the information of the character will be provided as follows:",
#             ),
#         },
#         {
#             "role": "user",
#             "content": avatar.get_summary(),
#         }
#     ]
# )

# print(Avatar_prompt)
# exit(0)

# ***************************************************************************************************

# todo: Load character personality

# 2. loop: run main loop
# 2.1. get speech recognition result
# 2.2. check if user needs assistance
# 2.3. process user input(if needed), read screen(if needed), opencv camera(if needed) and generate response
while True:

    pass


def main():
    # 示例对话
    dialogues = [
        "你好，我是虚拟助手，很高兴为你服务。",
        "今天天气真不错，适合出去走走。",
        "有什么我可以帮你的吗？",
    ]

    # 播放对话
    for text in dialogues:
        # 播放说话动作（假设模型中有"Talk"动作）
        displayer.play_motion("Talk", 1)

        # 生成并播放语音
        voice_gen.speak(text)

        # 短暂暂停
        time.sleep(1.0)

    # 关闭所有组件
    lip_sync.stop()
    displayer.close()


if __name__ == "__main__":
    main()
