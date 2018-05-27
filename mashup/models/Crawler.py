# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
import os

import requests
import time

from models import Model


class Crawler(Model):
	"""
	用于格式化爬虫输出信息
	"""

	@classmethod
	def default_names(cls):
		names = super().default_names()
		names = names + [
			('site', str, cls.__name__),
			('last_checked_time', str, Crawler.formatted_time(int(time.time()))),
		]
		return names

	@staticmethod
	def escape(s):
		"""
		Escape special characters.
		\ / : * ? " < > | ”
		"""
		for old, new in [("\\", "_"), ("/", "_"), (":", "_"), ("?", "_"),
						 ("*", "_"), ("\"", "_"), ("<", "("), (">", ")"),
						 ("|", "_"), ("“", "'"), ("”", "'"), (" ", "_")]:
			s = s.replace(old, new)
		return s

	@staticmethod
	def now():
		return Crawler.formatted_time(time.time())

	@classmethod
	def load_from_url(cls, url, cached=True, filename="", folder_name=None, headers=None):
		"""
		默认将传入的 url 缓存至 folder 文件夹
		"""
		if folder_name is None:
			folder_name = cls.__name__
		if cached:
			# 文件(夹)名称合法性校验/修正
			current_path = os.path.dirname(os.path.realpath(__file__))
			folder = os.path.join(current_path, "Cache", Crawler.escape(folder_name))
			filename = Crawler.escape(filename)

			# 建立缓存文件夹
			if not os.path.exists(folder):
				os.makedirs(folder)

			# 根据文件名生成文件路径
			path = os.path.join(folder, filename)
			# 检查路径是否存在
			if os.path.exists(path):
				with open(path, 'rb') as f:
					page = f.read()
					return page
			else:
				response = requests.get(url, headers=headers)
				with open(path, 'wb') as f:
					page = response.content
					f.write(page)
					return page
		else:
			response = requests.get(url, headers=headers)
			temp_page = response.content
			return temp_page

	def __repr__(self):
		name = self.__class__.__name__
		properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
		s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
		return s
