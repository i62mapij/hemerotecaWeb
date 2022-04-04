class BaseConfig(object):
    'Base configuracion'
    USER_APP_NAME = 'Hemeroteca'
    SECRET_KEY = '9ff384hr8f3hyhhrfey77472874h449iu87ygbe3h'
    DEBUG = True
    TESTING = False
    USER_ENABLE_EMAIL=False
    MONGODB_DB = 'hemeroteca'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_USERNAME = 'Guru99'
    MONGODB_PASSWORD = 'password'
class ProductionConfig(BaseConfig):
    'Produccion configuracion'
    'Base configuracion'
    USER_APP_NAME = 'Hemeroteca'
    SECRET_KEY = '9ff384hr8f3hyhhrfey77472874h449iu87ygbe3h'
    TESTING = False
    USER_ENABLE_EMAIL=False
    MONGODB_DB = 'hemeroteca'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_USERNAME = 'Guru99'
    MONGODB_PASSWORD = 'password'
    DEBUG = False
class DevelopmentConfig(BaseConfig):
    'Desarrollo configuracion'
    DEBUG = True
    TESTING = True
    SECRET_KEY = '9ff384hr8f3hyhhrfey77472874h449iu87ygbe3h'
    MAIL_SUPPRESS_SEND = False
    MAIL_PORT = 2525
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    CACHE_TYPE = "simple"
    BABEL_DEFAULT_LOCALE = "es"