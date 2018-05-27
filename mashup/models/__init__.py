# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""

import time

from bson import ObjectId
from pymongo import MongoClient, ReturnDocument, ASCENDING


class Model(object):
	# init mongodDb
	db = MongoClient()['mashup']
	db['Gongyu'].create_index([("url", ASCENDING)], unique=True)

	@classmethod
	def default_names(cls):
		names = [
			# (字段名, 类型, 默认值)
			('deleted', bool, False),
			('created_time', int, 0),
			('updated_time', int, 0),
		]
		return names

	@staticmethod
	def formatted_time(unix_time, time_format=None):
		if time_format is None:
			time_format = '%Y-%m-%d %H:%M:%S'
		return time.strftime(time_format, time.localtime(unix_time))

	def save(self):
		# 获取对象所属类的名字
		name = self.__class__.__name__
		result = self.db[name].insert_one(self.__dict__)
		_id = result.inserted_id
		self.id = str(_id)

	# 在对应子类下传入表单中的数据新建实例
	@classmethod
	def new(cls, form):
		# 创建所在类的空对象
		m = cls()
		for name in cls.default_names():
			k, t, v = name
			if k in form:
				# 将表单数据强制类型转换，写入db中对应的字段名下
				setattr(m, k, t(form[k]))
			else:
				setattr(m, k, v)
		# 写入默认参数
		timestamp = cls.formatted_time(int(time.time()))
		m.created_time = timestamp
		m.updated_time = timestamp
		m.deleted = False
		m.save()
		return m

	@classmethod
	def update(cls, id=None, query=None, form=None, **kwargs):
		if form is None:
			form = {}
		name = cls.__name__
		if id is not None:
			query = {
				'_id': ObjectId(id),
			}
		if cls.__name__ != 'Crawler':
			form['updated_time'] = cls.formatted_time(int(time.time()))
		else:
			form['last_checked_time'] = cls.formatted_time(int(time.time()))
		values = {
			'$set': form
		}
		values.update(kwargs)
		m = cls.db[name].find_one_and_update(query, values, return_document=ReturnDocument.AFTER)
		# cls.db[name].update_one(query, values)
		return m

	# 内部函数，用于将 mongo 数据重构为 model
	@classmethod
	def _new_from_bson(cls, bson, compress=None):
		m = cls()
		class_name = cls.__name__
		for key in bson:
			# 过滤 delete 字段
			if key != 'deleted':
				# 对 Message 的 content 字段进行压缩
				if key == 'content' and class_name == 'Message':
					if compress:
						setattr(m, key, bson[key][:compress])
					else:
						setattr(m, key, bson[key])
				elif key == 'sender' and class_name == 'Message' and bson[key] == 'admin':
					setattr(m, key, '系统消息')
				# 过滤 Message 中 deleted_user 字段
				elif key != 'deleted_user':
					setattr(m, key, bson[key])
		setattr(m, 'id', str(bson['_id']))
		return m

	@classmethod
	def _find_and_sort(cls, limit=None, sort=None, **kwargs):
		name = cls.__name__
		compress = None
		kwargs['deleted'] = False
		if 'id' in kwargs:
			if type(kwargs['id']) == str:
				kwargs['_id'] = ObjectId(kwargs['id'])
			elif type(kwargs['id']) == dict:
				query = kwargs['id']
				kwargs['_id'] = {key: ObjectId(query[key]) for key in query}
			kwargs.pop('id')
		if 'user_id' in kwargs:
			kwargs['user_id'] = str(kwargs['user_id'])
		if 'compress' in kwargs:
			compress = kwargs['compress']
			kwargs.pop('compress')
		# limit: type -> int
		if limit is not None:
			all_data = cls.db[name].find(kwargs).limit(limit)
		else:
			all_data = cls.db[name].find(kwargs)
		# sort: type -> list of tuple
		if sort is not None:
			all_data = all_data.sort(sort)
		l = [cls._new_from_bson(data, compress) for data in all_data]
		return l

	@classmethod
	def find_all(cls, **kwargs):
		return cls._find_and_sort(**kwargs)

	def json(self):
		"""
		返回当前 model 的字典表示
		"""
		datas = self.__dict__
		datas.pop('_id')
		if 'deleted' in datas:
			datas.pop('deleted')
		return datas

	@classmethod
	def all_json(cls, data_list, user=None):
		# 要转换为 dict 格式才行
		if cls.__name__ == 'DiscussReply':
			jsons = []
			for data in data_list:
				data = data.json()
				if (user in data['liked_user']):
					data['is_liked'] = True
				data.pop('liked_user')
				jsons.append(data)
		else:
			jsons = [data.json() for data in data_list]
		return jsons

	@classmethod
	def get_count(cls, **kwargs):
		name = cls.__name__
		number = cls.db[name].find(kwargs).count()
		return number

	# 赋予实例可以调用的特性，
	def __repr__(self):
		class_name = self.__class__.__name__
		properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
		s = '\n'.join(properties)
		return '< {}\n{} >\n'.format(class_name, s)
