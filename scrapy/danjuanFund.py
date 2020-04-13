# coding=utf-8
import requests
import json
import time
import random
from pymongo import MongoClient
import re

"""
蛋卷基金-基金排行-概要-公告
"""


class DanJuanFund():
    def __init__(self, db):
        self.headers = {
            "dj-client": "android",
            "Accept-Encoding": "",
            "client_id": "3XmoY2upy",
            "dj-version": "6.31.0",
            "client_secret": "Nh3H6PNpNPiaHhRE",
            "User-Agent": "Fund Android 6.31.0",
            "dj-flavor": "1200109001",
            "Authorization": "OAuth2",
            "Connection": "Keep-Alive",
            "dj-signature": "492720a84b99d91a1c83b5648fcf2e586bcf524f",
            "dj-device-id": "4c027de76e3dcca8964a4a5aec79ec23",
            "dj-timestamp": "1577523712717"
        }
        self.deviceid = "cbc5d43197df826cbfbd4cde1173362f%7C%7C037584220931968"
        self.MobileKey = "cbc5d43197df826cbfbd4cde1173362f%7C%7C037584220931968"
        self.db = db

    def getFundRank(self, page=1):
        url = "https://fund.xueqiu.com/v3/filter/all?order=desc&order_by=1m&page=" + str(page) + "&size=20&type=1003&"
        time.sleep(random.randint(2, 3))
        html = requests.get(url, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        total_count = data_json['data']['total_pages']
        items = data_json['data']['items']
        for d in items:
            dataDict = dict()
            dataDict['fd_code'] = d['fd_code']  # 基金代码
            dataDict['fd_name'] = d['fd_name']  # 基金名称
            print("=========提取基金信息【{fd_name}】============".format(fd_name=d['fd_name']))
            # 获取基金风险等级
            self.getRiskLevel(d['fd_code'], dataDict)
            # 获取基金概览
            self.getGeneral(d['fd_code'], dataDict)
            # 获取基金公告
            self.getNotes(d['fd_code'])
        # 根据总数循环
        if page <= total_count:
            page += 1
            self.getFundRank(page)
        print("=========全部提取基金信息完成============")

    def getRiskLevel(self, fcode, dataDict):
        url = "https://danjuanfunds.com/viewapi/fund?code=" + fcode
        time.sleep(random.randint(2, 3))
        html = requests.get(url, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        src = data_json['data']['src']
        dataDict['type_desc'] = src['type_desc']  # 指数型
        dataDict['risk_desc'] = src['op_fund']['fund_tags'][1]["name"]  # 中高风险
        dataDict['keeper_name'] = src['keeper_name']  # 所属公司

    # 概况
    def getGeneral(self, fcode, dataDict):
        url = "https://fund.xueqiu.com/fund/detail/" + fcode
        time.sleep(random.randint(2, 3))
        html = requests.get(url, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        dataDict['fund_company_desc'] = data_json['data']['fund_company']  # 基金公司描述
        managerList = data_json['data']['manager_list']
        managerDbList = []
        for managerItem in managerList:
            manageDictItem = dict()
            manageDictItem['manage_name'] = managerItem.get('name', "")  # 名字
            manageDictItem['manage_resume'] = managerItem.get('resume', "")  # 简历
            manageDictItem['manage_college'] = managerItem.get('college', "")  # 大学
            manageDictItem['manage_work_year'] = managerItem.get('work_year', "")  # 工作年限
            managerDbList.append(manageDictItem)
        dataDict['manager_list'] = managerDbList
        self.insertItem("contents", dataDict)
        print("=========提取概况============")
        # 插入mongodb
        print(dataDict)

    # 公告
    def getNotes(self, fcode, page=1):
        url = "https://fund.xueqiu.com/fund/discs/" + str(fcode) + "?page=" + str(page) + "&size=10&type=0&"
        time.sleep(random.randint(2, 3))
        html = requests.get(url, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        dataItem = data_json['data']['items']
        total_pages = data_json['data']['total_pages']
        for d in dataItem:
            data_dict = dict()
            data_dict['fd_code'] = d['fd_code']
            data_dict['disc_title'] = d['disc_title']  # 标题
            data_dict['declare_date'] = d['declare_date']  # 时间
            data_dict['disc_type'] = d['disc_type']  # 公告类型
            data_dict['disc_id'] = d['disc_id']  # 公告类型
            # type_id = d['disc_type']
            # if type_id == '1':
            #     data_dict['TYPE'] = "发行运作"
            # elif type_id == '2':
            #     data_dict['TYPE'] = "分红配送"
            # elif type_id == '3':
            #     data_dict['TYPE'] = "定期报告"
            self.getNotesDetail(d['disc_id'], data_dict)
            print("=========提取公告【{disc_title}】============".format(disc_title=d['disc_title']))
            # 插入mongodb
            print(data_dict)
        # 根据总共条数循环
        if page <= total_pages:
            page += 1
            self.getNotes(fcode, page)

    def getNotesDetail(self, id, data_dict):
        url = "https://fund.xueqiu.com/fund/disc/" + id
        time.sleep(random.randint(2, 3))
        html = requests.get(url, headers=self.headers, verify=False)
        data_json = json.loads(html.text)
        data_dict['disc_content'] = data_json['data']['disc_content']
        data_dict['acce_url'] = data_json['data']['acce_url']
        print("=========提取公告【{disc_title}】内容============".format(disc_title=data_json['data']['disc_title']))
        self.insertItem("notes", data_dict)

    def insertItem(self, tableName, data):
        my_set = self.db[tableName]
        my_set.insert_one(data)


def executeDanJuanFundScrapy():
    conn = MongoClient('127.0.0.1', 27017)
    db = conn["danJuanFund"]
    collection_names = db.collection_names()
    for collection_name in collection_names:
        db_collection = db[collection_name]
        db_collection.remove()
    danJuanFund = DanJuanFund(db)
    danJuanFund.getFundRank()
