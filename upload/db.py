"""
This module contains the DB class for connecting to production,
development, or test databases.
"""
import sqlalchemy
try:
  from donut import config
except ImportError:
  from donut import default_config as config

# Database class
class DB():
  def __init__(self, environment_name):
    """ self.db is the database connection. """
    if environment_name == "prod" and hasattr(config, "PROD"):
      environment = config.PROD
    elif environment_name == "dev" and hasattr(config, "DEV"):
      environment = config.DEV
    elif environment_name == "test" and hasattr(config, "TEST"):
      environment = config.TEST
    else: 
      raise ValueError("Illegal environment name.")

    self.engine = sqlalchemy.create_engine(environment.db_uri, 
                    convert_unicode=True)
    self.db = self.engine.connect()

  def __del__(self):
    self.db.close()
