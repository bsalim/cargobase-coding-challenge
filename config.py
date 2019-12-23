import os
from dotenv import load_dotenv
load_dotenv()

ENV = os.getenv('ENV')


class Config(object):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://{0}:{1}@{2}/{3}'.format(
                                  os.getenv('DB_USER'),
                                  os.getenv('DB_PASS'),
                                  os.getenv('DB_HOST'),
                                  os.getenv('DB_NAME')
                               )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    EMAIL_FROM = os.getenv('MAIL_FROM')
    BASE_URL = os.getenv('BASE_URL')
    LIVE_URL = os.getenv('LIVE_URL')
    ROOT_PATH = os.getenv('ROOT_PATH')

    SESSION_TYPE = 'sqlalchemy'
    SESSION_USE_SIGNER = True
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_PERMANENT = True


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
