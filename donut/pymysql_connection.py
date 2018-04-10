import pymysql
try:
    from donut import config
except ImportError:
    from donut import default_config as config


def make_db(environment_name):
    if environment_name == "prod" and hasattr(config, "PROD"):
        environment = config.PROD
    elif environment_name == "dev" and hasattr(config, "DEV"):
        environment = config.DEV
    elif environment_name == "test" and hasattr(config, "TEST"):
        environment = config.TEST
    else:
        raise ValueError("Illegal environment name.")
    return pymysql.connect(
        host='localhost',
        database=environment.db_name,
        user=environment.db_user,
        password=environment.db_password,
        db='db',
        autocommit=True,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
