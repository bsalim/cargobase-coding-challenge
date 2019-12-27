from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session, SqlAlchemySessionInterface
from config import app_config
from logging.config import dictConfig
import rq_dashboard

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect()
sess = Session()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

@app.errorhandler(404)
def page_not_found(e):
    # 404 page
    return render_template('404.html', title='Page is not found'), 404


def create_app(config_name):
    """Heart of Flask runner. Basically just initialization of application."""
    app.config.from_object(app_config[config_name])

    db.init_app(app)
    csrf.init_app(app)

    # initialize session
    app.config['SESSION_SQLALCHEMY'] = db
    sess.init_app(app)

    app.config.from_object(rq_dashboard.default_settings)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    # importing search pages blueprint
    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint)

    return app
