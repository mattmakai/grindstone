import os
from datetime import timedelta
from os import environ

basedir = os.path.abspath(os.path.dirname(__file__))

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        var_set = environ[setting]
        if var_set == 'true' or var_set == 'True':
            return True
        elif var_set == 'false' or var_set == 'False':
            return False
        return var_set
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise Exception(error_msg)


# General Flask app settings
DEBUG = get_env_setting('DEBUG')
SECRET_KEY = get_env_setting('SECRET_KEY')

# Relational database settings
SQLALCHEMY_DATABASE_URI = get_env_setting('DATABASE_URL')

# Redis
REDIS_SERVER = get_env_setting('REDIS_SERVER')
REDIS_PORT = get_env_setting('REDIS_PORT')
REDIS_DB = get_env_setting('REDIS_DB')

# Twilio API credentials
TWILIO_ACCOUNT_SID = get_env_setting('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = get_env_setting('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = get_env_setting('TWILIO_NUMBER')

# Celery
CELERY_BROKER_URL = get_env_setting('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = get_env_setting('CELERY_RESULT_BACKEND')
CELERY_IMPORTS=("grindstone.tasks",)
CELERYBEAT_SCHEDULE = {
    'poll-every-hour': {
        'task': 'grindstone.tasks.github_follower_count',
        'schedule': timedelta(minutes=120),
        'args': (get_env_setting('GITHUB_USERNAME'), )
    }
}

# Google API credentials
GOOGLE_CLIENT_SID = get_env_setting('GOOGLE_CLIENT_SID')
GOOGLE_CLIENT_SECRET = get_env_setting('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URL = get_env_setting('GOOGLE_REDIRECT_URL')
