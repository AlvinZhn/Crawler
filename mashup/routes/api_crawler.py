# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
from flask import (
	Blueprint,
	request,
	jsonify,
)

from models.Gongyu import Gongyu

crawler_api = Blueprint('crawler_api', __name__)


def site_model(site):
	site_dict = dict(
		gongyu=Gongyu,
	)
	return site_dict.get(site)


def source_model(source):
	site_dict = dict(
		gongyu=Gongyu,
	)
	if source != 'all':
		return site_dict.get(source)
	else:
		return site_dict


@crawler_api.route('/api/crawler/<string:site>/update')
@crawler_api.route('/api/crawler/<string:site>/<string:source>/update')
def update(site, source=None):
	if site == 'renting' and source is not None:
		new_data = site_model(source).update_data()
		response = dict(
			all=new_data,
			new_data=len(new_data),
			all_data=site_model(source).get_count(),
		)
	else:
		page = int(request.args.get('page'))
		url = site_model(site).get_url(page)
		has_update = site_model(site).check_update(url)
		response = dict(
			has_update=has_update,
			url=url,
			page=page,
		)
	return jsonify(response)


@crawler_api.route('/api/geocoder/crawler/renting/<string:source>')
def get_error_location_info(source):
	m = source_model(source)
	all_info = m.all_json(m.find_all(lng=0))
	return jsonify(all_info)


@crawler_api.route('/api/geocoder/crawler/renting/<string:source>/update', methods=['POST'])
def update_error_geocode(source):
	m = source_model(source)
	id = request.args.get('id')
	lat = float(request.form.get('lat', 0))
	lng = float(request.form.get('lng', 0))
	form = dict(
		lat=lat,
		lng=lng,
	)
	m.update(id=id, form=form)
	response = {'error': ''}
	return jsonify(response)
