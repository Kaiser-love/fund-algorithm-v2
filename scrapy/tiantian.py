# coding=utf-8
import requests
import json
import time
import random
from pymongo import MongoClient
import re

"""
天天基金-基金排行-概要-公告
"""


class TianTian():
    def __init__(self, db):
        self.headers = {
            "User-Agent": "okhttp/3.12.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.deviceid = "cbc5d43197df826cbfbd4cde1173362f%7C%7C037584220931968"
        self.MobileKey = "cbc5d43197df826cbfbd4cde1173362f%7C%7C037584220931968"
        self.db = db

    # 基金排名
    def get_contents(self, page=0):
        postData = {
            "RISKLEVEL": "",
            "ISABNORMAL": "false",
            "RLEVEL_ZS": "",
            "ESTABDATE": "",
            "pageSize": "30",
            "pageIndex": page,
            "DISCOUNT": "",
            "plat": "Android",
            "deviceid": self.deviceid,
            "BUY": "true",
            "appType": "ttjj",
            "MobileKey": self.MobileKey,
            "SortColumn": "SYL_Y",
            "version": "6.1.7",
            "CompanyId": "",
            # "gToken":"ceaf-5b157e504693b6b2477d18b1c0c6537a",
            "TOPICAL": "",
            "Sort": "desc",
            "FundType": "0",
            "product": "EFund",
            "ENDNAV": ""
        }
        url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNRankNewList"
        time.sleep(random.randint(2, 3))
        html = self.get_quests(url, postData)
        data_json = json.loads(html.text)
        total_count = data_json['TotalCount']
        page_no = (total_count // 30) + (total_count % 30)
        for d in data_json['Datas']:
            data_dict = dict()
            data_dict['FCODE'] = d['FCODE']  # 基金代码
            data_dict['SHORTNAME'] = d['SHORTNAME']  # 基金名称
            print("=========提取基金信息【{SHORTNAME}】============".format(SHORTNAME=d['SHORTNAME']))
            self.get_general(d['FCODE'], data_dict)
            self.get_notes(d['FCODE'])
        # 根据总数循环
        if page <= page_no:
            page += 1
            self.get_comments(page)
        print("=========全部提取基金信息完成============")

    # 概况
    def get_general(self, fcode, data_dict):
        postData = {
            "OSVersion": "5.0.2",
            "FCODE": fcode,
            "MobileKey": self.MobileKey,
            "version": "6.1.5",
            "AppVersion": "6.1.7",
            "passportid": "",
            "plat": "Android",
            "deviceid": self.deviceid,
            "product": "EFund"
        }
        url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNDetailInformation"
        time.sleep(random.randint(2, 3))
        html = requests.get(url, params=postData, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        data_dict['ESTABDATE'] = data_json['Datas']['ESTABDATE']  # 成立时间
        data_dict['BENCH'] = data_json['Datas']['BENCH']  # 业绩比较标准
        data_dict['INVTGT'] = data_json['Datas']['INVTGT']  # 投资目标
        data_dict['INVSTRA'] = data_json['Datas']['INVSTRA']  # 投资策略
        num = 1
        flag = 0
        for s in data_dict['INVSTRA'].split():
            # data_dict['INVSTRA_' + str(num)] = ""
            # flag = re.match("\d", s)
            if re.match("\d", s) is not None:
                flag += 1
            if flag >= 2:
                flag = 1
                num += 1
            if flag > 0 and flag <= 1:
                if data_dict.get('INVSTRA_' + str(num)) is None:
                    data_dict['INVSTRA_' + str(num)] = s
                else:
                    data_dict['INVSTRA_' + str(num)] += "  " + s

        self.insertItem("contents", data_dict)
        print("=========提取概况============")

    # 公告
    def get_notes(self, fcode, page=1):
        postData = {
            "FCODE": fcode,
            "NEWCATEGORY": "0",
            "cToken": "kd8kheua6cr6-jdaked8eck8cn6re8dc",
            "userId": "uid",
            "serverVersion": "6.1.5",
            "pageIndex": page,
            "plat": "Android",
            "deviceid": self.deviceid,
            "OSVersion": "5.0.2",
            "appVersion": "6.1.7",
            "MobileKey": self.MobileKey,
            "version": "6.1.7",
            "passportid": "1234567890",
            "uToken": "utoken",
            "pagesize": "10",
            "product": "EFund"
        }
        url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNNoticeList"
        time.sleep(random.randint(2, 3))
        html = requests.get(url, params=postData, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        total_count = data_json['TotalCount']
        page_no = (total_count // 30) + (total_count % 30)
        for d in data_json['Datas']:
            data_dict = dict()
            data_dict['ID'] = d['ID']
            data_dict['FCODE'] = fcode
            data_dict['TITLE'] = d['TITLE']  # 标题
            data_dict['PUBLISHDATE'] = d['PUBLISHDATE']  # 时间
            type_id = d['NEWCATEGORY']
            if type_id == '1':
                data_dict['TYPE'] = "发行运作"
            elif type_id == '2':
                data_dict['TYPE'] = "分红配送"
            elif type_id == '3':
                data_dict['TYPE'] = "定期报告"
            elif type_id == '4':
                data_dict['TYPE'] = "人事调整"
            elif type_id == '5':
                data_dict['TYPE'] = "基金销售"
            elif type_id == '6':
                data_dict['TYPE'] = "其他公告"
            self.get_notes_detail(fcode, d['ID'], data_dict)
            print("=========提取公告【{TITLE}】============".format(TITLE=d['TITLE']))
        # 根据总共条数循环
        if page <= page_no:
            page += 1
            self.get_notes(fcode, page)

    def get_notes_detail(self, fcode, id, data_dict):
        postData = {
            "deviceid": "app_danganye_f10",
            "version": "V2.1.0",
            "product": "EFund",
            "plat": "Iphone",
            "FCODE": fcode,  # "161127",
            "ID": id,  # "AN201912051371600824",
            "_": "1575611613928",
            "callback": "Zepto1575611611615"
        }
        url = "https://fundmobapi.eastmoney.com/FundMApi/FundNoticeDetail.ashx"
        time.sleep(random.randint(2, 3))
        html = requests.get(url, params=postData, headers=self.headers, verify=False)
        data_json = json.loads(html.text.replace("Zepto1575611611615", "").replace("(", "").replace(")", ""))
        data_dict['CONTEXT'] = data_json['Datas']['CONTEXT']
        print("=========提取公告【{TITLE}】内容============".format(TITLE=data_json['Datas']['TITLE']))
        self.insertItem("notes", data_dict)

    def get_quests(self, url, postData):
        try:
            html = requests.post(url, data=postData, headers=self.headers, verify=False)
        except Exception as ex:
            print("-------------访问错误------------")
            print(ex)
            return self.get_quests(url, postData)
        else:
            if html.status_code != 200:
                return self.get_quests(url, postData)
        return html

    def insertItem(self, tableName, data):
        my_set = self.db[tableName]
        my_set.insert_one(data)


def executeTianTianFundScrapy():
    conn = MongoClient('127.0.0.1', 27017)
    db = conn["tiantianFund"]
    collection_names = db.collection_names()
    for collection_name in collection_names:
        db_collection = db[collection_name]
        db_collection.remove()
    tiantian = TianTian(db)
    tiantian.get_contents()
