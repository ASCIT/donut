# Note: this file is only used for testing locally. The production environment
# uses wsgi to start up, and bypasses this file. So we are free to have debug
# settings enabled.
from Donut import app, config
import argparse

parser = argparse.ArgumentParser(description='Set up development server.')
parser.add_argument('port_num', metavar='port_num', type=int, 
                    help='Port on which to run server.')

args = parser.parse_args()


if __name__ == "__main__":
    port = getattr(config, 'PORT', args.port_num)
    debug = getattr(config, 'DEBUG', True)
    app.run(debug=debug, port=port)

