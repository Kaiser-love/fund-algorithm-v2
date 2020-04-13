from scrapy.danjuanFund import executeDanJuanFundScrapy
from scrapy.tiantian import executeTianTianFundScrapy


def callTianTianFundScrapy():
    print("开始抓取天天基金数据")
    executeTianTianFundScrapy()


def callDuanJuanFundScrapy():
    print("开始抓取蛋卷基金数据")
    executeDanJuanFundScrapy()


def default():
    print('No such case')


switch = {'0': callTianTianFundScrapy,
          '1': executeDanJuanFundScrapy,
          }
