from os import environ, path
import os



class Config:
    # General Flask Config
    SECRET_KEY = b'ergergergergegg/'
    USE_PROXYFIX = True

    APPLICATION_ROOT = '/'

    FLASK_APP = 'server.py'
    FLASK_RUN_HOST = '0.0.0.0'
    FLASK_RUN_PORT = 80

    #FLASK_DEBUG = 1
    #FLASK_ENV = "development" #production
    #DEBUG = True

    # no double mqtt message config

    FLASK_DEBUG = 0
    FLASK_ENV = "development" #production
    #FLASK_ENV = "production"  # production

    DEBUG = False # SET THIS TO FALSE
    TESTING = False #True

    SESSION_TYPE = 'sqlalchemy' #'redis'
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_COOKIE_NAME = 'my_cookieGetFace'
    SESSION_PERMANENT = True

    # Database

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite"  # = 'mysql://username:password@localhost/db_name'

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = "simple"  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT =  100
   
   # Mqtt
    
    MQTT_BROKER_URL = 'localhost'  # use the free broker from HIVEMQ
    MQTT_BROKER_PORT = 1883  # default port for non-tls connection
    #MQTT_USERNAME = ''  # set the username here if you need authentication for the broker
    #MQTT_PASSWORD = ''  # set the password here if the broker demands authentication
    #MQTT_KEEPALIVE = 5  # set the time interval for sending a ping to the broker to 5 seconds
    MQTT_TLS_ENABLED = False  # set TLS to disabled for testing purposes
    