import os

import platform
from splinter import Browser
from selenium import webdriver

import config


def add_chrome_webdriver():
	print(platform.system())
	if platform.system() == 'Windows':
		working_path = os.getcwd()
		library = 'library'
		path = os.path.join(working_path, library)
		os.environ["PATH"] += '{}{}{}'.format(os.pathsep, path, os.pathsep)
		print(os.environ['PATH'])


def find_website():
	chrome_options = webdriver.ChromeOptions()
	# 添加用户数据文件目录
	chrome_options.add_argument("--user-data-dir={}".format(config.profile))
	with Browser('chrome', headless=False, options=chrome_options) as browser:
		# Visit URL
		url = "https://www.zhihu.com"
		browser.visit(url)

		# 输入关键词
		browser.find_by_css('.Input').fill('python')
		# 点击搜索
		browser.find_by_css('.Icon--search').click()

		# 模拟执行向下滚动操作
		browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')

		# 获取前50条相关话题
		item_number = browser.evaluate_script('document.querySelectorAll(".AnswerItem").length;')
		while item_number < 50:
			browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
			item_number = browser.evaluate_script('document.querySelectorAll(".AnswerItem").length;')
		print('current item number: {}'.format(item_number))

		# Do something else whatever you want
		page = browser.html

		# 建立缓存文件(夹)
		folder = 'Zhihu'
		filename = 'zhihu-python.html'
		if not os.path.exists(folder):
			os.makedirs(folder)

		path = os.path.join(folder, filename)

		with open(path, 'wb') as f:
			f.write(page.encode())
		print('File has been cached.')

def main():
	add_chrome_webdriver()
	find_website()


if __name__ == '__main__':
	main()
