class Environment(object):
    """A configuration environment.
  Provides environment-specific configuration variables:
    db_uri: uri to connect to the database.
    db_hostname: database hostname.
    db_name: name of the database.
    db_user: database user.
    db_password: database password.
    debug: bool for whether or not debug mode should be enabled.
    testing: bool for whether or not testing mode should be enabled.
    secret_key: secret key for session cookie.
    imgur_api: a map {"id": <imgur_id>, "secret": <imgur_secret>}
  """

    def __init__(self, db_hostname, db_name, db_user, db_password, debug,
                 testing, secret_key, imgur_api):
        self.db_hostname = db_hostname
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.debug = debug
        self.secret_key = secret_key
        self.imgur_api = imgur_api

    @property
    def db_uri(self):
        return "mysql+pymysql://{0}:{1}@{2}/{3}".format(
            self.db_user, self.db_password, self.db_hostname, self.db_name)
