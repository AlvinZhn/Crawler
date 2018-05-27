# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""
from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
)

mashup_view = Blueprint('mashup_view', __name__)


@mashup_view.route('/')
@mashup_view.route('/mashup/<string:path>')
def index(path='renting'):
    path_list = ['renting']
    if path not in path_list:
        return redirect(url_for('.index'))
    return render_template('map.html')
