from app import db, app
from datetime import datetime

class SearchQueries(db.Model):
    __tablename__ = 'search_queries'

    id = db.Column(db.BigInteger, primary_key=True)
    # job_id = db.Column(db.String(100), index=True)
    keyword = db.Column(db.String(255), nullable=True)
    result_found = db.Column(db.Integer, default=0)
    google_completed = db.Column(db.Integer, default=0)
    duck2go_completed = db.Column(db.Integer, default=0)
    wikipedia_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)


class SearchResults(db.Model):
    __tablename__ = 'search_results'

    id = db.Column(db.BigInteger, primary_key=True)
    query_id = db.Column(db.BigInteger, index=True)
    search_engine = db.Column(db.String(50), index=True, nullable=True)
    title = db.Column(db.String(50), index=True, nullable=True)
    description = db.Column(db.Text, index=True, nullable=True)
    link = db.Column(db.Text, index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)


class SearchJobs(db.Model):
    __tablename__ = 'search_jobs'

    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.BigInteger, index=True)
    job_id = db.Column(db.String(50), index=True, nullable=True)
    search_engine = db.Column(db.String(50), nullable=True)
    is_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=None)


class CrawlLogs(db.Model):
    __tablename__ = 'crawl_logs'

    id = db.Column(db.BigInteger, primary_key=True)
    query_id = db.Column(db.BigInteger, index=True)
    search_engine = db.Column(db.String(50), index=True, nullable=True)
    http_status_code = db.Column(db.String(5), nullable=True)
    time_taken = db.Column(db.Float(10,5), default=0)
    html = db.Column(db.Text, default=None)
    created_at = db.Column(db.DateTime, default=datetime.now())
