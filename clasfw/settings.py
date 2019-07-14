"""Application configuration."""
import os


class Config:
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    SECRET_KEY = '\x9d\x8a\xcf\xa0\xbb\xd9\xe6\xc1"\x00\xc1\x84\x9e\xfa\xa8&6k\xfcR\x80<\xc31'
    
    DEBUG = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Workaround for bug
    # https://github.com/pallets/flask/issues/1907
    TEMPLATES_AUTO_RELOAD = True
    
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED=True
     
    RECAPTCHA_PUBLIC_KEY  = '6LcZA2cUAAAAAGgvNfUDkVZ9DtAI9d_x1xKk31Fq'
    RECAPTCHA_PRIVATE_KEY = '6LcZA2cUAAAAAIFqH2tGhcjOfhdBGjMwmiVjhLGw'
    
    
    # SERVER_NAME = 'clas.sinp.msu.ru'
    MAIL_SERVER = 'depni-mx.sinp.msu.ru'
    # MAIL_DEFAULT_SENDER = ('CLAS DB Support Team', 'clasdb@depni.sinp.msu.ru')
    MAIL_DEFAULT_SENDER = 'clasdb@depni.sinp.msu.ru'
    ADMINS = ['chesn@depni.sinp.msu.ru']
    
    # STYLUS_BIN = '/usr/local/bin/stylus'
    
    
    USER_APP_NAME                   = "CLAS Analysis Framework"    # Used by email templates
    USER_ENABLE_EMAIL               = True
    USER_ENABLE_USERNAME            = True
    USER_ENABLE_CHANGE_USERNAME     = False
    
    USER_ENABLE_INVITATION          = True
    USER_REQUIRE_INVITATION         = True
    USER_ENABLE_INVITE_USER         = True
    
    USER_LOGIN_URL                  = '/user/login'
    USER_LOGOUT_URL                 = '/user/logout'
    
    USER_AFTER_LOGIN_ENDPOINT = 'index'
    # USER_AFTER_LOGIN_ENDPOINT = 'user.profile'
    # USER_AFTER_LOGOUT_ENDPOINT = 'index'


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False

    DB_NAME = 'clasfw_production.sqlite3'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)

    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

    DB_NAME = 'clasfw_development.sqlite3'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)

    # SQLALCHEMY_ECHO = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
