from app import db, app
from datetime import datetime

class Movies(db.Model):
    __tablename__ = 'movies'


class SearchQueries(db.Model):
    __tablename__ = 'search_queries'

    id = db.Column(db.Integer, primary_key=True)

    keyword = db.Column(db.String(255), nullable=True)
    result_found = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)


class SearchResults(db.Model):
    __tablename__ = 'search_results'

    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, index=True)
    search_engine = db.Column(db.String(50), index=True, nullable=True)
    title = db.Column(db.String(50), index=True, nullable=True)
    description = db.Column(db.Text, index=True, nullable=True)
    link = db.Column(db.Text, index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)


class CrawlLogs(db.Model):
    __tablename__ = 'crawl_logs'

    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, index=True)
    search_engine = db.Column(db.String(50), index=True, nullable=True)
    title = db.Column(db.String(50), index=True, nullable=True)
    description = db.Column(db.Text, index=True, nullable=True)
    link = db.Column(db.Text, index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)
