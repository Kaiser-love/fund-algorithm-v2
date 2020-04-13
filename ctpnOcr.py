# -*- coding:utf-8 -*-
import dlocr
import time


def ctpnOcr(image_file):
    ocrModel = dlocr.get_or_create()
    start = time.time()
    # "asset/1.png"
    bboxes, texts = ocrModel.detect(image_file)
    api_result = ''
    print('\n'.join(texts))
    print(f"cost: {(time.time() - start) * 1000}ms")
    for text in texts:
        api_result += text
    return api_result.replace(" ", "")
