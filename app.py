# -*- coding: utf-8 -*-
import logging

import jinja2
from flask import Flask
from flask import render_template
from flask import request
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', '../KB-python-API')))

from kb.nl.collections import SETS
from kb.nl.api import sru
from kb.nl.api import oai
from kb.nl.helpers import alto_to_text

sources = SETS.keys()
app = Flask(__name__)
if app.debug:
     app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def binnen():
    payload = render_template('home.html', sources=sorted(sources), selected = '')
    return payload

@app.route("/vind")
def vinden():
    source = request.args.get('bron')
    q = request.args.get('q')
    if q and source:
        q = q.split()
        q = (' AND ').join(q)
    if SETS[source].get('extra_query'):
        q = '%s AND %s' % (q, SETS[source]['extra_query'])

    q_response = sru.search(q, source)

    if q_response:
        oai_handler = oai
        oai_handler.__init__(current_set=source)
        results = []
        i = 0

        for record in q_response.records:
            if not record.identifiers:
                continue
            else:
                print(record.identifiers)
            result = {}
            if source == 'BYVANCK':
               result['fulltext'] = '<img src="%s" class="resultthumbnail" />' % record.identifiers[0]

            i += 1
            if i < 10:
                #print ('OAI: %s' % record.identifiers[0])
                r = oai_handler.get(record.identifiers[0])
                if r.alto:
                    for alto in r.alto:
                        if alto:
                            result['fulltext'] = alto_to_text(alto)
                        else:
                            result['fulltext'] = None

            result['dates'] = ' '.join(str(el) for el in record.dates)
            result['identifiers'] = '{}'.format( '|'.join(str(el) for el in record.identifiers if el.startswith('http') ))
            result['abstracts'] = ' '.join(str(el) for el in record.abstracts)
            result['titles'] = ' '.join(str(el) for el in record.titles)
            results.append(result)

        payload = render_template('home.html',
                                   sources = sorted(sources),
                                   response = q_response,
                                   results = results,
                                   selected = source,
                                   q = request.args.get('q'))
    else:
        payload = render_template('home.html', sources=sorted(sources), selected = source, q = request.args.get('q'))

    return payload

if __name__ == '__main__':
    app.run(port=5004)