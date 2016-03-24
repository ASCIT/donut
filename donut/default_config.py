"""Default website configurations, used only for testing.
"""

from donut import environment

# Public Test Database
TEST = environment.Environment(
    db_hostname="localhost",
    db_name="donut_test",
    db_user="donut_test",
    db_password="public",
    debug=True,
    secret_key="1234567890")
