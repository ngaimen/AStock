#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib2
import socket
import re
import time
from aclass import *

ResultSuccess = 0
ResultTimeout = 1
ResultNoChange = 2
ResultUnknown = 3

stockList = []
timePattern = re.compile(r',(\d+:\d+:\d+),')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^,"]+,[^,"]+,[^,"]+,[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,[^"]+";')
lastTime = ''
lastData = []

def loadStockList():
        if len(sys.argv) <= 1:
                stockList.append('sh600987')
                stockList.append('sh600037')
                stockList.append('sz159949')
                stockList.append('sz159901')
                stockList.append('sh510050')
                stockList.append('sh510500')
                stockList.append('sz162411')
                stockList.append('sz159920')
                stockList.append('sh518880')
                stockList.append('sh513100')
                stockList.append('sh512660')
                stockList.append('sz159938')
                stockList.append('sh513050')
                return True

	for index in range(1, len(sys.argv)):
		stockNumber = sys.argv[index]
		if len(stockNumber) == 8:
			# 8位长度的代码必须以sh或者sz开头，后面6位是数字
			if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
				stockList.append(stockNumber)
		elif len(stockNumber) == 6:
			# 6位长度的代码必须全是数字
			if stockNumber.decode().isdigit():
				# 0开头自动补sz，6开头补sh，3开头补sz，否则无效
				if stockNumber.startswith('0') or stockNumber.startswith('15') or stockNumber.startswith('16') or stockNumber.startswith('3'):
					stockList.append('sz' + stockNumber)
				elif stockNumber.startswith('6') or stockNumber.startswith('51'):
					stockList.append('sh' + stockNumber)
		elif stockNumber == 'sh':
			stockList.append('sh000001')
		elif stockNumber == 'sz':
			stockList.append('sz399001')
		elif stockNumber == 'zx':
			stockList.append('sz399005')
		elif stockNumber == 'cy':
			stockList.append('sz399006')
		elif stockNumber == '300':
			stockList.append('sh000300')
	if len(stockList) == 0:
		return False
	return True

def requestStockData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return ResultTimeout
	except socket.timeout:
		return ResultTimeout
	# 判断数据时间有没有更新
	global lastTime
	match = timePattern.search(content)
	if match == None:
		return ResultUnknown
	elif match.group(1) == lastTime:
		return ResultNoChange
	lastTime = match.group(1)
	# 抓取所有数据并计算
	lastData[:] = []
	match = stockPattern.search(content)
	while match:
		stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))
		stock.calcBuyPercent([match.group(7), match.group(8), match.group(9), match.group(10), match.group(11), match.group(12), match.group(13), match.group(14), match.group(15), match.group(16)])
		lastData.append(stock)
		match = stockPattern.search(content, match.end())
	if len(lastData) == 0:
		return ResultUnknown
	return ResultSuccess

if loadStockList() == False:
	print('没有有效的股票代码')
else:
	while True:
		result = requestStockData()
		if result == ResultSuccess:
			print(lastTime)
                        lastData.sort(key=lambda Stock: Stock.increase, reverse=True)
			for stock in lastData:
				stock.printStockData()
			time.sleep(60)
		elif result == ResultTimeout:
			print('超时重试')
			time.sleep(5)
		elif result == ResultNoChange:
			timeValue = int(lastTime.replace(':', '')[0:4])
			if timeValue > 1130 and timeValue < 1255:
				time.sleep(180)
			elif timeValue < 925:
				time.sleep(180)
			elif timeValue > 1500:
				print('已经休市')
				break
			else:
				time.sleep(30)
		else:
			print('未知错误')
			break
