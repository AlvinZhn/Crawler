# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
import config

from flask import Flask
from flask_session import Session

from routes.routes_mashup import mashup_view
from routes.api_mashup import mashup_api

from routes.api_crawler import crawler_api


def register_routes(app):
	app.register_blueprint(mashup_view)
	app.register_blueprint(mashup_api)

	app.register_blueprint(crawler_api)


def configured_app():
	app = Flask(__name__)

	register_routes(app)
	# load config from config file
	app.config.from_object(config)
	Session(app)

	return app


if __name__ == '__main__':
	app = configured_app()

	# 自动 reload jinja
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.jinja_env.auto_reload = True
	# 关闭 js 静态缓存
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

	config = dict(
		host='0.0.0.0',
		port=3000,
		debug=True,
	)
	app.run(**config)
