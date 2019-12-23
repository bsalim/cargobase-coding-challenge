import requests

from . import search
from app import app, db
from flask import render_template

@search.route('/', methods=['GET'])
def search_index():
    return render_template('index.html', title='')


@search.route('/search/results', methods=['GET'])
def search_result():
    q = request.args.get('q', None)

    if q is not None:
        try:
            search_query = SearchQueries.query.all()[:10]
        except NoResultFound as e:
            search_query = SearchQueries(keyword=q)
            db.session.add(search_query)
            db.session.commit()
    else:
        return redirect('/')

    return render_template('search_result.html',
                           search_query=search_query,
                           title='Search Result for "{}"'.format(q))
