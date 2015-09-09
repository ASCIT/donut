# Note: this file is only used for testing locally. The production environment
# uses wsgi to start up, and bypasses this file. So we are free to have debug
# settings enabled.
from Donut import app, config

port = getattr(config, 'PORT', 5050)
app.run(debug=True, port=port)
