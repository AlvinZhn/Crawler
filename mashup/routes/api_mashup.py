# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
from flask import (
    Blueprint,
    jsonify,
    request)

from models.Gongyu import Gongyu

mashup_api = Blueprint('mashup_api', __name__)


def source_model(source):
    site_dict = dict(
        gongyu=Gongyu,
    )
    if source != 'all':
        return site_dict.get(source)
    else:
        return site_dict


@mashup_api.route('/api/mashup/<string:site>/<string:source>', methods=['POST'])
def info(site, source):
    form = request.json
    response = {}
    lngMax = form.get('lngMax')
    lngMin = form.get('lngMin')
    latMax = form.get('latMax')
    latMin = form.get('latMin')
    query = {
        'lat': {'$lte': latMax, '$gte': latMin},
        'lng': {'$lte': lngMax, '$gte': lngMin}
    }
    m = source_model('all')
    for k in m:
        response[k] = m[k].all_json(m[k].find_all(**query))
    return jsonify(response)
    # data = []
    # if site == 'renting':
    #     m = source_model(source)
    #     if source != 'all':
    #         data += m.all_json(m.find_all())
    #     else:
    #         for k in m:
    #             data += m[k].all_json(m[k].find_all())
    # return jsonify(data)
