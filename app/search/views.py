import requests
import redis
import os
from . import search
from app import app, db
from flask import render_template, request, redirect, jsonify, render_template_string
from app.crawler.signals import scraping_done
from app import crawler
from .models import SearchQueries, SearchResults, CrawlLogs, SearchJobs
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm.exc import NoResultFound

from rq import Queue
from rq.job import Job

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)



@search.route('/', methods=['GET'])
def search_index():
    return render_template('index.html', title='Search from Your Favorite Search Engines')


@scraping_done.connect
def when_crawler_returned_results(sender, **extra):
    response = extra.get('response', None)
    search_engine = extra.get('search_engine')

    app.logger.info('Signal being received {}'.format(search_engine))

    if response is None:
        app.logger.error('Return no response')
        raise Exception('No results found')

    crawl_log = CrawlLogs()
    crawl_log.query_id = response['query_id']
    crawl_log.http_status_code = response['http_status_code']
    crawl_log.search_engine = search_engine
    crawl_log.html = response['html']
    crawl_log.time_taken = response['time_taken']

    db.session.add(crawl_log)
    db.session.commit()

    search_engine_field = '{}_completed'.format(search_engine)

    SearchQueries.query.filter_by(id=response['query_id']).update({search_engine_field: 1})
    db.session.flush()
    db.session.commit()

    for result in response['results']:
        app.logger.info('Parsing scraping results')
        try:
            search_result = SearchResults()
            search_result.search_engine = search_engine
            search_result.query_id = response['query_id']
            search_result.title = result['title']
            search_result.description = result['description']
            search_result.link = result['link']

            db.session.add(search_result)
            db.session.commit()
        except Exception as e:
            app.logger.error(e)


def _initialize_scrape(keyword, query_id):
    q = Queue(connection=conn)

    for cls in ('GoogleCrawler', 'WikipediaCrawler', 'DuckduckGoCrawler'):
        try:
            # Loop through Class Crawler
            class_ = getattr(crawler, cls)
            instance = class_()

            # Forking each Crawler as background job
            job = q.enqueue_call(
                func=instance.scrape, args=(keyword, query_id), result_ttl=5000
            )

            # Saved job to DB
            search_job = SearchJobs()
            search_job.job_id = job.get_id()
            search_job.query_id = query_id
            search_job.search_engine = class_

            db.session.add(search_job)
            db.session.commit()
            app.logger.info('Search job saved')
        except SQLAlchemyError as e:
            app.logger.error(e)
            db.session.rollback()
        except Exception as e:
            app.logger.error(e)


@search.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    try:
        job = Job.fetch(job_key, connection=conn)

        if job.is_finished:
            return str(job.result), 200
        else:
            return "Not finished", 202
    except Exception as e:
        app.logger.error(e)
        return "Error occured", 500


@search.route('/search/results', methods=['GET'])
def search_result():
    query = request.args.get('q', None)
    new_search = False

    if not query:
        search_query = None
    else:
        try:
            search_query = SearchQueries.query.filter_by(keyword=query).one()
        except NoResultFound as e:
            keyword = query

            new_query = SearchQueries(keyword=query)

            db.session.add(new_query)
            db.session.commit()

            new_search = True
            _initialize_scrape(keyword, new_query.id)

            search_query = new_query
        except (SQLAlchemyError, OperationalError) as e:
            # Rollback DB if anything wrong in database
            app.logger.error(e)
            db.session.rollback()
        except Exception as e:
            app.logger.error(e)
            search_query = None

    top_10_results = SearchQueries.query.order_by(SearchQueries.id.desc()).all()[:10]

    return render_template('search_result.html',
                           new_search=new_search,
                           search_query=search_query,
                           top_10_results=top_10_results,
                           title='Search Result for "{}"'.format(query))


@search.route('/search/detail/<int:query_id>', methods=['GET'])
def search_detail(query_id):
    search_query = SearchQueries.query.filter_by(id=query_id).first()

    google_search_results = SearchResults.query.filter_by(query_id=query_id, search_engine='google').all()
    duckduckgo_search_results = SearchResults.query.filter_by(query_id=query_id, search_engine='duck2go').all()
    wikipedia_search_results = SearchResults.query.filter_by(query_id=query_id, search_engine='wikipedia').all()

    return render_template('search_detail.html',
                           search_query=search_query,
                           google_search_results=google_search_results,
                           duckduckgo_search_results=duckduckgo_search_results,
                           wikipedia_search_results=wikipedia_search_results,
                           title='Search Result for "{}"'.format(search_query.keyword))


@search.route('/debug', methods=['GET'])
def debug():
    crawl_logs = CrawlLogs.query.all()

    return render_template('debug.html',
                           crawl_logs=crawl_logs,
                           title='Debug')


@search.route('/debug/html/<log_id>', methods=['GET'])
def debug_html(log_id):
    crawl_log = CrawlLogs.query.get(log_id)

    return render_template('debug_html.html',
                           title='Debug',
                           log=crawl_log)


@search.route('/json/results', methods=['GET'])
def search_results_json():
    try:
        top_10_results = SearchQueries.query.order_by(SearchQueries.id.desc()).all()[:10]

        result_container = []

        for result in top_10_results:
            result_container.append({
                'query_id': result.id,
                'keyword': result.keyword,
                'google_completed': result.google_completed,
                'duck2go_completed': result.duck2go_completed,
                'wikipedia_completed': result.wikipedia_completed,
                'is_completed': result.google_completed == 1 and result.duck2go_completed == 1 and result.wikipedia_completed == 1
            })
    except Exception as e:
        app.logger.error(e)

        result_container = {
            'status': 'error',
            'message': e
        }


    return jsonify(result_container)
