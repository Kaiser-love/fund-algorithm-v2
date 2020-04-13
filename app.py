# coding: utf-8
import json
import os
import shutil
from PIL import Image
import pytesseract
from flask import Flask
from flask_restplus import Resource, Api, reqparse
from pinyin import pinyin

import ctpnOcr
import tensorflow as tf

import file_page_query
import predict
from similarity import sensim
from web.runnable.ThreadFunc import ThreadFunc

global graph, model
graph = tf.get_default_graph()
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))


def getTextFromImage(img_path):
    # img_path = 'images/1.jpg'
    # 依赖OpenCv
    # img = cv.imread(img_path)
    config = ('-l chi_sim')
    text = pytesseract.image_to_string(Image.open(img_path), config=config)
    # text = pytesseract.image_to_boxes(Image.open(img_path), config=config)
    text = text.replace(" ", "")
    print(text)
    return text


# @api.route('/ocr/<string:img_path>')
@api.route('/api/v1/ocr/tessAct')
class TessActOcr(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('imgPath', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        return {'ocrResult': getTextFromImage(params.get('imgPath'))}


@api.route('/api/v1/ocr/ctpn')
class CtpnOcr(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('imgPath', type=str, location='args')
        self.parser.add_argument('apiType', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        image_file = params.get('imgPath')
        return {'ocrResult': ctpnOcr.ctpnOcr(image_file)}


@api.route('/api/v1/wireShark')
class ScrapyApi(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('apiTypeDesc', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        apiType = params.get('apiType')
        thread = ThreadFunc(apiType)
        thread.start()
        return {
            "code": 1,
            "message": "ok",
            "data": "ok"
        }


# 新建模型
@api.route('/api/v1/newModel')
class NewModel(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('modelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        modelName = params.get('modelName')
        modelPinYinName = pinyin.get(modelName, format='strip')
        shutil.copytree('data/base_data', 'data/' + modelPinYinName)
        return {
            "code": 1,
            "message": "ok",
            "data": modelPinYinName
        }


# 更新模型名
@api.route('/api/v1/updateModel')
class UpdateModel(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('sourceModelName', type=str, location='args')
        self.parser.add_argument('targetModelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        sourceModelPinYinName = pinyin.get(params.get('sourceModelName'), format='strip')
        targetModelPinYinName = pinyin.get(params.get('targetModelName'), format='strip')
        os.rename('data/' + sourceModelPinYinName, 'data/' + targetModelPinYinName)
        if os.path.exists("model/" + sourceModelPinYinName):
            os.rename('model/' + sourceModelPinYinName, 'model/' + targetModelPinYinName)
        return {
            "code": 1,
            "message": "ok",
            "data": targetModelPinYinName
        }


# 添加标注数据
@api.route('/api/v1/addTagData')
class AddTagData(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('tagDatas', type=str, location='args')
        self.parser.add_argument('modelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        tagDatas = params.get('tagDatas')
        modelName = params.get('modelName')
        modelPinYinName = pinyin.get(modelName, format='strip')
        with open("data/" + modelPinYinName + "/train.tsv", 'a+', encoding="utf8") as f:
            for text in json.loads(tagDatas):
                f.write(text + '\n')
        return {
            "code": 1,
            "message": "ok",
            "data": "ok"
        }


# 训练模型
@api.route('/api/v1/trainModel')
class TrainModel(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('modelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        modelName = params.get('modelName')
        modelPinYinName = pinyin.get(modelName, format='strip')
        if os.path.exists("model/" + modelPinYinName):
            shutil.rmtree("model/" + modelPinYinName)
        thread = ThreadFunc('2', modelPinYinName)
        thread.start()
        return {
            "code": 1,
            "message": "ok",
            "data": "ok"
        }


# 删除模型
@api.route('/api/v1/deleteModel')
class DeleteModel(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('modelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        modelName = params.get('modelName')
        modelPinYinName = pinyin.get(modelName, format='strip')
        if os.path.exists("model/" + modelPinYinName):
            shutil.rmtree("model/" + modelPinYinName)
        if os.path.exists("data/" + modelPinYinName):
            shutil.rmtree("data/" + modelPinYinName)
        return {
            "code": 1,
            "message": "ok",
            "data": "ok"
        }


# 根据模型进行预测
@api.route('/api/v1/predictTag')
class PredictTag(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('modelName', type=str, location='args')
        self.parser.add_argument('data', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        modelName = params.get('modelName')
        data = params.get('data')
        # data = [["有保障"],
        #         ["无风险"],
        #         ["基金过往数据并不代表未来趋势"],
        #         ["为什么"],
        #         ["周杰伦"],
        #         ]
        modelPinYinName = pinyin.get(modelName, format='strip')
        if not os.path.exists("model/" + modelPinYinName):
            return {
                "code": 0,
                "message": "model not exist",
                "data": ""
            }
        request_data = json.loads(data)
        predict_result = predict.predict_tag(modelPinYinName, request_data)
        api_result = {}
        for i in range(len(request_data)):
            api_result[request_data[i][0]] = predict_result[i]
        return {
            "code": 1,
            "message": "ok",
            "data": api_result
        }


# 标注数据分页
@api.route('/api/v1/dataPageList')
class DataPageList(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=str, location='args')
        self.parser.add_argument('count', type=str, location='args')
        self.parser.add_argument('modelName', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        file_name = pinyin.get(params.get('modelName'), format='strip')
        data = file_page_query.page_list(file_name,
                                         int(params.get('page')),
                                         int(params.get('count')))
        return {
            "code": 1,
            "message": "ok",
            "data": {
                "data": data,
                "size": file_page_query.count_file_lines(file_name) - 1
            }
        }


# 修改标注数据
@api.route('/api/v1/dataChange')
class DataChange(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str, location='args')
        self.parser.add_argument('modelName', type=str, location='args')
        self.parser.add_argument('data', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        file_page_query.modify_line(pinyin.get(params.get('modelName'), format='strip'),
                                    int(params.get('id')),
                                    params.get('data'))
        return {
            "code": 1,
            "message": "ok",
            "data": "ok"
        }


# 获取中文拼音
@api.route('/api/v1/chinesePinYin')
class ChinesePinYin(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('data', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        return {
            "code": 1,
            "message": "ok",
            "data": pinyin.get(params.get('data'), format='strip')
        }


# 计算文本余弦相似度
@api.route('/api/v1/cosSimilarity')
class CosSimilarity(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('data', type=str, location='args')

    def get(self):
        params = self.parser.parse_args()
        data = params.get('data')
        # data = [
        #     [
        #         "驾驶 违章 一次 扣 12分 用 两个 驾驶证 处理 可以 吗",
        #         " 一次性 扣 12分 的 违章 , 能用 不满 十二分 的 驾驶证 扣分 吗"
        #     ],
        #     ["风险几乎为零", "风险高"],
        #     ["电脑 反应 很 慢 怎么 办", "反应 速度 慢 , 电脑 总是 卡 是 怎么回事"],
        # ]
        return {
            "code": 1,
            "message": "ok",
            "data": sensim.cos_similarity(json.loads(data))
        }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6006)
