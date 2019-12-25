from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session, SqlAlchemySessionInterface
from celery import Celery
from celery.signals import after_setup_task_logger
from celery.app.log import TaskFormatter
from config import app_config

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect()
sess = Session()

app.config.from_object(app_config['development'])


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(TaskFormatter('%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s'))

@app.errorhandler(404)
def page_not_found(e):
    # 404 page
    return render_template('404.html', title='Page is not found'), 404


def make_celery():
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery


celery_client = make_celery()

def create_app(config_name):
    """Heart of Flask runner. Basically just initialization of application."""

    app.config.from_object(app_config[config_name])

    db.init_app(app)
    csrf.init_app(app)

    # initialize session
    app.config['SESSION_SQLALCHEMY'] = db
    sess.init_app(app)

    # importing search pages blueprint
    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint)

    return app
