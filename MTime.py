# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
import os
import requests
from utiles import escape
from pyquery import PyQuery


class Model():
	def __repr__(self):
		name = self.__class__.__name__
		properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
		s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
		return s


class MTime(Model):
	def __init__(self):
		self.title = ''
		self.score = 0
		self.ranking = 0
		self.quote = ''
		self.cover_url = ''


def get(url, filename, is_img=False):
	"""
	缓存, 避免重复下载网页浪费时间
	"""
	folder = 'MTime'
	# 建立 cached 文件夹
	if not os.path.exists(folder):
		os.makedirs(folder)

	if is_img:
		img_folder = 'img'
		current_path = os.path.dirname(os.path.realpath(__file__))
		folder = os.path.join(current_path, folder, img_folder)
		if not os.path.exists(folder):
			os.makedirs(folder)

	path = os.path.join(folder, filename)
	if os.path.exists(path):
		with open(path, 'rb') as f:
			s = f.read()
			return s
	else:
		# 发送网络请求, 把结果写入到文件夹中
		r = requests.get(url)
		with open(path, 'wb') as f:
			f.write(r.content)
			return r.content


def movie_from_div(tag):
	"""
	从一个 div tag 里面获取到一个电影信息
	"""
	div = PyQuery(tag)

	# 小作用域变量用单字符
	m = MTime()
	m.ranking = div('.number em').text()
	m.cover_url = div('img').attr('src')
	m.score = div('.total').text() + div('.total2').text()
	m.title = div('.mov_con').find('h2').find('a').text()
	m.quote = div('.mt3').text()
	return m


def save_cover(movies):
	for m in movies:
		filename = "{}_{}.jpg".format(m.ranking, escape(m.title))
		get(m.cover_url, filename, is_img=True)


def movies_from_url(url):
	if "index" not in url:
		# http://www.mtime.com/top/movie/top100/
		filename = 'top_1_10.html'
	else:
		# http://www.mtime.com/top/movie/top100/index-2.html
		filename = 'top_{}_{}.html'.format(
			url.split('-', 1)[-1].split('.')[0],
			int(url.split('-', 1)[-1][0]) * 10
		)
	page = get(url, filename)
	elements = PyQuery(page)
	items = elements('.top_list').find("li")
	movies = [movie_from_div(tag) for tag in items]
	save_cover(movies)
	return movies


def main():
	url_1 = "http://www.mtime.com/top/movie/top100/"
	movies_1 = movies_from_url(url_1)
	print('top10 movies from MTime', movies_1)
	for i in range(2, 11):
		url = 'http://www.mtime.com/top/movie/top100/index-{}.html'.format(i)
		movies = movies_from_url(url)
		print('top100 movies from MTime', movies)


if __name__ == '__main__':
	main()
