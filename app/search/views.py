import requests

from . import search
from app import app, db, celery_client
from flask import render_template
from app.crawler import GoogleCrawler
from sqlalchemy.exc import SQLAlchemyError

@search.route('/', methods=['GET'])
def search_index():
    return render_template('index.html', title='')

@celery_client.task()
def add_together(a, b):
    return a + b

@search.route('/celery', methods=['GET'])
def search_celery():
    result = add_together.delay(23, 42)

    res = result.wait()
    print(res)
    return 'hello'


@celery_client.task(bind=True, max_retries=5)
def _scrape_google(keyword):
    try:
        google = GoogleCrawler()
        res = google.scrape(keyword)
    except SQLAlchemyError:
        self.retry(exc=exc, countdown=3)  # the task goes back to the queue


@celery_client.task()
def _scrape_wiki(keyword):
    wiki = WikipediaCrawler()
    res = wiki.scrape(keyword)


@search.route('/test-scraping')
def search_celery_scraping():
    res = _scrape_google.delay('ninja')
    res = _scrape_wiki.delay('ninja')
    print(res)

    return 'nothing'


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
