import threading

import fine_tuning
from web.scrapy.ScrapySwitch import switch, default


class ThreadFunc(threading.Thread):
    def __init__(self, type, modelPinYinName=None):
        threading.Thread.__init__(self)
        self.type = type
        self.modelPinYinName = modelPinYinName

    def run(self):
        print("开始线程：" + self.type)
        if self.type == '2':
            print("开始训练模型")
            fine_tuning.train_model(self.modelPinYinName)
        else:
            switch.get(self.type + '', default)()
        print("退出线程：" + self.type)
