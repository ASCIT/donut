import pytest

from Donut import app

@pytest.fixture
def client():
  # Need to specify a server, since test_client doesn't do that for us.
  app.config['SERVER_NAME'] = "127.0.0.1"

  # Establish an application context before running the tests.
  ctx = app.app_context()
  ctx.push()

  return app.test_client()
