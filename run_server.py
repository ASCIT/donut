# Note: this file is only used for testing locally. The production environment
# uses wsgi to start up, and bypasses this file. So we are free to have debug
# settings enabled.
import argparse

import donut
from donut import app

parser = argparse.ArgumentParser(description="Run development server.")
parser.add_argument("-e", "--env", default="dev")
parser.add_argument(
    "-p",
    "--port",
    metavar="port",
    type=int,
    default=5000,
    help="Port on which to run server.")

if __name__ == "__main__":
    args = parser.parse_args()
    donut.init(args.env)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=args.port)
