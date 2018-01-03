# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask
from flask import render_template
from flask import request
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'KB-python-API')))

from kb.nl.collections import SETS
from kb.nl.api import sru
from kb.nl.api import oai
from kb.nl.helpers import alto_to_text

sources = SETS.keys()
app = Flask(__name__)
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def binnen():
    payload = render_template('home.html', sources=sources)
    return payload

@app.route("/vind")
def vinden():
    print (request)
    source = request.args.get('bron')
    q = request.args.get('q')
    if q and source:
        q = q.split()
        q = (' AND ').join(q)

    q_response = sru.search(q, source)
    oai_handler = oai
    oai_handler.__init__(current_set=source)
    results = []

    for record in q_response.records:
        if not record.identifiers:
            continue
        r = oai_handler.get(record.identifiers[0])
        if r.alto:
            for alto in r.alto:
                if alto:
                    record.fulltext = alto_to_text(alto)
                else:
                    record.fulltext = None
        results.append(record)

    payload = render_template('home.html',
                               sources=sources,
                               response = q_response,
                               results=results)
    return payload
