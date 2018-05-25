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


class Movie(Model):
	def __init__(self):
		self.title = ''
		self.other = ''
		self.score = 0
		self.quote = ''
		self.cover_url = ''
		self.ranking = 0


def get(url, filename, is_img=False):
	"""
	缓存, 避免重复下载网页浪费时间
	"""
	folder = 'Douban'
	# 建立缓存文件夹
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


def movie_from_div(div):
	"""
	从一个 div 里面获取到一个电影信息
	"""
	d = PyQuery(div)
	m = Movie()
	m.title = d('.title').text()
	m.other = d('.other').text()
	m.score = d('.rating_num').text()
	m.quote = d('.inq').text()
	m.cover_url = d('img').attr('src')
	m.ranking = d('.pic').find('em').text()
	return m


def save_cover(movies):
	"""
	下载封面
	"""
	for m in movies:
		filename = "{}_{}.jpg".format(m.ranking, escape(m.title))
		get(m.cover_url, filename, is_img=True)


def movies_from_url(url):
	"""
	从 url 中下载网页并解析出页面内所有的电影
	"""
	# https://movie.douban.com/top250?start=100
	filename = 'top_{}_{}.html'.format(int(url.split('=', 1)[-1]) + 1, int(url.split('=', 1)[-1]) + 25)
	page = get(url, filename)
	e = PyQuery(page)
	items = e('.item')
	# 调用 movie_from_div
	movies = [movie_from_div(i) for i in items]
	save_cover(movies)
	return movies


def main():
	for i in range(0, 250, 25):
		url = 'https://movie.douban.com/top250?start={}'.format(i)
		movies = movies_from_url(url)
		print('top250 movies', movies)


if __name__ == '__main__':
	main()
