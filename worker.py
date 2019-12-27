import os
import redis
from rq import Worker, Queue, Connection
from app import create_app

env = os.getenv('ENV', 'production')
app = create_app(env)
listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

with app.app_context():
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
