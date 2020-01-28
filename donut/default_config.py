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
    testing=True,
    secret_key="1234567890",
    imgur_api={
        "id": "b579f690cacf867",
        "secret": "****************************************"
    },
    restricted_ips=r"127\.0\.0\.1")
